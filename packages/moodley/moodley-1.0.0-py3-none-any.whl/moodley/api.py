import pydantic
import requests
from bs4 import BeautifulSoup
import time
from moodley.models import CalendarResponse
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Suppress only this warning
urllib3.disable_warnings(category=InsecureRequestWarning)

class UnauthorizedError(Exception):
    pass

def get_login_token(r: requests.Session, url) -> str:
    try:
        body = r.get(f"{url}/login/index.php")
        parsed_body = BeautifulSoup(body.text, "html.parser")
        token_tag = parsed_body.find("input", {"name": "logintoken"})
        return token_tag["value"]
    except requests.ConnectionError:
        raise



def login(r: requests.Session, url, token, username, password):
    try:
        response = r.post(f"{url}/login/index.php", {
            "username": username,
            "password": password,
            "logintoken": token
        })
        parsed_body = BeautifulSoup(response.text, "html.parser")
        if parsed_body.find(id="loginerrormessage"):
            raise UnauthorizedError("Invalid credentials.")
        sesskey_tag = parsed_body.find("input", {"name": "sesskey"})
        r.sesskey = sesskey_tag["value"]
    except requests.ConnectionError:
        raise



def fetch_assignments(base_url, username, password):
    try:
        current_time = int(time.time())
        payload = [{
            "methodname": "core_calendar_get_action_events_by_timesort",
            "args": {
                "limitnum": 50,
                "limittononsuspendedevents": True,
                "timesortfrom": current_time
            }
        }]
        r = requests.Session()
        r.verify=False
        token = get_login_token(r, base_url)
        login(r, base_url, token, username, password)
        response = r.post(f"{base_url}/lib/ajax/service.php",
              params={
                "sesskey": r.sesskey,
                "info": "core_calendar_get_action_events_by_timesort"
              },
            json=payload
        )
        data_json = response.json()[0].get("data", {})
        validated_response = CalendarResponse.model_validate(data_json)
        return validated_response

    except requests.ConnectionError:
        raise
    except pydantic.ValidationError:
        raise





