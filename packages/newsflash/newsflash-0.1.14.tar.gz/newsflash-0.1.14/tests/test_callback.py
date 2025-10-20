from typing import Any, Annotated
import unittest

from newsflash.callback.builder import construct_callback
from newsflash.callback.utils import process_callback_arg
from newsflash.callback.models import Callback, WidgetIO
from newsflash.widgets.chart.bar import BarChart
from newsflash.widgets import Button


class TestProcessCallbackArgs(unittest.TestCase):
    def setUp(self) -> None:
        def dummy_callback_function(
            self: Any,
            bar_chart: Annotated[BarChart, "bar-chart-id"],
            button: Annotated[Button, "button-id"],
        ):
            pass

        self.dummy_callback_function = dummy_callback_function

    def test_process_callback_arg_for_chart(self):
        result = process_callback_arg(self.dummy_callback_function, "bar_chart")

        expected = (BarChart, "bar-chart-id", WidgetIO.OUTPUT)

        self.assertEqual(result, expected)

    def test_process_callback_arg_for_button(self):
        result = process_callback_arg(self.dummy_callback_function, "button")

        expected = (Button, "button-id", WidgetIO.INPUT)

        self.assertEqual(result, expected)


class TestCallback(unittest.TestCase):
    def test_construct_callback_with_button_and_chart(self):
        def dummy_callback_function(
            self: Any,
            bar_chart: Annotated[BarChart, "bar-chart-id"],
            button: Annotated[Button, "button-id"],
        ):
            pass

        result = construct_callback(
            callback_fn=dummy_callback_function,
            endpoint_name="ABC",
            trigger_event="click",
        )

        expected = Callback(
            endpoint_name="ABC",
            trigger_event="click",
            inputs=["button-id-input"],
            targets=["bar-chart-id"],
            target_wrapper_ids="#bar-chart-id-wrapper",
        )

        self.assertEqual(result, expected)
