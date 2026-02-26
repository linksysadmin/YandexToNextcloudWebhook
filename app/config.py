import logging
import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Config:
    USERNAME = os.getenv("USERNAME")
    APP_PASSWORD = os.getenv("APP_PASSWORD")
    NEXTCLOUD_URL = os.getenv("NEXTCLOUD_URL")
    CALENDAR = os.getenv("CALENDAR")
    logging.info(f"{APP_PASSWORD, USERNAME, NEXTCLOUD_URL, CALENDAR}")

