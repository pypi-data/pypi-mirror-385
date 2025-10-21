#!/usr/bin/env python3
#
# Copyright 2025 Sikt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import argparse
import logging
import signal
import sys
from datetime import datetime, timedelta, timezone
from operator import itemgetter
from typing import Optional

import requests
import zinolib as ritz
from pyargus.client import Client
from pyargus.models import Event, Incident
from simple_rest_client.exceptions import ClientConnectionError
from zinolib.ritz import NotifierResponse

from zinoargus.config import (
    InvalidConfigurationError,
    read_configuration,
)
from zinoargus.config.models import (
    ArgusConfiguration,
    Configuration,
    ZinoConfiguration,
)

# A map of Zino case numbers to Zino case objects
CaseMap = dict[int, ritz.Case]
# A map of Zino case numbers to Argus incident objects
IncidentMap = dict[int, Incident]

_logger = logging.getLogger("zinoargus")

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
HISTORY_EVENT_TYPE = "OTH"  # Other
INCIDENT_ATTRIBUTE_CHANGE_TYPE = "CHI"
POLL_TIMEOUT = 30  # seconds
INCIDENT_REFRESH_INTERVAL = timedelta(seconds=POLL_TIMEOUT)
MY_TZINFO = datetime.now().astimezone().tzinfo

_config: Optional[Configuration] = None
_zino: Optional[ritz.ritz] = None
_notifier: Optional[ritz.notifier] = None
_argus: Optional[Client] = None
_circuit_metadata = dict()
_last_incident_refresh = datetime.now()


def main():
    global _zino
    global _notifier
    global _argus
    global _config

    args = parse_arguments()

    # Read configuration
    try:
        _config = read_configuration(args.config_file)
    except OSError:
        _logger.error("No configuration file found: %s", args.config_file)
        sys.exit(1)
    except InvalidConfigurationError as error:
        _logger.error("Invalid configuration in file %s: %s", args.config_file, error)
        sys.exit(1)

    # Initiate Logging
    setup_logging(verbosity=args.verbose or 0)

    # Catch SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    _argus = get_argus_client(_config.argus)

    """Initiate connectionloop to Zino"""
    try:
        _zino, _notifier = connect_to_zino(_config.zino)
        start()

        # TODO: If the Zino connection errors out, this should try to reconnect rather than die
    except ritz.AuthenticationError:
        _logger.critical("Unable to authenticate against Zino, retrying in 30sec")
    except ritz.NotConnectedError:
        _logger.critical("Lost connection with Zino, retrying in 30sec")
    except ConnectionRefusedError:
        _logger.critical(
            "Connection refused by Zino (%s:%s)", _config.zino.server, _config.zino.port
        )
    except ClientConnectionError:
        _logger.critical("Connection refused by Argus (%s)", _config.argus.url)
    except KeyboardInterrupt:
        _logger.critical("CTRL+C detected, exiting application")
    except SystemExit:
        _logger.critical("Received sigterm, exiting")
    except Exception:  # pylint: disable=broad-except
        # Break on an unhandled exception
        _logger.critical("Unhandled exception from main event loop", exc_info=True)
    finally:
        try:
            _zino.close()
        except Exception:  # noqa
            pass

        _zino = None
        _notifier = None


def connect_to_zino(
    configuration: ZinoConfiguration,
) -> tuple[ritz.ritz, ritz.notifier]:
    """Connects to Zino and returns the ritz instance and notifier instance"""
    zino = ritz.ritz(
        server=str(configuration.server),
        port=configuration.port,
        username=configuration.user,
        password=configuration.secret,
    )
    zino.connect()
    notifier = zino.init_notifier()
    return zino, notifier


def get_argus_client(configuration: ArgusConfiguration) -> Client:
    """Returns a new Argus client instance"""
    return Client(
        api_root_url=str(configuration.url),
        token=configuration.token,
        timeout=configuration.timeout,
    )


def start():
    """This is the main "event loop" of the Zino-Argus glue service, called when there
    are successful connections to the Zino and Argus API, and torn down when the
    connections or API's fail.
    """
    _logger.info("starting")
    collect_circuit_metadata()

    argus_incidents, zino_cases = synchronize_all_cases()
    synchronize_continuously(argus_incidents, zino_cases)


