# Moodley CLI
Moodley is a cross-platform command-line tool that fetches assignments from LMS and VITOL and automatically creates corresponding events in Google Calendar.

⚠️ Note: This tool is specifically designed for VIT Chennai. The LMS and VITOL integrations are tailored for this college's systems and may not work with other institutions.
If you want to use it with other Moodle-based sites, you can update the URLs in the BASE_URLS dictionary in the core.py file.

Credentials are securely stored using the system keyring, and Google OAuth handles calendar access.

---

## Features

* Fetch assignments from LMS and VITOL.
* Automatically create Google Calendar events for assignment deadlines.
* Secure credential storage via system keyring.
* Cross-platform support: Windows, macOS, Linux.
* Simple and intuitive CLI interface.

---

## Installation

### From PyPI (Recommended)

```bash
pip install moodley
```

### From Source (Editable Mode)

```bash
git clone https://github.com/Faheem12005/moodley.git
cd moodley
pip install -e .
```

---

## Setup

Before using Moodley:

1. Obtain your `credentials.json` from the Google Cloud Console for the Calendar API.
2. Run Moodley for the first time:

```bash
moodley
```

3. Follow the prompts to enter your LMS, VITOL, and Google credentials.
4. Credentials will be securely stored, and Google OAuth will generate `token.json`.

---

## CLI Usage

```bash
moodley [OPTIONS]
```

### Fetch Assignments and Sync with Google Calendar

Fetch assignments once from all sources:

```bash
moodley --check
```

---

### Initialize Credentials and Google Calendar

```bash
moodley --init
```

This will guide you interactively to set your LMS/VITOL credentials and Google Calendar authentication.

---

### Change Existing Credentials

```bash
moodley --change
```

Allows you to update LMS, VITOL, or Google Calendar credentials interactively.

---

### Reset All Stored Credentials

```bash
moodley --reset
```

Deletes all saved credentials.

---

### Activate Background Worker

```bash
moodley --activate FREQUENCY
```

Start the background worker to fetch assignments periodically.
`FREQUENCY` is in seconds (minimum 60, default is 900).

---

### Deactivate Background Worker

```bash
moodley --deactivate
```

Stop the background worker if running.

---

### Check Background Worker Status

```bash
moodley --status
```

---

## Project Structure

```
moodley/
├── moodley/              # Main package
│   ├── __init__.py
│   ├── main.py           # CLI entry point
│   ├── core.py           # Core logic
│   ├── api.py            # LMS/VITOL API interactions
│   ├── background.py     # Background job handling
│   ├── calendar_utils.py # Google Calendar helpers
│   ├── helpers.py        # Paths, logging, token handling
│   └── models.py         # Models for validating API requests
├── tests/                # Unit tests
├── pyproject.toml        # Build configuration
├── LICENSE               # MIT License
└── README.md             # Project description
```

---

## Logging

Moodley logs runtime events automatically at:

* **Windows:** `%LOCALAPPDATA%\moodley\Logs\moodley.log`
* **macOS:** `~/Library/Application Support/moodley/Logs/moodley.log`
* **Linux:** `~/.local/share/moodley/Logs/moodley.log`

---


## License

This project is licensed under the **MIT License**. See `LICENSE` for details.
