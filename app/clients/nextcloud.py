import requests
import logging


class NextcloudClient:

    def __init__(self, base_url, username, password, calendar):
        self.calendar_url = f"{base_url}/remote.php/dav/calendars/{username}/{calendar}/"

        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            "Content-Type": "text/calendar"
        })

    def upload_event(self, event: str, uid: str) -> int:
        url = self.calendar_url + f"{uid}.ics"

        try:
            response = self.session.put(url, data=event, allow_redirects=False)
            logging.info(f"Nextcloud status: {response.status_code}")
            return response.status_code
        except Exception as e:
            logging.error(f"Nextcloud error: {e}")
            return 500