def synchronize_all_cases() -> tuple[IncidentMap, CaseMap]:
    """Fully synchronize cases/incidents between Zino and Argus, returning maps of all
    known Argus incidents and all Zino cases.
    """
    argus_incidents = get_all_my_argus_incidents()
    zino_cases = get_all_interesting_zino_cases()

    close_argus_incidents_missing_from_zino(argus_incidents, zino_cases)
    create_argus_incidents_from_new_zino_cases(argus_incidents, zino_cases)

    return argus_incidents, zino_cases


def get_all_my_argus_incidents() -> IncidentMap:
    """Get a map of all Argus incidents that belong to the source system represented by
    this glue service instance.
    """
    argus_incidents: IncidentMap = {}
    for incident in _argus.get_my_incidents(open=True):
        if not incident.source_incident_id:
            _logger.error(
                "Ignoring incident %s with no 'source_incident_id' set (%r)",
                incident.pk,
                incident.description,
            )
            continue
        if not incident.source_incident_id.isnumeric():
            _logger.error(
                "Ignoring incident %s (%r), source_incident_id is not a numeric value (%r)",
                incident.pk,
                incident.description,
                incident.source_incident_id,
            )
            continue
        _logger.debug(
            "Argus incident %s (Zino case #%s) added to to internal data structures (%r)",
            incident.pk,
            incident.source_incident_id,
            incident.description,
        )

        argus_incidents[int(incident.source_incident_id)] = incident
    return argus_incidents


def get_all_interesting_zino_cases() -> CaseMap:
    """Returns a map of all Zino cases that are deeming interesting enough to
    synchronize to Argus.
    """
    zino_cases: CaseMap = {}
    case: ritz.Case
    for case in _zino.cases_iter():
        if not is_case_interesting(case):
            continue

        _logger.debug(
            "Zino case #%s of type %s (%s) added to internal data structure",
            case.id,
            case.type,
            case.get("router"),
        )
        zino_cases[case.id] = case

    return zino_cases


def create_argus_incidents_from_new_zino_cases(
    argus_incidents: IncidentMap, zino_cases: CaseMap
):
    for case_id in set(zino_cases) - set(argus_incidents):
        incident = get_or_make_argus_incident_for_zino_case(
            case_id, zino_cases[case_id], argus_incidents
        )
        if incident.stateful and not incident.open:
            # Argus incident was closed while zino-argus-glue was down, closing Zino
            # case
            update_case_closed(incident, zino_cases[case_id])


def close_argus_incidents_missing_from_zino(
    argus_incidents: IncidentMap, zino_cases: CaseMap
):
    for case_id in set(argus_incidents) - set(zino_cases):
        _logger.info(
            "Zino case %s is not cached from Zino, and ready to be closed in Argus",
            case_id,
        )
        close_argus_incident(
            argus_incidents[case_id],
            description="This case did not exist in Zino when glue service was started",
        )


def synchronize_continuously(argus_incidents: IncidentMap, zino_cases: CaseMap):
    """Continuously "poll" the Zino notification channel and update Argus accordingly"""
    global _last_incident_refresh
    while True:
        if datetime.now() > (_last_incident_refresh + INCIDENT_REFRESH_INTERVAL):
            # Refreshes Argus incidents at least every INCIDENT_REFRESH_INTERVAL
            refresh_argus_incidents(argus_incidents, zino_cases)
            _last_incident_refresh = datetime.now()

        update = _notifier.poll(timeout=POLL_TIMEOUT)
        if not update:
            continue
        _logger.debug(
            "Update on Zino case id:%s type:%s info:%s",
            update.id,
            update.type,
            update.info,
        )

        if update.type == "scavenged":
            # This Zino case can no longer be fetched from Zino, so we need to forget it
            zino_cases.pop(update.id, None)
            argus_incidents.pop(update.id, None)
            continue

        # Ensure we have the details on both the Zino Case and Argus Incident being updated
        if update.id not in zino_cases:
            # We didn't know about this case ID before, so we need to fetch it
            zino_cases[update.id] = _zino.case(update.id)
        case = zino_cases[update.id]

        if not is_case_interesting(case):
            # Ignore this update, as it's not interesting to us
            continue

        incident = get_or_make_argus_incident_for_zino_case(
            update.id, case, argus_incidents
        )

        if update.type == "state":
            update_state(update, case, incident, zino_cases, argus_incidents)

        if update.type == "history":
            synchronize_case_history(case, incident)


