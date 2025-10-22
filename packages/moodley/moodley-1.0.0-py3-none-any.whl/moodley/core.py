import logging
import argparse
from typing import Callable
import os.path
import pydantic
import questionary
import requests
import keyring
import keyring.errors
import sys
from moodley import api
from moodley.background import activate, deactivate, get_status
from moodley.calendar_utils import create_event
from moodley.helpers import (
    prompt_for_credentials,
    get_token_path,
    setup_logging,
)
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from moodley.background import run_worker, APP_DIR

logger = logging.getLogger(__name__)

# Constants
SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE = "moodley"
BASE_URLS = {
    "lms": "https://lms.vit.ac.in",
    "vitol": "https://vitolcc.vit.ac.in",
}


class CredentialManager:
    """Handles credential storage and retrieval."""

    @staticmethod
    def get_all() -> tuple[str | None, str | None, str | None]:
        """Retrieve all stored credentials."""
        return (
            keyring.get_password(SERVICE, "username"),
            keyring.get_password(SERVICE, "password_lms"),
            keyring.get_password(SERVICE, "password_vitol"),
        )

    @staticmethod
    def set_all(username: str, password_lms: str, password_vitol: str) -> None:
        """Store credentials securely."""
        keyring.set_password(SERVICE, "username", username)
        keyring.set_password(SERVICE, "password_lms", password_lms)
        keyring.set_password(SERVICE, "password_vitol", password_vitol)

    @staticmethod
    def clear() -> None:
        """Delete all stored credentials."""
        for key in ["username", "password_lms", "password_vitol"]:
            try:
                keyring.delete_password(SERVICE, key)
            except keyring.errors.PasswordDeleteError:
                pass
        logger.info("Credentials cleared successfully")


class AssignmentFetcher:
    """Handles fetching assignments from multiple sources."""

    def __init__(self, credentials: tuple[str, str, str]):
        username, password_lms, password_vitol = credentials
        if not all([username, password_lms, password_vitol]):
            raise ValueError("Credentials not fully configured")

        self.username = username
        self.password_lms = password_lms
        self.password_vitol = password_vitol

    def fetch(self) -> None:
        """Fetch assignments from all configured sources and create calendar events."""
        credentials_map = {
            "lms": self.password_lms,
            "vitol": self.password_vitol,
        }

        for source, url in BASE_URLS.items():
            password = credentials_map[source]
            logger.info(f"Fetching from {source.upper()}...")
            result = api.fetch_assignments(url, self.username, password)
            create_event(result.events)

        logger.info("Assignments fetched and synced to calendar")


def handle_initialization() -> None:
    """Interactive initialization flow."""
    session = requests.Session()
    session.verify = False

    try:
        username, password_lms, password_vitol = CredentialManager.get_all()

        # Prompt for missing credentials
        if not username:
            username = questionary.text("Enter Registration number:").ask()
            if not username:
                logger.info("Username not provided, exiting")
                return

        if not password_lms:
            password_lms = questionary.password("Enter LMS password:").ask()
            if not password_lms:
                logger.info("LMS password not provided, exiting")
                return

        if not password_vitol:
            password_vitol = questionary.password("Enter VITOL password:").ask()
            if not password_vitol:
                logger.info("VITOL password not provided, exiting")
                return

        # Validate credentials by logging in
        logger.info("Validating credentials...")
        for source, url in BASE_URLS.items():
            password = password_lms if source == "lms" else password_vitol
            login_token = api.get_login_token(session, url)
            api.login(session, url, login_token, username, password)

        # Save credentials
        CredentialManager.set_all(username, password_lms, password_vitol)

        # Initialize Google Calendar OAuth
        _setup_google_calendar()

        logger.info("Initialization completed successfully")

    except requests.ConnectionError as e:
        logger.error("Could not connect to the server, check your network")
    except api.UnauthorizedError:
        logger.error("Invalid credentials")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise


