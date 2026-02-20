import logging
import os

from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(override=True)
app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,           # Показывать INFO и выше
    format="%(asctime)s [%(levelname)s] %(message)s"
)


# --- Настройки Nextcloud ---
USERNAME = os.getenv("USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")
NEXTCLOUD_URL = os.getenv("NEXTCLOUD_URL")
CALENDAR = os.getenv("CALENDAR")
CALENDAR_URL = f"{NEXTCLOUD_URL}/remote.php/dav/calendars/{USERNAME}/{CALENDAR}/"


# --- ID вопросов формы (если используете отправку идентификаторов) ---
NAME_QUESTION_ID = "name"
EMAIL_QUESTION_ID = "email"


# --- Утилиты ---
def clean_name(raw_name: str) -> str:
    """Удаляет префикс текста вопроса из имени."""
    prefix = "Ваше имя "
    if raw_name.startswith(prefix):
        return raw_name[len(prefix):].strip()
    return raw_name.strip()


def escape_ical(text: str) -> str:
    """Экранирует спецсимволы для iCal."""
    if not text:
        return ""
    return text.replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")


def extract_answers(params: dict) -> dict:
    """
    Получает ответы пользователя из webhook.
    Сначала пробуем по ID вопросов (answers), если нет — используем прямые поля name/email.
    """
    # Если форма присылает answers с ID
    answers = params.get("answers", {})
    if answers:
        name = answers.get(NAME_QUESTION_ID, "Нет имени")
        email = answers.get(EMAIL_QUESTION_ID, "Нет email")
    else:
        # Если просто приходят поля name/email в params
        name = params.get("name", "Нет имени")
        email = params.get("email", "Нет email")

    return {"name": escape_ical(name), "email": escape_ical(email)}


def build_description(user_data: dict) -> str:
    """Создаёт описание события для iCal."""
    return f"Имя: {user_data['name']}\\nEmail: {user_data['email']}"


def build_ical_event(description: str, summary: str = "Yandex-форма") -> tuple[str, str]:
    """Создаёт iCal событие с уникальным UID и текущим UTC временем."""
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    event_uid = str(uuid.uuid4())
    event = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//YourApp//EN
BEGIN:VEVENT
UID:{event_uid}
DTSTAMP:{now}
DTSTART:{now}
SUMMARY:{summary}
DESCRIPTION:{description}
END:VEVENT
END:VCALENDAR
"""
    return event, event_uid


def upload_to_nextcloud(event: str, event_uid: str) -> int:
    """Загружает iCal событие в календарь Nextcloud и возвращает HTTP статус."""
    event_url = CALENDAR_URL + f"{event_uid}.ics"
    response = requests.put(
        event_url,
        data=event,
        auth=HTTPBasicAuth(USERNAME, APP_PASSWORD),
        headers={"Content-Type": "text/calendar"}
    )
    return response.status_code


# --- Flask webhook ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    logging.info(f"JSON:{data}", )
    logging.info(f"RAW: {request.data}")

    params = data.get("params", {})
    name_raw = params.get("name", "Нет имени")
    email_raw = params.get("email", "Нет email")

    name = escape_ical(clean_name(name_raw))
    email = escape_ical(email_raw)

    user_data = {"name": name, "email": email}
    description = build_description(user_data)
    event, event_uid = build_ical_event(description)
    status_code = upload_to_nextcloud(event, event_uid)

    logging.info(f"Nextcloud ответил: {status_code}")

    if status_code not in (200, 201, 204):
        return f"Nextcloud error {status_code}", 500

    return jsonify({
        "status": "received",
        "nextcloud_status": status_code,
        "name": user_data['name'],
        "email": user_data['email']
    })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