def refresh_argus_incidents(argus_incidents: IncidentMap, zino_cases: CaseMap):
    """Refreshes all the Argus incidents that we know of and care about.

    This also triggers actions that modify Zino cases if indicated by changes to the
    Argus incidents.
    """
    do_update_on_ack = _config.sync.acknowledge.setstate != "none"
    _logger.info("Refreshing %s Argus incidents", len(argus_incidents))
    for case_id, old_incident in argus_incidents.items():
        new_incident = _argus.get_incident(old_incident.pk)
        argus_incidents[case_id] = new_incident

        if do_update_on_ack and new_incident.acked and not old_incident.acked:
            update_case_acknowledged(
                incident=new_incident,
                case=zino_cases[case_id],
                desired_state=_config.sync.acknowledge.setstate,
            )

        if _config.sync.ticket.enable:
            update_case_ticket(incident=new_incident, case_id=case_id)

        if not new_incident.open and old_incident.open:
            update_case_closed(incident=new_incident, case=zino_cases[case_id])


def update_case_acknowledged(incident: Incident, case: ritz.Case, desired_state: str):
    """Updates a Zino case with the acknowledged status from Argus, if necessary."""
    case_id = getattr(case, "_caseid")
    msg = "Argus incident %s (Zino case %s) was acknowledged"
    if case.state == desired_state:
        return

    _logger.info(msg + ", setting Zino case to %r", incident.pk, case_id, desired_state)

    acks = _argus.get_incident_acknowledgements(incident)
    acks.sort(key=lambda ack: ack.event.timestamp, reverse=True)
    _logger.debug("Argus incident %s acks: %r", incident.pk, acks)

    last_ack = acks[0]

    description = f"{last_ack.event.description} ({last_ack.event.actor})"
    _zino.add_history(case_id, description)
    _zino.set_state(case_id, desired_state)


def update_case_ticket(incident: Incident, case_id: int):
    """Updates a Zino case history with a new ticket URL from Argus, if it isn't there
    already.
    """
    if not incident.ticket_url:
        return
    if is_string_in_case_history(case_id, incident.ticket_url):
        return
    user = find_who_added_incident_ticket(incident, incident.ticket_url)
    _logger.info(
        "New ticket URL %s found on Argus incident %s, adding to Zino case %s",
        incident.ticket_url,
        incident.pk,
        case_id,
    )
    message = f"Ticket {incident.ticket_url} added by Argus user {user}"
    _zino.add_history(case_id, message)


def is_string_in_case_history(case_id: int, string: str) -> bool:
    """Returns True if a substring is present in the case history"""
    history = _zino.get_history(case_id)
    return any(any(string in line for line in entry["log"]) for entry in history)


def find_who_added_incident_ticket(incident: Incident, ticket_url: str) -> str:
    """Traverses the incident events to find the user who added the ticket URL."""
    # This works under the assumption that events are returned in descending order by
    # timestamp (they seem to be by Argus 2.0, at least), so the first event we
    # find that contains the ticket URL should be the event that represents the change
    # to the current value.
    for event in _argus.get_incident_events(incident):
        if (
            event.type == INCIDENT_ATTRIBUTE_CHANGE_TYPE
            and ticket_url in event.description
        ):
            return event.actor
    return "(unknown user)"


def update_case_closed(incident: Incident, case: ritz.Case):
    """Closes a Zino case if the Argus incident is closed."""
    case_id = getattr(case, "_caseid")
    if incident.open:
        return

    _logger.info(
        "Closing Zino case %s, because Argus incident %s was closed",
        case_id,
        incident.pk,
    )

    events = _argus.get_incident_events(incident)
    events.sort(key=lambda event: event.timestamp, reverse=True)
    _logger.debug("Argus incident %s events: %r", incident.pk, events)

    for event in events:
        if event.type == "CLO":
            closing_event = event
            break

    description = f"{closing_event.description} ({closing_event.actor})"
    _zino.add_history(case_id, description)
    _zino.set_state(case_id, "closed")


