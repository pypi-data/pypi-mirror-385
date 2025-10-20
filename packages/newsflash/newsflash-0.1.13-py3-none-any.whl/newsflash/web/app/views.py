from typing import Callable, Type, Literal
import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from newsflash import App
from newsflash.widgets.chart.base import Chart
from newsflash.widgets.control.select import Select
from newsflash.widgets import Button, Title
from newsflash.callback.caller import (
    get_callback_in_and_outputs, 
    render_callback_outputs,
    parse_request_inputs,
)


type ChartDimension = dict[Literal["width"] | Literal["height"], float]
type ChartDimensions = dict[str, ChartDimension]


def build_main_view(app: Type[App]) -> Callable:
    def main(request: HttpRequest, page_num: int = 1) -> HttpResponse:
        _app = app()
        titles = _app.query_all(type=Title)
        titles = [title._build(request=request) for title in titles]

        return render(
            request,
            "app/page.html",
            context={
                "content": _app.render(request),
                "page_num": page_num,
                "navbar": _app.navbar,
                "titles": titles
            },
        )

    return main


def build_button_view(app: Type[App]) -> Callable:
    def click(request: HttpRequest) -> HttpResponse:
        trigger, additional_inputs, chart_dimensions_dict = parse_request_inputs(
            request
        )

        _app = app()
        button_element = _app.query_one(trigger, Button)
        assert button_element is not None

        callback_inputs, callback_outputs = get_callback_in_and_outputs(
            button_element.on_click, additional_inputs, chart_dimensions_dict
        )

        button_element.on_click(**callback_inputs)
        return HttpResponse(render_callback_outputs(callback_outputs, request))

    return click


def build_select_view(app: Type[App]) -> Callable:
    def select(request: HttpRequest) -> HttpResponse:
        trigger, additional_inputs, chart_dimensions_dict = parse_request_inputs(
            request
        )
        trigger = trigger.removesuffix("-input")
        value = request.POST[f"{trigger}-value"]

        _app = app()
        select_element = _app.query_one(trigger, Select)
        assert select_element is not None

        callback_inputs, callback_outputs = get_callback_in_and_outputs(
            select_element.on_input, additional_inputs, chart_dimensions_dict
        )

        value_type = type(select_element.selected)
        select_element.selected = value_type(value)
        select_element.on_input(**callback_inputs)

        return HttpResponse(render_callback_outputs(callback_outputs, request))

    return select


def build_chart_view(app: Type[App]) -> Callable:
    def chart(request: HttpRequest) -> HttpResponse:
        trigger, additional_inputs, chart_dimensions_dict = parse_request_inputs(
            request
        )
        trigger = trigger.removesuffix("-wrapper")

        _app = app()
        chart_element = _app.query_one(trigger, Chart)
        assert chart_element is not None

        chart_element.width_in_px = chart_dimensions_dict[trigger]["width"]
        chart_element.height_in_px = chart_dimensions_dict[trigger]["height"]

        callback_inputs, callback_outputs = get_callback_in_and_outputs(
            chart_element.on_load, additional_inputs, chart_dimensions_dict
        )

        callback_outputs[trigger] = chart_element
        chart_element.on_load(**callback_inputs)

        return HttpResponse(render_callback_outputs(callback_outputs, request))

    return chart
