from math import floor
from django.http import HttpRequest
from django.contrib.humanize.templatetags.humanize import intcomma
from .base import Chart
from pydantic import BaseModel
from .utils import Point, Space
from fontTools.ttLib import TTFont
from pathlib import Path

from .element import Text, ElementCollection
from .element import Path as PathElement
from .axes import build_x_axis, build_y_axis, build_y_grid_lines, build_y_ticks
from .title import build_title


def build_lines(
    xs: list[float],
    ys: list[float],
    multiplier: float,
    max_y: float,
    space: Space,
) -> ElementCollection:
    elements = ElementCollection()

    ys = [y / multiplier for y in ys]
    normalized_ys = [y / max_y for y in ys]
    min_x, max_x = xs[0], xs[-1]
    normalized_xs = [(x - min_x) / (max_x - min_x) for x in xs]

    points: list[Point] = []
    for idx, x in enumerate(normalized_xs):
        points.append(Point(x=x, y=normalized_ys[idx]))

    elements.append(
        PathElement(
            points=points,
            stroke_color="hsl(0, 49%, 41%)",
            space=space,
        )
    )

    return elements


class LineChartContext(BaseModel):
    id: str
    width: float
    height: float
    elements: list[str]
    swap_oob: bool = False


class LineChart(Chart):
    chart_template_name: str = "chart/chart"

    xs: list[float] = []
    ys: list[float] = []

    def set_points(self, xs: list[float], ys: list[float]) -> None:
        self.xs = xs
        self.ys = ys

    def _build_chart(self, request: HttpRequest, id: str) -> LineChartContext:
        font = TTFont(
            Path(__file__).resolve().parent.parent.parent
            / "fonts"
            / "noto-serif"
            / "NotoSerif.ttf"
        )

        elements = ElementCollection()

        if self.title is not None:
            title = build_title(
                text=self.title,
                x_end=self.width_in_px,
                font=font,
            )

            elements.append(title)
            title_height = title.get_height()
        else:
            title_height = 0

        x_axis_font_size = 16
        x_axis_height = x_axis_font_size * 1.5

        y_ticks, y_labels, multiplier = build_y_ticks(
            number_of_ticks=4,
            max_y_value=max(self.ys),
        )

        if multiplier != 1:
            multiplier_text = Text(
                text=f"x {intcomma(multiplier)}",
                pos=Point(x=0, y=title_height),
                y_align="bottom",
                font_size=x_axis_font_size,
                font=font,
                color="gray",
            )
            elements.append(multiplier_text)

        y_axis = build_y_axis(
            y_start=title_height * 2,
            y_end=self.height_in_px - x_axis_height,
            x_start=0,
            bottom_y_value=0.0,
            top_y_value=max(y_ticks),
            ticks=y_ticks,
            labels=y_labels,
            font=font,
        )

        bar_width = ((self.width_in_px - y_axis.get_width()) / len(self.ys)) / 2
        chart_start_x = y_axis.get_width() + x_axis_font_size

        ticks_step = floor(len(self.xs) / 8)

        x_axis = build_x_axis(
            x_start=chart_start_x + bar_width,
            x_end=self.width_in_px - bar_width,
            y_end=self.height_in_px,
            start_x_value=self.xs[0],
            end_x_value=self.xs[-1],
            ticks=list(range(int(self.xs[0]), int(self.xs[-1]) + 1, ticks_step)),
            font_size=x_axis_font_size,
            font=font,
        )

        y_grid_lines = build_y_grid_lines(
            bottom_y_value=0.0,
            top_y_value=max(y_ticks),
            ticks=y_ticks,
            space=Space(
                top_left=Point(x=chart_start_x + bar_width, y=title_height * 2),
                bottom_right=Point(
                    x=self.width_in_px - bar_width, y=self.height_in_px - x_axis_height
                ),
            ),
        )

        bars = build_lines(
            xs=self.xs,
            ys=self.ys,
            multiplier=multiplier,
            max_y=max(y_ticks),
            space=Space(
                top_left=Point(x=chart_start_x + bar_width, y=title_height * 2),
                bottom_right=Point(
                    x=self.width_in_px - bar_width, y=self.height_in_px - x_axis_height
                ),
            ),
        )

        elements.extend(y_axis)
        elements.extend(x_axis)
        elements.extend(y_grid_lines)
        elements.extend(bars)

        assert self.id is not None
        return LineChartContext(
            id=self.id,
            width=self.width_in_px,
            height=self.height_in_px,
            elements=elements.render(),
            swap_oob=self.swap_oob,
        )