def synchronize_case_history(case: ritz.Case, incident: Incident):
    """Synchronizes case history to an Argus incident.

    This is slightly tricky, since there is no explicit mapping between Zino case
    history entries and Argus incident events, so there is some guesswork involved -
    mainly by comparing timestamps.

    If two history entries somehow have the same timestamp, the current algorithm
    cannot handle it and which of the two history entries are transmitted to Argus is
    undefined.

    A specific case of this applies to the initial history entry for all Zino cases:
    Its timestamp is always the same as the case's "opened" timestamp, but contains
    nothing interesting other than a "state change from embryonic to opened", so it
    conveys no more information than the initial "incident start" event and is easily
    omitted (this algorithm will see the STA and OTH events as duplicates).

    Another case is the history entry that is added when we close a Zino case when the
    Argus incident is closed. Since we already have it recorded as an Argus event, we
    do not need to sync that back. We can identify these by comparing the author of the
    log entry with the user we have saved as our Zino username.
    """
    history = _zino.get_history(case.id)
    existing_events = _argus.get_incident_events(incident)
    # Filter out events that seem to originate from this glue service actor:
    my_actor = next(event.actor for event in existing_events if event.type == "STA")
    my_events_by_timestamp = {
        event.timestamp: event for event in existing_events if event.actor == my_actor
    }

    new_events = []
    for entry in history:
        event = make_event_from_history_entry(entry)
        if (
            event.timestamp in my_events_by_timestamp
            or entry["user"] == _config.zino.user
        ):
            # Event likely already exists in Argus
            continue
        new_events.append(event)
    _logger.debug(
        "Adding %s new history events to incident %s", len(new_events), incident.pk
    )
    for event in new_events:
        _argus.post_incident_event(incident, event)


def make_event_from_history_entry(entry: dict) -> Event:
    """Makes an Argus Incident Event data object from a Zino history entry"""
    description = entry.get("header")
    if entry.get("log"):
        description += "\n" + "\n".join(entry.get("log"))
    # datetime objects from ritz/zinolib are converted from Zino's UTC to the local
    # timezone, but the objects are timezone-naive.  We need to assign proper tzinfo
    # to the timestamp before sending to Argus:
    timestamp = entry.get("date").replace(tzinfo=MY_TZINFO)
    return Event(
        timestamp=timestamp,
        description=description,
        type=HISTORY_EVENT_TYPE,
    )


def get_or_make_argus_incident_for_zino_case(
    case_id: int, case: ritz.Case, argus_incidents: IncidentMap
) -> Incident:
    """Tries to get the Argus incident for a Zino case (even closed ones), creating
    a new one if it doesn't exist.
    """
    if case_id in argus_incidents:
        return argus_incidents[case_id]

    incidents = _argus.get_my_incidents(source_incident_id=case_id)
    incident = next(incidents, None)
    if incident:
        argus_incidents[case_id] = incident
        return incident

    new_incident = create_argus_incident(case)
    argus_incidents[case_id] = new_incident
    return new_incident


def update_state(
    update: NotifierResponse,
    case: ritz.Case,
    incident: Incident,
    zino_cases: CaseMap,
    argus_incidents: IncidentMap,
):
    """Handles a state update notification from Zino"""
    old_state, new_state = update.info.split(" ", 1)
    if new_state == "closed":
        # Closing case
        _logger.debug(
            "Zino case %s is closed and is being removed from Argus", update.id
        )
        if incident.open:
            close_argus_incident(incident, case)
            # keep track of closed incidents in case of further updates
            argus_incidents[update.id] = incident
        zino_cases.pop(update.id, None)
    else:
        # Any other state changes should just be updated internally
        zino_cases[update.id] = case


def collect_circuit_metadata():
    global _circuit_metadata
    global _config

    metadata_url = _config.metadata.ports_url
    if not metadata_url:
        return

    r = requests.get(url=metadata_url)

    r2 = r.json()
    _logger.info("Collected metadata for %s routers", len(r2["data"]))
    _logger.info(r2["data"].keys())
    _circuit_metadata = r2["data"]


def is_down_log(log):
    """Returns true if any of the log entries"""
    return any(string in log for string in ("linkDown", "lowerLayerDown", "up to down"))


def is_production_interface(case: ritz.Case):
    # All interfaces in production should follow the correct description syntax
    if "descr" in case.keys():
        return "," in case.descr
    return False


