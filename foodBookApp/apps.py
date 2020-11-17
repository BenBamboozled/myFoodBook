from django.apps import AppConfig


class FoodbookappConfig(AppConfig):
    name = 'foodBookApp'

    def ready(self):
        import foodBookApp.signals

