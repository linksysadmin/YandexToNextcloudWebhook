import uuid
from icalendar import Calendar, Event
from datetime import datetime, timedelta, timezone


def bool_to_ru(value: str) -> str:
    """Конвертирует 'true'/'false' в 'Да'/'Нет'"""
    if str(value).lower() == "true":
        return "Да"
    elif str(value).lower() == "false":
        return "Нет"
    return str(value)


def build_ical_event(summary: str, description: str, start_dt: datetime, duration_minutes: int = 60):
    uid = str(uuid.uuid4())

    cal = Calendar()
    cal.add('prodid', '-//YandexFormWebhook//EN')
    cal.add('version', '2.0')

    event = Event()
    event.add('uid', uid)
    event.add('dtstamp', datetime.now(timezone.utc))
    event.add('dtstart', start_dt)
    event.add('dtend', start_dt + timedelta(minutes=duration_minutes))
    event.add('summary', summary)
    event.add('description', description)
    cal.add_component(event)

    return cal.to_ical().decode('utf-8'), uid


def decode_time_slot(code: str):
    """
    0910 -> (09:00, 60 минут)
    1011 -> (10:00, 60 минут)
    """
    if not code or len(code) != 4 or not code.isdigit():
        return None, None

    start_hour = int(code[:2])
    end_hour = int(code[2:])

    duration = (end_hour - start_hour) * 60

    if duration <= 0:
        return None, None

    start_time_str = f"{start_hour:02d}:00"
    return start_time_str, duration