def handle_change_credentials() -> None:
    """Interactive credential change flow."""
    session = requests.Session()
    session.verify = False

    try:
        username, password_lms, password_vitol = CredentialManager.get_all()

        # Show current credentials status
        print("\nCurrent credentials:")
        print(f"  Username: {'Set' if username else 'Not set'}")
        print(f"  LMS Password: {'Set' if password_lms else 'Not set'}")
        print(f"  VITOL Password: {'Set' if password_vitol else 'Not set'}")
        print()

        # Let user choose what to change
        choices = questionary.checkbox(
            "What would you like to change?",
            choices=[
                "Username",
                "LMS Password",
                "VITOL Password",
                "Google Calendar Credentials",
            ],
        ).ask()

        if not choices:
            logger.info("No changes selected")
            return

        # Update selected credentials
        new_username = username
        new_password_lms = password_lms
        new_password_vitol = password_vitol

        if "Username" in choices:
            new_username = questionary.text(
                "Enter new Registration number:",
                default=username or "",
            ).ask()
            if not new_username:
                logger.info("Username not provided, keeping existing")
                new_username = username

        if "LMS Password" in choices:
            new_password_lms = questionary.password("Enter new LMS password:").ask()
            if not new_password_lms:
                logger.info("LMS password not provided, keeping existing")
                new_password_lms = password_lms

        if "VITOL Password" in choices:
            new_password_vitol = questionary.password("Enter new VITOL password:").ask()
            if not new_password_vitol:
                logger.info("VITOL password not provided, keeping existing")
                new_password_vitol = password_vitol

        # Validate new credentials if any were changed
        if (new_username != username or
                new_password_lms != password_lms or
                new_password_vitol != password_vitol):

            if not all([new_username, new_password_lms, new_password_vitol]):
                logger.error("All credentials must be set. Use --reset to clear all credentials.")
                return

            logger.info("Validating new credentials...")
            credentials_to_validate = {
                "lms": (new_password_lms, password_lms != new_password_lms),
                "vitol": (new_password_vitol, password_vitol != new_password_vitol),
            }

            for source, (password, should_validate) in credentials_to_validate.items():
                if should_validate or new_username != username:
                    url = BASE_URLS[source]
                    login_token = api.get_login_token(session, url)
                    api.login(session, url, login_token, new_username, password)

            # Save new credentials
            CredentialManager.set_all(new_username, new_password_lms, new_password_vitol)
            logger.info("Credentials updated successfully")

        # Update Google Calendar if selected
        if "Google Calendar Credentials" in choices:
            _setup_google_calendar()

    except requests.ConnectionError:
        logger.error("Could not connect to the server, check your network")
    except api.UnauthorizedError:
        logger.error("Invalid credentials provided")
    except Exception as e:
        logger.error(f"Failed to change credentials: {e}")
        raise


def _setup_google_calendar() -> None:
    """Set up Google Calendar authentication."""
    cred_path = prompt_for_credentials()
    if not cred_path:
        logger.warning("Google Calendar credentials not provided")
        return

    token_path = get_token_path()
    creds = None

    # Load existing token if available
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Refresh or obtain new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server(port=0)

    # Save token for future runs
    with open(token_path, "w") as f:
        f.write(creds.to_json())


def handle_fetch() -> None:
    """Fetch assignments once."""
    try:
        credentials = CredentialManager.get_all()
        fetcher = AssignmentFetcher(credentials)
        fetcher.fetch()
    except pydantic.ValidationError:
        logger.error("Server response was not in the correct format")
    except ValueError:
        logger.error("Credentials not configured. Run 'moodley --init' first")
    except requests.ConnectionError:
        logger.error("Could not connect to the server, check your network")
    except api.UnauthorizedError:
        logger.error("Invalid credentials")


def handle_activate(frequency: int) -> None:
    """Activate background worker with frequency validation."""
    if frequency < 60:
        logger.error("Frequency must be at least 60 seconds")
        sys.exit(1)
    activate(frequency)


def setup_parser() -> argparse.ArgumentParser:
    """Configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Moodley CLI — Sync LMS/VITOL assignments to Google Calendar",
    )

    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize credentials and Google Calendar",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fetch assignments once",
    )
    parser.add_argument(
        "--change",
        action="store_true",
        help="Change existing credentials",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear all stored credentials",
    )
    parser.add_argument(
        "--activate",
        type=int,
        metavar="FREQUENCY",
        help="Start background worker (FREQUENCY in seconds, minimum 60)",
    )
    parser.add_argument(
        "--deactivate",
        action="store_true",
        help="Stop background worker",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show background worker status",
    )

    return parser


def main() -> int:
    """Main entry point. Returns exit code (0 for success, 1 for error)."""
    setup_logging(is_background=False)

    if "--run-worker" in sys.argv:
        # pop it so the normal argparse doesn't see it
        index = sys.argv.index("--run-worker")
        frequency = int(sys.argv.pop(index + 1))
        sys.argv.pop(index)  # remove the flag itself
        log_file = APP_DIR / "moodley.log"
        setup_logging(is_background=True)
        run_worker(frequency, log_file)
        sys.exit(0)

    parser = setup_parser()
    args = parser.parse_args()

    # Handler mapping
    handlers: dict[str, tuple[Callable, list]] = {
        "init": (handle_initialization, []),
        "check": (handle_fetch, []),
        "change": (handle_change_credentials, []),
        "reset": (CredentialManager.clear, []),
        "deactivate": (deactivate, []),
        "status": (get_status, []),
    }

    # Special handling for activate since it takes an argument
    if args.activate is not None:
        handlers["activate"] = (handle_activate, [args.activate])

    try:
        # Find which action to perform
        action = None
        for key in handlers:
            attr_value = getattr(args, key, False)
            if attr_value is not False and attr_value is not None:
                action = key
                break

        if action:
            func, func_args = handlers[action]
            func(*func_args)
        else:
            # Default to initialization
            handle_initialization()

    except Exception as e:
        logger.exception(f"Unhandled error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())