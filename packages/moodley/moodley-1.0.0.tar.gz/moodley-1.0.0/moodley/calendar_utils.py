import datetime
import os.path
import hashlib
from datetime import datetime, timedelta, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from moodley.helpers import get_credentials_path, get_token_path
import logging

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def add_deadline_event(service, summary, description, deadline_epoch, calendar_id='primary', tz='UTC'):
    """
    Adds a deadline event to Google Calendar if it doesn't already exist.

    Args:
        service: Authorized Google Calendar API service instance.
        summary (str): Title of the event.
        description (str): Details of the event.
        deadline_epoch (int or float): Deadline timestamp (in seconds since epoch).
        calendar_id (str): Calendar ID (default 'primary').
        tz (str): Timezone for display, e.g. 'America/New_York'.
    """

    # Convert epoch to datetime
    deadline_dt = datetime.fromtimestamp(deadline_epoch, timezone.utc)

    # Create a stable event ID (hash based on summary + date)
    raw_id = f"{summary}-{int(deadline_epoch)}"
    event_id = hashlib.sha1(raw_id.encode()).hexdigest()[:20]

    # Check if event already exists
    try:
        existing = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        logging.warn(f"Event already exists: {existing.get('htmlLink')}")
        return existing
    except HttpError as e:
        if e.resp.status != 404:
            raise

    # Create new event object
    start_time = deadline_dt.isoformat()
    end_time = (deadline_dt + timedelta(minutes=1)).isoformat()

    event = {
        'id': event_id,
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': tz},
        'end': {'dateTime': end_time, 'timeZone': tz},
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 60 * 24},  # 1 day before
                {'method': 'popup', 'minutes': 60},       # 1 hour before
            ],
        },
        'colorId': '11',  # red for deadlines
    }

    # Insert event
    created = service.events().insert(calendarId=calendar_id, body=event).execute()
    logging.info(f"Created new event: {created.get('htmlLink')}")
    return created

def create_event(events):
    """
    Takes a list of Moodle events and creates Google Calendar events for them.
    Uses cross-platform paths for credentials and token files with logging.
    """
    try:
        creds = None
        token_path = get_token_path()
        cred_path = get_credentials_path()

        # Load existing token if it exists
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # Perform OAuth flow if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(cred_path):
                    logging.error(f"credentials.json not found at {cred_path}. Cannot create events.")
                    return
                flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save token for future runs
            os.makedirs(os.path.dirname(token_path), exist_ok=True)
            with open(token_path, "w") as token_file:
                token_file.write(creds.to_json())

        service = build("calendar", "v3", credentials=creds)

        for assignment in events:
            try:
                add_deadline_event(
                    service=service,
                    summary=assignment.name,
                    description=assignment.description,
                    deadline_epoch=assignment.timestart,
                )
            except Exception as e:
                logging.error(f"Failed to add event '{assignment.name}': {e}")

    except HttpError as e:
        logging.error(f"Google Calendar API error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in create_event: {e}")