import os
import shutil
import questionary
import logging
from platformdirs import user_config_dir, user_log_dir

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE = "moodley"
BASE_URLS = {
    "lms": "https://lms.vit.ac.in",
    "vitol": "https://vitolcc.vit.ac.in",
}


APP_NAME = "moodley"
APP_AUTHOR = "Faheem12005"  # optional, shown in Windows AppData

def get_app_dir():
    """
    Returns the base configuration directory for Moodley.
    Example:
      - Windows: C:\\Users\\<User>\\AppData\\Roaming\\moodley
      - macOS:   ~/Library/Application Support/moodley
      - Linux:   ~/.config/moodley
    """
    path = user_config_dir(APP_NAME, APP_AUTHOR)
    os.makedirs(path, exist_ok=True)
    return path


def get_credentials_path():
    """Path for user-provided credentials.json"""
    return os.path.join(get_app_dir(), "credentials.json")


def get_token_path():
    """Path for OAuth token.json"""
    return os.path.join(get_app_dir(), "token.json")


def get_log_path():
    """Path for storing logs"""
    log_dir = user_log_dir(APP_NAME, APP_AUTHOR)
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, "moodley.log")


def setup_logging(is_background: bool = True):
    """Configures logging to both file and console"""
    log_path = get_log_path()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ]
    )
    if is_background:
        logging.info(f"Logging initialized at {log_path}")

def prompt_for_credentials():
    cred_path = get_credentials_path()
    if os.path.exists(cred_path):
        return cred_path

    logging.warn(f"credentials.json not found in the expected location: {cred_path}")
    user_path = questionary.path("Enter the full path to your credentials.json file:").ask()
    if not user_path or not os.path.exists(user_path):
        logging.error("File does not exist. Exiting.")
        return None

    os.makedirs(os.path.dirname(cred_path), exist_ok=True)
    shutil.copy(user_path, cred_path)
    logging.info(f"Copied credentials.json to {cred_path}")
    return cred_path
