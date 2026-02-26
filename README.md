# Yandex Form → Nextcloud Calendar Webhook

![Nextcloud](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQqico_ZkMibmY2TKeuCYzwKqFM-fViduEtJw&s) ![Flask](https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/flask-logo-icon.png)

**Автоматическая интеграция Яндекс.Форм с календарём Nextcloud через webhook.**
Все ответы из формы превращаются в события iCal и загружаются в выбранный календарь Nextcloud.

---

## 🔹 Возможности

* Приём webhook от Яндекс.Форм
* Обработка полей формы: `name`, `email` и дополнительные поля
* Генерация iCal события с уникальным UID
* Загрузка событий в календарь Nextcloud через WebDAV
* Лёгкая настройка через `.env`
* Production-ready запуск через Gunicorn + Docker
* Поддержка ngrok для тестирования локально

---

## ⚙️ Установка и запуск локально

```bash
git clone https://github.com/linksysadmin/YandexToNextcloudWebhook.git
cd YandexToNextcloudWebhook
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Создайте файл `.env` в корне проекта:

```env
USERNAME='service-bot'
APP_PASSWORD='ваш_пароль_приложения'
NEXTCLOUD_URL='https://example.com'
CALENDAR='-'          # идентификатор календаря
FLASK_PORT=5000
WEBHOOK_SECRET='секретный_ключ'  # для HMAC-проверки webhook
```

* `USERNAME` — сервисный аккаунт Nextcloud
* `APP_PASSWORD` — пароль приложения, созданный в Nextcloud
* `CALENDAR` — идентификатор календаря
* `WEBHOOK_SECRET` — безопасная проверка webhook

### 🔹 Dev запуск

```bash
python run.py
```

* Приложение слушает порт из `.env` (по умолчанию 5000)
* Для ngrok-теста можно пробросить порт наружу:

```bash
ngrok http 5000
```

---

## ⚡ Docker / Production

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

* Gunicorn запускает 4 worker-а
* `EXPOSE 5000` — internal Docker port

### docker-compose.yml

```yaml
version: "3.9"
services:
  webhook:
    build: .
    container_name: flask_webhook
    env_file:
      - .env
    restart: always
    expose:
      - "5000"  # виден только внутри Docker network
```

### 🔹 Настройка Nginx (если есть на 80/443)

Добавьте проксирование к контейнеру:

```nginx
location /webhook/ {
    proxy_pass http://webhook:5000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

---

## 🔗 Настройка webhook в Яндекс.Формах

| Параметр      | Значение                                                                           |
| ------------- | ---------------------------------------------------------------------------------- |
| URL           | [https://your-ngrok-url.ngrok.io/webhook](https://your-ngrok-url.ngrok.io/webhook) |
| Метод         | POST                                                                               |
| Формат данных | JSON                                                                               |

Пример JSON от Яндекс.Форм:

```json
{
  "formId": "123456",
  "formName": "Регистрация",
  "params": {
    "name": "Иван Иванов",
    "email": "ivan@mail.com"
  }
}
```

---

## 📂 Пример iCal события

```ical
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//YourApp//EN
BEGIN:VEVENT
UID:9f1c2e7e-42d3-42c6-bf3a-7e1b6f453gs
DTSTAMP:20260220T123456Z
DTSTART:20260220T123456Z
SUMMARY:Yandex-форма
DESCRIPTION:Имя: Иван Иванов\nEmail: ivan@mail.com
END:VEVENT
END:VCALENDAR
```

---

## 🛠 Работа с календарём Nextcloud

### Список календарей пользователя

```bash
curl -u service-bot:APP_PASSWORD -X PROPFIND -H "Depth: 1" \
https://example.com/remote.php/dav/calendars/service-bot/
```

### Загрузка события

```bash
curl -u service-bot:APP_PASSWORD -X PUT \
-H "Content-Type: text/calendar" \
--data-binary @event.ics \
https://example.com/remote.php/dav/calendars/service-bot/-/9f1c2e7e-5d56-4c7e-bf3a-7e1b6f65f19a.ics
```

---

## 🔹 Логи приложения

Пример логов:

```
2026-02-20 15:24:43 [INFO] JSON: {'params': {'name': 'Иван Иванов', 'email': 'ivan@mail.com'}}
2026-02-20 15:24:43 [INFO] Nextcloud ответил: 201
```

**Важно:** логирование скрывает пароли и секреты для безопасности.

---

## ⚠️ Обработка ошибок

| Код | Причина                                | Решение                                                 |
| --- | -------------------------------------- | ------------------------------------------------------- |
| 401 | Неправильный USERNAME или APP_PASSWORD | Проверьте `.env` и пароль приложения Nextcloud          |
| 403 | Нет прав на календарь                  | Убедитесь, что сервисный аккаунт имеет доступ на запись |
| 404 | Неверный URL календаря                 | Проверьте CALENDAR и путь в Nextcloud                   |
| 500 | Ошибка Nextcloud                       | Логируйте response.status_code и response.text          |

Пример возврата при ошибке:

```json
{
  "error": "Nextcloud error 403"
}
```

---

## 💡 Советы по использованию

* Создайте отдельный сервисный аккаунт с правами только на нужный календарь
* Для тестирования используйте ngrok или другой туннель
* Проверяйте доступность календаря через PROPFIND
* Используйте уникальный UID для каждого события, чтобы не было дублирования

---

## 📂 Структура проекта

```
.
├── app.py             # Основное приложение Flask
├── requirements.txt   # Зависимости Python
├── .env               # Настройки приложения
├── Dockerfile         # Docker image для продакшн
├── docker-compose.yml # Композиция контейнеров
└── README.md          # Документация
```

---

## 📜 Лицензия

MIT License © 2026

---

## ❤️ Благодарности

* Nextcloud CalDAV API
* Flask веб-фреймворк
* Yandex Forms — удобный сбор данных

