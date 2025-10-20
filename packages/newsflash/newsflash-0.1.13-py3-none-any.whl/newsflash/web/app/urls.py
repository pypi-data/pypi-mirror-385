from typing import Type
from django.urls import path
from . import views
from newsflash import App


urlpatterns = []


def set_urlpatterns(app: Type[App]) -> None:
    global urlpatterns

    urlpatterns = [
        path("", views.build_main_view(app), name="home"),
        path("<int:page_num>", views.build_main_view(app), name="home"),
        path("click", views.build_button_view(app), name="click"),
        path("select", views.build_select_view(app), name="select"),
        path("chart", views.build_chart_view(app), name="chart"),
    ]
