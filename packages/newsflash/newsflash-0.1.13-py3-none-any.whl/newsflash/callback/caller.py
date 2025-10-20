from typing import Callable, Literal
from inspect import signature
import json

from django.http import HttpRequest

from newsflash.widgets.base import Widget
from newsflash.widgets.control.select import Select
from newsflash.widgets.chart.base import Chart
from .utils import process_callback_arg
from .models import WidgetIO


# TODO: find better location (and deduplicate)
type ChartDimension = dict[Literal["width"] | Literal["height"], float]
type ChartDimensions = dict[str, ChartDimension]


def get_callback_in_and_outputs(
    callback_fn: Callable,
    additional_inputs: dict[str, str],
    chart_dimensions_dict: ChartDimensions,
) -> tuple[dict[str, Widget], dict[str, Widget]]:
    sig = signature(callback_fn)

    callback_inputs: dict[str, Widget] = {}
    callback_outputs: dict[str, Widget] = {}
    for param in sig.parameters:
        if param == "self" or param == "selected":
            continue

        widget_type, widget_id, widget_io = process_callback_arg(callback_fn, param)

        if issubclass(widget_type, Select):
            widget = widget_type(selected=additional_inputs[widget_id])

        if issubclass(widget_type, Chart):
            widget = widget_type(
                width_in_px=chart_dimensions_dict[widget_id]["width"],
                height_in_px=chart_dimensions_dict[widget_id]["height"],
                swap_oob=True,
            )

        callback_inputs[param] = widget
        if widget_io == WidgetIO.OUTPUT or widget_io == WidgetIO.BOTH:
            widget.swap_oob = True
            callback_outputs[param] = widget

    return callback_inputs, callback_outputs


def render_callback_outputs(
    callback_outputs: dict[str, Widget], request: HttpRequest
) -> bytes:
    result: str = ""

    for callback_output in callback_outputs.values():
        if callback_output._cancel_update:
            continue
        if isinstance(callback_output, Chart):
            result += "\n" + callback_output.render_chart(
                request, authenticated=request.user.is_authenticated
            )
        else:
            result += "\n" + callback_output.render(request)

    return result.encode()


def parse_chart_dimensions(request: HttpRequest) -> ChartDimensions:
    dimensions = request.POST["dimensions"]
    assert isinstance(dimensions, str)
    chart_dimensions = [
        {k.removesuffix("-container"): v for k, v in chart.items()}
        for chart in json.loads(dimensions)
    ]

    chart_dimensions_dict: ChartDimensions = {}
    for chart in chart_dimensions:
        chart_dimensions_dict.update(chart)

    return chart_dimensions_dict


def parse_additional_inputs(request: HttpRequest, trigger: str) -> dict[str, str]:
    additional_inputs: dict[str, str] = {}

    for k in request.POST:
        if k.endswith("-value") and k.removesuffix("-value") != trigger:
            _value = request.POST[k]
            assert isinstance(_value, str)
            additional_inputs[k.removesuffix("-value")] = _value

    return additional_inputs


def parse_request_inputs(
    request: HttpRequest,
) -> tuple[str, dict[str, str], ChartDimensions]:
    trigger: str = request.headers["Hx-Trigger"]  # type: ignore
    additional_inputs = parse_additional_inputs(request, trigger)
    chart_dimensions_dict = parse_chart_dimensions(request)
    return trigger, additional_inputs, chart_dimensions_dict

