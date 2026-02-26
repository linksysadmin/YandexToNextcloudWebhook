import logging

from flask import Flask
from app.config import Config
from app.clients.nextcloud import NextcloudClient
from app.services.booking import BookingService
from app.routes import create_routes


def create_app():
    app = Flask(__name__)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )

    client = NextcloudClient(
        Config.NEXTCLOUD_URL,
        Config.USERNAME,
        Config.APP_PASSWORD,
        Config.CALENDAR
    )

    booking_service = BookingService(client)

    app.register_blueprint(create_routes(booking_service))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
