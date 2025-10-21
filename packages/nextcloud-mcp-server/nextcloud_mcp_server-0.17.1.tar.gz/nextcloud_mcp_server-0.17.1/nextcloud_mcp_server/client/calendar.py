"""CalDAV client for Nextcloud calendar and task operations using caldav library."""

import datetime as dt
import logging
import uuid
from typing import Any, Dict, List, Optional

import anyio
from caldav.async_collection import AsyncCalendar
from caldav.async_davclient import AsyncDAVClient
from httpx import Auth
from icalendar import Alarm, Calendar, vRecur
from icalendar import Event as ICalEvent
from icalendar import Todo as ICalTodo

logger = logging.getLogger(__name__)


class CalendarClient:
    """Client for Nextcloud CalDAV calendar and task operations."""

    def __init__(self, base_url: str, username: str, auth: Auth | None = None):
        """Initialize CalendarClient with AsyncDAVClient.

        Args:
            base_url: Nextcloud base URL
            username: Nextcloud username
            auth: httpx.Auth object (BasicAuth or BearerAuth)
        """
        self.username = username
        self.base_url = base_url
        # AsyncDAVClient needs the full base URL for proper URL construction
        self._dav_client = AsyncDAVClient(
            url=f"{base_url}/remote.php/dav/",
            username=username,
            auth=auth,
        )
        self._calendar_home_url = f"{base_url}/remote.php/dav/calendars/{username}/"

    def _get_calendar_url(self, calendar_name: str) -> str:
        """Get the full URL for a calendar."""
        return f"{self._calendar_home_url}{calendar_name}/"

    def _get_calendar(self, calendar_name: str) -> AsyncCalendar:
        """Get an AsyncCalendar object for the given calendar name."""
        calendar_url = self._get_calendar_url(calendar_name)
        return AsyncCalendar(
            client=self._dav_client, url=calendar_url, name=calendar_name
        )

    async def close(self):
        """Close the DAV client connection."""
        await self._dav_client.close()

    async def _wait_for_calendar_propagation(
        self, calendar_name: str, max_attempts: int = 40, initial_delay_ms: int = 100
    ) -> None:
        """Wait for calendar to propagate through Nextcloud's DAV backend.

        After MKCALENDAR succeeds (201), the calendar may not be immediately queryable
        due to Nextcloud's internal caching/indexing. This polls until it appears.

        Args:
            calendar_name: Name of the calendar to wait for
            max_attempts: Maximum polling attempts (default: 40)
            initial_delay_ms: Initial delay between attempts in ms (default: 100ms)
        """
        logger.info(f"Waiting for calendar '{calendar_name}' to propagate...")
        delay_ms = initial_delay_ms

        for attempt in range(max_attempts):
            try:
                logger.debug(
                    f"Attempt {attempt + 1}/{max_attempts} to find calendar '{calendar_name}'..."
                )
                calendars = await self.list_calendars()
                if any(cal["name"] == calendar_name for cal in calendars):
                    logger.info(
                        f"Calendar '{calendar_name}' became available after {attempt + 1} attempts"
                    )
                    return
            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_attempts} to verify calendar '{calendar_name}' failed: {e}"
                )

            if attempt < max_attempts - 1:
                await anyio.sleep(delay_ms / 1000.0)
                # Exponential backoff: double delay up to 2 seconds max
                delay_ms = min(delay_ms * 2, 2000)

        logger.error(
            f"Calendar '{calendar_name}' did not become available after {max_attempts} attempts."
        )

    # ============= Calendar Operations =============

    async def list_calendars(self) -> List[Dict[str, Any]]:
        """List all available calendars for the user."""
        # Use custom PROPFIND with CalendarServer namespace (cs:) for calendar-color.
        # caldav library's nsmap lacks "CS" namespace, and its CalendarColor uses
        # Apple iCal namespace which Nextcloud doesn't recognize.
        from lxml import etree

        propfind_body = """<?xml version="1.0" encoding="utf-8"?>
<d:propfind xmlns:d="DAV:" xmlns:cs="http://calendarserver.org/ns/" xmlns:c="urn:ietf:params:xml:ns:caldav">
    <d:prop>
        <d:displayname/>
        <d:resourcetype/>
        <cs:getctag/>
        <c:calendar-description/>
        <cs:calendar-color/>
    </d:prop>
</d:propfind>"""

        response = await self._dav_client.propfind(
            self._calendar_home_url, props=propfind_body, depth=1
        )

        result = []

        # Parse XML response
        tree = etree.fromstring(response.raw.encode("utf-8"))
        ns = {
            "d": "DAV:",
            "cs": "http://calendarserver.org/ns/",
            "c": "urn:ietf:params:xml:ns:caldav",
        }

        for response_elem in tree.findall(".//d:response", ns):
            # Check if this is a calendar (has resourcetype/calendar)
            resourcetype = response_elem.find(".//d:resourcetype", ns)
            if (
                resourcetype is not None
                and resourcetype.find(".//c:calendar", ns) is not None
            ):
                href = response_elem.find("./d:href", ns)
                if href is not None and href.text:
                    calendar_url = href.text
                    # Extract calendar name from URL
                    calendar_name = calendar_url.rstrip("/").split("/")[-1]

                    # Skip if this is the calendar home itself
                    if calendar_url.rstrip("/") == self._calendar_home_url.rstrip("/"):
                        continue

                    display_name_elem = response_elem.find(".//d:displayname", ns)
                    display_name = (
                        display_name_elem.text
                        if display_name_elem is not None and display_name_elem.text
                        else calendar_name
                    )

                    description_elem = response_elem.find(
                        ".//c:calendar-description", ns
                    )
                    description = (
                        description_elem.text
                        if description_elem is not None and description_elem.text
                        else ""
                    )

                    color_elem = response_elem.find(".//cs:calendar-color", ns)
                    color = (
                        color_elem.text
                        if color_elem is not None and color_elem.text
                        else "#1976D2"
                    )

                    result.append(
                        {
                            "name": calendar_name,
                            "display_name": display_name,
                            "description": description,
                            "color": color,
                            "href": calendar_url,
                        }
                    )

        logger.debug(f"Found {len(result)} calendars")
        return result

    async def create_calendar(
        self,
        calendar_name: str,
        display_name: str = "",
        description: str = "",
        color: str = "#1976D2",
    ) -> Dict[str, Any]:
        """Create a new calendar with retry on 429 errors."""
        # Use custom MKCALENDAR XML instead of caldav library's make_calendar() due to:
        # 1. Missing CalendarServer namespace (cs:) in caldav's nsmap
        # 2. caldav's CalendarColor uses Apple iCal namespace, not cs:calendar-color
        # 3. make_calendar() doesn't support calendar-description or calendar-color params
        calendar_url = (
            f"{self.base_url}/remote.php/dav/calendars/{self.username}/{calendar_name}/"
        )

        mkcalendar_body = f"""<?xml version="1.0" encoding="utf-8"?>
<mkcalendar xmlns="urn:ietf:params:xml:ns:caldav" xmlns:d="DAV:" xmlns:cs="http://calendarserver.org/ns/">
    <d:set>
        <d:prop>
            <d:displayname>{display_name or calendar_name}</d:displayname>
            <cs:calendar-color>{color}</cs:calendar-color>
            <caldav:calendar-description xmlns:caldav="urn:ietf:params:xml:ns:caldav">{description}</caldav:calendar-description>
            <caldav:supported-calendar-component-set xmlns:caldav="urn:ietf:params:xml:ns:caldav">
                <caldav:comp name="VEVENT"/>
                <caldav:comp name="VTODO"/>
            </caldav:supported-calendar-component-set>
        </d:prop>
    </d:set>
</mkcalendar>"""

        # Create calendar via MKCALENDAR request
        response = await self._dav_client.mkcalendar(calendar_url, mkcalendar_body)

        if response.status != 201:
            raise RuntimeError(
                f"Failed to create calendar '{calendar_name}': HTTP {response.status}"
            )

        logger.debug(f"Created calendar: {calendar_name}")

        # Wait for calendar to be queryable (Nextcloud eventual consistency)
        await self._wait_for_calendar_propagation(calendar_name)

        return {
            "name": calendar_name,
            "display_name": display_name or calendar_name,
            "description": description,
            "color": color,
            "status_code": 201,
        }

    async def delete_calendar(self, calendar_name: str) -> Dict[str, Any]:
        """Delete a calendar."""
        # Use absolute URL for deletion
        calendar_url = (
            f"{self.base_url}/remote.php/dav/calendars/{self.username}/{calendar_name}/"
        )
        await self._dav_client.delete(calendar_url)

        logger.debug(f"Deleted calendar: {calendar_name}")
        return {"status_code": 204}

    # ============= Event Operations =============

    async def get_calendar_events(
        self,
        calendar_name: str,
        start_datetime: Optional[dt.datetime] = None,
        end_datetime: Optional[dt.datetime] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List events in a calendar within date range."""
        calendar = self._get_calendar(calendar_name)

        # Get all events using caldav library (now with proper filter)
        events = await calendar.events()

        result = []
        for event in events:
            await event.load(only_if_unloaded=True)
            event_dict = self._parse_ical_event(event.data)
            if event_dict:
                event_dict["href"] = str(event.url)
                event_dict["etag"] = ""
                result.append(event_dict)

            if len(result) >= limit:
                break

        logger.debug(f"Found {len(result)} events")
        return result

    async def create_event(
        self, calendar_name: str, event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new calendar event."""
        calendar = self._get_calendar(calendar_name)

        event_uid = str(uuid.uuid4())
        ical_content = self._create_ical_event(event_data, event_uid)

        # save_event returns (event, response) tuple
        event, response = await calendar.save_event(ical=ical_content)

        if response.status not in [201, 204]:
            raise RuntimeError(
                f"Failed to create event {event_uid}: HTTP {response.status}"
            )

        logger.debug(f"Created event {event_uid}")

        return {
            "uid": event_uid,
            "href": str(event.url),
            "etag": "",
            "status_code": 201,
        }

    async def update_event(
        self,
        calendar_name: str,
        event_uid: str,
        event_data: Dict[str, Any],
        etag: str = "",
    ) -> Dict[str, Any]:
        """Update an existing calendar event."""
        calendar = self._get_calendar(calendar_name)

        # Find the event by UID using caldav library
        event = await calendar.event_by_uid(event_uid)
        await event.load(only_if_unloaded=True)

        # Merge updates into existing iCal data
        updated_ical = self._merge_ical_properties(event.data, event_data, event_uid)
        event.data = updated_ical

        await event.save()

        logger.debug(f"Updated event {event_uid}")
        return {
            "uid": event_uid,
            "href": str(event.url),
            "etag": "",
            "status_code": 200,
        }

    async def delete_event(self, calendar_name: str, event_uid: str) -> Dict[str, Any]:
        """Delete a calendar event."""
        calendar = self._get_calendar(calendar_name)

        try:
            event = await calendar.event_by_uid(event_uid)
            await event.delete()
            logger.debug(f"Deleted event {event_uid}")
            return {"status_code": 204}
        except Exception as e:
            logger.debug(f"Event {event_uid} not found: {e}")
            return {"status_code": 404}

    async def get_event(
        self, calendar_name: str, event_uid: str
    ) -> tuple[Dict[str, Any], str]:
        """Get detailed information about a specific event."""
        calendar = self._get_calendar(calendar_name)

        event = await calendar.event_by_uid(event_uid)
        await event.load(only_if_unloaded=True)

        event_data = self._parse_ical_event(event.data)
        if not event_data:
            raise ValueError(f"Failed to parse event data for {event_uid}")

        event_data["href"] = str(event.url)
        event_data["etag"] = ""

        logger.debug(f"Retrieved event {event_uid}")
        return event_data, ""

    async def search_events_across_calendars(
        self,
        start_datetime: Optional[dt.datetime] = None,
        end_datetime: Optional[dt.datetime] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search events across all calendars with advanced filtering."""
        try:
            calendars = await self.list_calendars()
            all_events = []

            for calendar in calendars:
                try:
                    events = await self.get_calendar_events(
                        calendar["name"], start_datetime, end_datetime
                    )

                    # Apply filters if provided
                    if filters:
                        events = self._apply_event_filters(events, filters)

                    # Add calendar info to each event
                    for event in events:
                        event["calendar_name"] = calendar["name"]
                        event["calendar_display_name"] = calendar.get(
                            "display_name", calendar["name"]
                        )

                    all_events.extend(events)
                except Exception as e:
                    logger.warning(
                        f"Error getting events from calendar {calendar['name']}: {e}"
                    )
                    continue

            return all_events

        except Exception as e:
            logger.error(f"Error searching events across calendars: {e}")
            raise

    # ============= Todo/Task Operations (NEW) =============

    async def list_todos(
        self, calendar_name: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List todos/tasks in a calendar."""
        calendar = self._get_calendar(calendar_name)

        # Get all todos using caldav library (now with proper filter)
        todos = await calendar.todos()

        result = []
        for todo in todos:
            # Only load if data not already present from REPORT response
            # This avoids 404 errors for virtual calendars (e.g., Deck boards)
            await todo.load(only_if_unloaded=True)
            todo_dict = self._parse_ical_todo(todo.data)
            if todo_dict:
                todo_dict["href"] = str(todo.url)
                todo_dict["etag"] = ""

                # Apply filters if provided
                if not filters or self._todo_matches_filters(todo_dict, filters):
                    result.append(todo_dict)

        logger.debug(f"Found {len(result)} todos")
        return result

    async def create_todo(
        self, calendar_name: str, todo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new todo/task."""
        calendar = self._get_calendar(calendar_name)

        todo_uid = str(uuid.uuid4())
        ical_content = self._create_ical_todo(todo_data, todo_uid)

        # save_todo returns (todo, response) tuple
        todo, response = await calendar.save_todo(ical=ical_content)

        if response.status not in [201, 204]:
            raise RuntimeError(
                f"Failed to create todo {todo_uid}: HTTP {response.status}"
            )

        logger.debug(f"Created todo {todo_uid}")

        return {
            "uid": todo_uid,
            "href": str(todo.url),
            "etag": "",
            "status_code": 201,
        }

    async def update_todo(
        self,
        calendar_name: str,
        todo_uid: str,
        todo_data: Dict[str, Any],
        etag: str = "",
    ) -> Dict[str, Any]:
        """Update an existing todo/task."""
        calendar = self._get_calendar(calendar_name)

        try:
            # Find the todo by UID
            todo = await calendar.todo_by_uid(todo_uid)
            await todo.load(only_if_unloaded=True)

            logger.debug(
                f"Loaded todo {todo_uid}, current data length: {len(todo.data)}"
            )

            # Merge updates into existing iCal data
            updated_ical = self._merge_ical_todo_properties(
                todo.data, todo_data, todo_uid
            )
            logger.debug(f"Merged iCal data length: {len(updated_ical)}")
            logger.debug(f"Updated iCal content:\n{updated_ical}")

            todo.data = updated_ical

            save_result = await todo.save()
            logger.debug(f"Save result: {save_result}")

            logger.debug(f"Updated todo {todo_uid}")
            return {
                "uid": todo_uid,
                "href": str(todo.url),
                "etag": "",
                "status_code": 200,
            }
        except Exception as e:
            logger.error(f"Error updating todo {todo_uid}: {e}", exc_info=True)
            raise

    async def delete_todo(self, calendar_name: str, todo_uid: str) -> Dict[str, Any]:
        """Delete a todo/task."""
        calendar = self._get_calendar(calendar_name)

        try:
            todo = await calendar.todo_by_uid(todo_uid)
            await todo.delete()
            logger.debug(f"Deleted todo {todo_uid}")
            return {"status_code": 204}
        except Exception as e:
            logger.debug(f"Todo {todo_uid} not found: {e}")
            return {"status_code": 404}

    async def search_todos_across_calendars(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search todos across all calendars."""
        try:
            calendars = await self.list_calendars()
            all_todos = []

            for calendar in calendars:
                try:
                    todos = await self.list_todos(calendar["name"], filters)

                    # Add calendar info to each todo
                    for todo in todos:
                        todo["calendar_name"] = calendar["name"]
                        todo["calendar_display_name"] = calendar.get(
                            "display_name", calendar["name"]
                        )

                    all_todos.extend(todos)
                except Exception as e:
                    logger.warning(
                        f"Error getting todos from calendar {calendar['name']}: {e}"
                    )
                    continue

            return all_todos

        except Exception as e:
            logger.error(f"Error searching todos across calendars: {e}")
            raise

    # ============= Helper Methods - Event iCalendar =============

    def _create_ical_event(self, event_data: Dict[str, Any], event_uid: str) -> str:
        """Create iCalendar content from event data."""
        cal = Calendar()
        cal.add("prodid", "-//Nextcloud MCP Server//EN")
        cal.add("version", "2.0")

        event = ICalEvent()
        event.add("uid", event_uid)
        event.add("summary", event_data.get("title", ""))
        event.add("description", event_data.get("description", ""))
        event.add("location", event_data.get("location", ""))

        # Handle dates/times
        start_str = event_data.get("start_datetime", "")
        end_str = event_data.get("end_datetime", "")
        all_day = event_data.get("all_day", False)

        if start_str:
            if all_day:
                start_date = dt.datetime.fromisoformat(start_str.split("T")[0]).date()
                event.add("dtstart", start_date)
                if end_str:
                    end_date = dt.datetime.fromisoformat(end_str.split("T")[0]).date()
                    event.add("dtend", end_date)
            else:
                start_dt = dt.datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                event.add("dtstart", start_dt)
                if end_str:
                    end_dt = dt.datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                    event.add("dtend", end_dt)

        # Add categories
        categories = event_data.get("categories", "")
        if categories:
            event.add("categories", categories.split(","))

        # Add priority and status
        priority = event_data.get("priority", 5)
        event.add("priority", priority)

        status = event_data.get("status", "CONFIRMED")
        event.add("status", status)

        # Add privacy classification
        privacy = event_data.get("privacy", "PUBLIC")
        event.add("class", privacy)

        # Add URL
        url = event_data.get("url", "")
        if url:
            event.add("url", url)

        # Handle recurrence
        recurring = event_data.get("recurring", False)
        if recurring:
            recurrence_rule = event_data.get("recurrence_rule", "")
            if recurrence_rule:
                event.add("rrule", vRecur.from_ical(recurrence_rule))

        # Add alarms/reminders
        reminder_minutes = event_data.get("reminder_minutes", 0)
        if reminder_minutes > 0:
            alarm = Alarm()
            alarm.add("action", "DISPLAY")
            alarm.add("description", "Event reminder")
            alarm.add("trigger", dt.timedelta(minutes=-reminder_minutes))
            event.add_component(alarm)

        # Add attendees
        attendees = event_data.get("attendees", "")
        if attendees:
            for email in attendees.split(","):
                if email.strip():
                    event.add("attendee", f"mailto:{email.strip()}")

        # Add timestamps
        now = dt.datetime.now(dt.UTC)
        event.add("created", now)
        event.add("dtstamp", now)
        event.add("last-modified", now)

        cal.add_component(event)
        return cal.to_ical().decode("utf-8")

    def _parse_ical_event(self, ical_text: str) -> Optional[Dict[str, Any]]:
        """Parse iCalendar text and extract event data."""
        try:
            cal = Calendar.from_ical(ical_text)
            for component in cal.walk():
                if component.name == "VEVENT":
                    event_data = {
                        "uid": str(component.get("uid", "")),
                        "title": str(component.get("summary", "")),
                        "description": str(component.get("description", "")),
                        "location": str(component.get("location", "")),
                        "status": str(component.get("status", "CONFIRMED")),
                        "priority": int(component.get("priority", 5)),
                        "privacy": str(component.get("class", "PUBLIC")),
                        "url": str(component.get("url", "")),
                    }

                    # Handle dates
                    dtstart = component.get("dtstart")
                    if dtstart:
                        if isinstance(dtstart.dt, dt.date) and not isinstance(
                            dtstart.dt, dt.datetime
                        ):
                            event_data["start_datetime"] = dtstart.dt.isoformat()
                            event_data["all_day"] = True
                        else:
                            event_data["start_datetime"] = dtstart.dt.isoformat()
                            event_data["all_day"] = False

                    dtend = component.get("dtend")
                    if dtend:
                        if isinstance(dtend.dt, dt.date) and not isinstance(
                            dtend.dt, dt.datetime
                        ):
                            event_data["end_datetime"] = dtend.dt.isoformat()
                        else:
                            event_data["end_datetime"] = dtend.dt.isoformat()

                    # Handle categories
                    categories = component.get("categories")
                    if categories:
                        event_data["categories"] = self._extract_categories(categories)

                    # Handle recurrence
                    rrule = component.get("rrule")
                    if rrule:
                        event_data["recurring"] = True
                        event_data["recurrence_rule"] = str(rrule)

                    # Handle attendees
                    attendees = []
                    for attendee in component.get("attendee", []):
                        if isinstance(attendee, list):
                            attendees.extend(
                                str(a).replace("mailto:", "") for a in attendee
                            )
                        else:
                            attendees.append(str(attendee).replace("mailto:", ""))
                    if attendees:
                        event_data["attendees"] = ",".join(attendees)

                    return event_data

            return None

        except Exception as e:
            logger.error(f"Error parsing iCalendar event: {e}")
            return None

    def _merge_ical_properties(
        self, raw_ical: str, event_data: Dict[str, Any], event_uid: str
    ) -> str:
        """Merge new event data into existing raw iCal while preserving all properties."""
        try:
            cal = Calendar.from_ical(raw_ical)

            for component in cal.walk():
                if component.name == "VEVENT":
                    # Update only provided properties
                    if "title" in event_data:
                        component["SUMMARY"] = event_data["title"]
                    if "description" in event_data:
                        component["DESCRIPTION"] = event_data["description"]
                    if "location" in event_data:
                        component["LOCATION"] = event_data["location"]
                    if "status" in event_data:
                        component["STATUS"] = event_data["status"].upper()
                    if "priority" in event_data:
                        component["PRIORITY"] = event_data["priority"]
                    if "privacy" in event_data:
                        component["CLASS"] = event_data["privacy"].upper()
                    if "url" in event_data:
                        component["URL"] = event_data["url"]

                    # Handle dates
                    if "start_datetime" in event_data:
                        start_str = event_data["start_datetime"]
                        all_day = event_data.get("all_day", False)
                        if all_day:
                            start_date = dt.datetime.fromisoformat(
                                start_str.split("T")[0]
                            ).date()
                            component["DTSTART"] = start_date
                        else:
                            start_dt = dt.datetime.fromisoformat(
                                start_str.replace("Z", "+00:00")
                            )
                            component["DTSTART"] = start_dt

                    if "end_datetime" in event_data:
                        end_str = event_data["end_datetime"]
                        all_day = event_data.get("all_day", False)
                        if all_day:
                            end_date = dt.datetime.fromisoformat(
                                end_str.split("T")[0]
                            ).date()
                            component["DTEND"] = end_date
                        else:
                            end_dt = dt.datetime.fromisoformat(
                                end_str.replace("Z", "+00:00")
                            )
                            component["DTEND"] = end_dt

                    # Update timestamps
                    from icalendar import vDDDTypes

                    now = dt.datetime.now(dt.UTC)
                    component["LAST-MODIFIED"] = vDDDTypes(now)
                    component["DTSTAMP"] = vDDDTypes(now)

                    break

            return cal.to_ical().decode("utf-8")

        except Exception as e:
            logger.error(f"Error merging iCal properties: {e}")
            return self._create_ical_event(event_data, event_uid)

    # ============= Helper Methods - Todo iCalendar =============

    def _ensure_timezone_aware(self, datetime_str: str) -> dt.datetime:
        """Parse datetime string and ensure it's timezone-aware.

        If the datetime string doesn't include timezone info, interpret it as UTC.
        This ensures RFC 5545 compliance for CalDAV/iCalendar properties.

        Args:
            datetime_str: ISO format datetime string (e.g., "2025-10-19T14:30:00" or "2025-10-19T14:30:00Z")

        Returns:
            Timezone-aware datetime object
        """
        # Replace 'Z' with '+00:00' for consistent parsing
        datetime_str = datetime_str.replace("Z", "+00:00")

        # Parse the datetime
        parsed_dt = dt.datetime.fromisoformat(datetime_str)

        # If timezone-naive, assume UTC
        if parsed_dt.tzinfo is None:
            parsed_dt = parsed_dt.replace(tzinfo=dt.UTC)

        return parsed_dt

    def _create_ical_todo(self, todo_data: Dict[str, Any], todo_uid: str) -> str:
        """Create iCalendar VTODO content from todo data."""
        cal = Calendar()
        cal.add("prodid", "-//Nextcloud MCP Server//EN")
        cal.add("version", "2.0")

        todo = ICalTodo()
        todo.add("uid", todo_uid)
        todo.add("summary", todo_data.get("summary", ""))
        todo.add("description", todo_data.get("description", ""))

        # Status
        status = todo_data.get("status", "NEEDS-ACTION").upper()
        todo.add("status", status)

        # Priority (0-9, 0=undefined)
        priority = todo_data.get("priority", 0)
        todo.add("priority", priority)

        # Percent complete
        percent = todo_data.get("percent_complete", 0)
        todo.add("percent-complete", percent)

        # Due date
        due = todo_data.get("due", "")
        if due:
            from icalendar import vDDDTypes

            due_dt = self._ensure_timezone_aware(due)
            todo.add("due", vDDDTypes(due_dt))

        # Start date
        dtstart = todo_data.get("dtstart", "")
        if dtstart:
            from icalendar import vDDDTypes

            start_dt = self._ensure_timezone_aware(dtstart)
            todo.add("dtstart", vDDDTypes(start_dt))

        # Completed timestamp
        completed = todo_data.get("completed", "")
        if completed:
            from icalendar import vDDDTypes

            completed_dt = self._ensure_timezone_aware(completed)
            todo.add("completed", vDDDTypes(completed_dt))

        # Categories
        categories = todo_data.get("categories", "")
        if categories:
            todo.add("categories", categories.split(","))

        # Add timestamps
        now = dt.datetime.now(dt.UTC)
        todo.add("created", now)
        todo.add("dtstamp", now)
        todo.add("last-modified", now)

        cal.add_component(todo)
        return cal.to_ical().decode("utf-8")

    def _parse_ical_todo(self, ical_text: str) -> Optional[Dict[str, Any]]:
        """Parse iCalendar text and extract todo data."""
        try:
            cal = Calendar.from_ical(ical_text)
            for component in cal.walk():
                if component.name == "VTODO":
                    todo_data = {
                        "uid": str(component.get("uid", "")),
                        "summary": str(component.get("summary", "")),
                        "description": str(component.get("description", "")),
                        "status": str(component.get("status", "NEEDS-ACTION")),
                        "priority": int(component.get("priority", 0)),
                        "percent_complete": int(component.get("percent-complete", 0)),
                    }

                    # Handle due date
                    due = component.get("due")
                    if due:
                        todo_data["due"] = due.dt.isoformat()

                    # Handle start date
                    dtstart = component.get("dtstart")
                    if dtstart:
                        todo_data["dtstart"] = dtstart.dt.isoformat()

                    # Handle completed date
                    completed = component.get("completed")
                    if completed:
                        todo_data["completed"] = completed.dt.isoformat()

                    # Handle categories
                    categories = component.get("categories")
                    if categories:
                        todo_data["categories"] = self._extract_categories(categories)

                    return todo_data

            return None

        except Exception as e:
            logger.error(f"Error parsing iCalendar todo: {e}")
            return None

    def _merge_ical_todo_properties(
        self, raw_ical: str, todo_data: Dict[str, Any], todo_uid: str
    ) -> str:
        """Merge new todo data into existing raw iCal while preserving all properties."""
        try:
            logger.debug(
                f"Merging todo properties for {todo_uid}: {list(todo_data.keys())}"
            )
            cal = Calendar.from_ical(raw_ical)

            for component in cal.walk():
                if component.name == "VTODO":
                    # Update only provided properties
                    if "summary" in todo_data:
                        component["SUMMARY"] = todo_data["summary"]
                    if "description" in todo_data:
                        component["DESCRIPTION"] = todo_data["description"]
                    if "status" in todo_data:
                        status_value = todo_data["status"].upper()
                        component["STATUS"] = status_value
                        logger.debug(f"Set STATUS to {status_value}")
                    if "priority" in todo_data:
                        component["PRIORITY"] = todo_data["priority"]
                    if "percent_complete" in todo_data:
                        percent_value = todo_data["percent_complete"]
                        component["PERCENT-COMPLETE"] = percent_value
                        logger.debug(f"Set PERCENT-COMPLETE to {percent_value}")

                    # Import vDDDTypes at the beginning for datetime formatting
                    from icalendar import vDDDTypes

                    # Handle due date
                    if "due" in todo_data:
                        due_str = todo_data["due"]
                        if due_str:
                            due_dt = self._ensure_timezone_aware(due_str)
                            component["DUE"] = vDDDTypes(due_dt)
                            logger.debug(f"Set DUE to {due_dt}")

                    # Handle start date
                    if "dtstart" in todo_data:
                        dtstart_str = todo_data["dtstart"]
                        if dtstart_str:
                            dtstart_dt = self._ensure_timezone_aware(dtstart_str)
                            component["DTSTART"] = vDDDTypes(dtstart_dt)
                            logger.debug(f"Set DTSTART to {dtstart_dt}")

                    # Handle completed date
                    if "completed" in todo_data:
                        completed_str = todo_data["completed"]
                        if completed_str:
                            completed_dt = self._ensure_timezone_aware(completed_str)
                            component["COMPLETED"] = vDDDTypes(completed_dt)
                            logger.debug(f"Set COMPLETED to {completed_dt}")

                    # Handle categories
                    if "categories" in todo_data:
                        categories_str = todo_data["categories"]
                        if categories_str:
                            component["CATEGORIES"] = categories_str.split(",")
                            logger.debug(f"Set CATEGORIES to {categories_str}")

                    # Update timestamps
                    now = dt.datetime.now(dt.UTC)
                    component["LAST-MODIFIED"] = vDDDTypes(now)
                    component["DTSTAMP"] = vDDDTypes(now)

                    break

            return cal.to_ical().decode("utf-8")

        except Exception as e:
            logger.error(f"Error merging iCal todo properties: {e}", exc_info=True)
            return self._create_ical_todo(todo_data, todo_uid)

    # ============= Helper Methods - Filtering =============

    def _extract_categories(self, categories_obj) -> str:
        """Extract categories from icalendar object to string."""
        if not categories_obj:
            return ""

        try:
            if hasattr(categories_obj, "cats"):
                # Handle Categories object with cats attribute
                return ", ".join(str(cat) for cat in categories_obj.cats)
            elif hasattr(categories_obj, "__iter__") and not isinstance(
                categories_obj, str
            ):
                # Handle list of vCategory objects or strings
                result = []
                for cat in categories_obj:
                    # Try to extract value from vCategory objects using to_ical()
                    if hasattr(cat, "to_ical"):
                        result.append(cat.to_ical().decode("utf-8"))
                    else:
                        result.append(str(cat))
                return ", ".join(result)
            else:
                # Handle single category string or object
                if hasattr(categories_obj, "to_ical"):
                    return categories_obj.to_ical().decode("utf-8")
                return str(categories_obj)
        except Exception as e:
            logger.warning(f"Error extracting categories: {e}")
            return str(categories_obj)

    def _apply_event_filters(
        self, events: List[Dict[str, Any]], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply advanced filters to event list."""
        return [
            event for event in events if self._event_matches_filters(event, filters)
        ]

    def _event_matches_filters(
        self, event: Dict[str, Any], filters: Dict[str, Any]
    ) -> bool:
        """Check if an event matches the provided filters."""
        try:
            # Filter by minimum attendees
            if "min_attendees" in filters:
                attendees = event.get("attendees", "")
                attendee_count = len(attendees.split(",")) if attendees else 0
                if attendee_count < filters["min_attendees"]:
                    return False

            # Filter by categories
            if "categories" in filters:
                event_categories = event.get("categories", "").lower()
                required_categories = [cat.lower() for cat in filters["categories"]]
                if not any(cat in event_categories for cat in required_categories):
                    return False

            # Filter by status
            if "status" in filters:
                if event.get("status", "").upper() != filters["status"].upper():
                    return False

            # Filter by title contains
            if "title_contains" in filters:
                title = event.get("title", "").lower()
                search_term = filters["title_contains"].lower()
                if search_term not in title:
                    return False

            # Filter by location contains
            if "location_contains" in filters:
                location = event.get("location", "").lower()
                search_term = filters["location_contains"].lower()
                if search_term not in location:
                    return False

            return True

        except Exception:
            return True

    def _todo_matches_filters(
        self, todo: Dict[str, Any], filters: Dict[str, Any]
    ) -> bool:
        """Check if a todo matches the provided filters."""
        try:
            # Filter by status
            if "status" in filters:
                if todo.get("status", "").upper() != filters["status"].upper():
                    return False

            # Filter by minimum priority
            if "min_priority" in filters:
                priority = todo.get("priority", 0)
                if priority == 0 or priority > filters["min_priority"]:
                    return False

            # Filter by categories
            if "categories" in filters:
                todo_categories = todo.get("categories", "").lower()
                required_categories = [cat.lower() for cat in filters["categories"]]
                if not any(cat in todo_categories for cat in required_categories):
                    return False

            # Filter by summary contains
            if "summary_contains" in filters:
                summary = todo.get("summary", "").lower()
                search_term = filters["summary_contains"].lower()
                if search_term not in summary:
                    return False

            return True

        except Exception:
            return True

    # ============= Legacy Methods (for backward compatibility) =============

    async def bulk_update_events(
        self, filter_criteria: Dict[str, Any], update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Bulk update events matching filter criteria."""
        try:
            start_datetime = None
            end_datetime = None
            if "start_date" in filter_criteria and filter_criteria["start_date"]:
                start_datetime = dt.datetime.fromisoformat(
                    filter_criteria["start_date"]
                )
            if "end_date" in filter_criteria and filter_criteria["end_date"]:
                end_datetime = dt.datetime.fromisoformat(filter_criteria["end_date"])

            events = await self.search_events_across_calendars(
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                filters=filter_criteria,
            )

            updated_count = 0
            failed_count = 0
            results = []

            for event in events:
                try:
                    await self.update_event(
                        event["calendar_name"], event["uid"], update_data
                    )
                    updated_count += 1
                    results.append(
                        {
                            "uid": event["uid"],
                            "status": "updated",
                            "title": event.get("title", ""),
                        }
                    )
                except Exception as e:
                    failed_count += 1
                    results.append(
                        {
                            "uid": event["uid"],
                            "status": "failed",
                            "error": str(e),
                            "title": event.get("title", ""),
                        }
                    )

            return {
                "total_found": len(events),
                "updated_count": updated_count,
                "failed_count": failed_count,
                "results": results,
            }

        except Exception as e:
            logger.error(f"Error in bulk update: {e}")
            raise

    async def find_availability(
        self,
        duration_minutes: int,
        attendees: Optional[List[str]] = None,
        start_datetime: Optional[dt.datetime] = None,
        end_datetime: Optional[dt.datetime] = None,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Find available time slots for scheduling.

        Note: This is a simplified stub that returns empty list.
        Full implementation would require complex free/busy analysis.
        """
        logger.warning("find_availability is not fully implemented with AsyncDavClient")
        return []
