import os
from typing import Type, TypeVar
from newsflash.widgets.layout.base import Layout
from newsflash.widgets.base import Widget
from newsflash.widgets import Notifications, Columns

from django.http import HttpRequest
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application
from django.core.handlers.wsgi import WSGIHandler


T = TypeVar("T")


class App:
    layout: Layout
    navbar: bool = False

    def __init__(self) -> None:
        self.layout = self.compose()
        self.layout.main_element = True

    def compose(self) -> Layout:
        return Columns(children=[])

    def query_one(self, id: str, type: Type[T]) -> T | None:
        notifications = Notifications()
        if id == "notifications" and isinstance(notifications, type):
            return notifications

        return self.layout.query_one(id, type)

    def query_all(self, type: Type[T]) -> list[T]:
        return self.layout.query_all(type=type, widgets=[])

    def query_type(self, id: str) -> Type[Widget] | None:
        return self.layout.query_type_one(id)

    def render(self, request: HttpRequest) -> str:
        return self.layout.render(request)

    @classmethod
    def run(cls):
        from newsflash.web.app.urls import set_urlpatterns

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsflash.web.settings")
        set_urlpatterns(cls)
        execute_from_command_line(["manage.py", "runserver"])

    @classmethod
    def get_wsgi_application(cls) -> WSGIHandler:
        from newsflash.web.app.urls import set_urlpatterns

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsflash.web.settings")
        set_urlpatterns(cls)
        application = get_wsgi_application()
        return application