def is_case_interesting(case: ritz.Case):
    # TODO: Add metadata from telemator and check importance against circuit type

    if case.type in [ritz.caseType.BFD]:
        _logger.info("Zino case %s of type %s is ignored", case.id, case.type)
        return False

    if case.type in [ritz.caseType.PORTSTATE]:
        logs = (_l["header"] for _l in case.log)
        if not any(is_down_log(_l) for _l in logs):
            return False
        if not is_production_interface(case):
            return False

    return True


def describe_zino_case(zino_case: ritz.Case):
    if zino_case.type == ritz.caseType.REACHABILITY:
        return f"{zino_case.router} is not reachable"
    elif zino_case.type == ritz.caseType.BGP:
        # TODO: Lookup remote_addr name in reverse-DNS
        return f"{zino_case.router} BGP Neighbor AS{zino_case.remote_as}/{zino_case.remote_addr} is DOWN"
    elif zino_case.type == ritz.caseType.BFD:
        # BFD should be ignored
        pass
    elif zino_case.type == ritz.caseType.PORTSTATE:
        return f"{zino_case.router} port {zino_case.port} changed state to DOWN ({zino_case.get('descr', '')})"
    elif zino_case.type == ritz.caseType.ALARM:
        return f"{zino_case.router} Active alarms reported"
    return None


def generate_tags(zino_case):
    yield "host", zino_case.router
    if zino_case.type == ritz.caseType.PORTSTATE:
        yield "interface", zino_case.port
        descr = zino_case.get("descr")
        if descr:
            yield "description", descr
            # GET UN


def close_argus_incident(
    incident: Incident,
    case: Optional[ritz.Case] = None,
    description: Optional[str] = None,
) -> None:
    """Closes an Argus incident.

    The ending timestamp is taken from the last Zino case history entry,
    if available, otherwise the current time is used.  If the description is empty,
    the end event description will also be taken from the last history entry.
    """
    _logger.info("Closing Argus incident %s", incident.pk)
    timestamp = datetime.now(tz=timezone.utc)
    if case:
        if last_history := get_last_case_history_entry(case):
            timestamp = last_history.get("date").replace(tzinfo=MY_TZINFO)
            if not description:
                description = last_history.get("header")

    _argus.resolve_incident(incident, description=description, timestamp=timestamp)
    incident.open = False


def get_last_case_history_entry(case: ritz.Case) -> Optional[dict]:
    """Returns the last history entry for a case"""
    history = _zino.get_history(case.id)
    if not history:
        return None
    history.sort(key=itemgetter("date"))
    return history[-1]


def create_argus_incident(zino_case: ritz.Case):
    description = describe_zino_case(zino_case)
    if not description:
        _logger.info("Ignoring Zino case %s", zino_case.id)
        return None

    _logger.info("Creating Argus incident for Zino case %s", zino_case.id)
    # ritz/zinolib datetime objects are timezone-naive, given in local time
    timestamp_opened = zino_case.opened.replace(tzinfo=MY_TZINFO)
    incident = Incident(
        start_time=timestamp_opened,
        end_time=datetime.max,
        source_incident_id=zino_case.id,
        description=description,
        tags=dict(generate_tags(zino_case)),
    )
    incident = _argus.post_incident(incident)
    synchronize_case_history(zino_case, incident)
    return incident


def setup_logging(verbosity: int = 0):
    """Configure logging instance"""

    stdout = logging.StreamHandler()
    stdout.setFormatter(FORMATTER)
    root = logging.getLogger()
    root.addHandler(stdout)
    # Disabling redundant exception logging from simple_rest_client library
    logging.getLogger("simple_rest_client.decorators").setLevel(logging.CRITICAL)

    if not verbosity:
        root.setLevel(logging.WARNING)
        _logger.critical("Enable critical logging")

    elif int(verbosity) == 1:
        root.setLevel(logging.INFO)
        _logger.info("Enable informational logging")
    elif int(verbosity) > 1:
        root.setLevel(logging.DEBUG)
        _logger.debug("Enable debug logging")
        if int(verbosity) > 2:
            # Also enable argus debugging
            # Not Implemented
            pass


def parse_arguments() -> argparse.Namespace:
    arguments = argparse.ArgumentParser()
    arguments.add_argument("-v", "--verbose", action="count")
    arguments.add_argument("-c", "--config-file", default="zinoargus.toml")
    return arguments.parse_args()


def signal_handler(_signum, _frame):
    raise SystemExit()


if __name__ == "__main__":
    main()
