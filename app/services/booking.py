from datetime import datetime

from app.services.help_func import decode_time_slot, build_ical_event, bool_to_ru


class BookingService:

    def __init__(self, calendar_client):
        self.calendar_client = calendar_client

    def process_form(self, params: dict) -> list[str]:

        data = self._parse(params)
        time_slots = [t.strip() for t in data["time"].split(",") if t.strip()]

        created_uids = []

        for time_item in time_slots:
            start_time_str, duration = decode_time_slot(time_item)
            if not start_time_str:
                continue

            try:
                local_dt = datetime.strptime(
                    f"{data['date']} {start_time_str}",
                    "%Y-%m-%d %H:%M"
                )
            except ValueError:
                continue

            description = self._build_description(data)
            summary = f"[Оборудование {data['equipment_type']}] {data['name']}"

            event, uid = build_ical_event(summary, description, local_dt, duration)
            status = self.calendar_client.upload_event(event, uid)

            if status in (200, 201, 204):
                created_uids.append(uid)

        return created_uids


    def _parse(self, params):
        return {
            "name": params.get("name", "Нет имени"),
            "email": params.get("email", "Нет email"),
            "equipment": bool_to_ru(params.get("equipment", "Нет")),
            "brief": bool_to_ru(params.get("brief", "Нет")),
            "equipment_type": params.get("equipment_type"),
            "date": params.get("date"),
            "time": params.get("time"),
        }


    def _build_description(self, data):
        return (
            f"Имя: {data['name']}\n"
            f"Email: {data['email']}\n"
            f"Оборудование: {data['equipment']}\n"
            f"Тип оборудования: {data['equipment_type']}\n"
            f"Инструкция: {data['brief']}"
        )