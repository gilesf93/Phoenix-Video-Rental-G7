from django.apps import AppConfig


class RentalsConfig(AppConfig):
    name = "rentals"

    def ready(self):
        from . import signals  # noqa: F401
