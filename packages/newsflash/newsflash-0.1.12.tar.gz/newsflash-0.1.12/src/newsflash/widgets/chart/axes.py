from math import floor
from .utils import Point, Space, order_of_magnitude
from fontTools.ttLib import TTFont
from .element import ElementCollection, Text, Line


def build_x_axis(
    x_start: float,
    x_end: float,
    y_end: float,
    start_x_value: float,
    end_x_value: float,
    ticks: list[float],
    font_size: int,
    font: TTFont,
    labels: list[str] | None = None,
) -> ElementCollection:
    x_axis_height = font_size * 1.5

    x_axis_space = Space(
        top_left=Point(x=x_start, y=y_end - x_axis_height),
        bottom_right=Point(x=x_end, y=y_end),
    )

    if labels is None:
        labels = [str(tick) for tick in ticks]

    elements = ElementCollection()
    ticks = [(tick - start_x_value) / (end_x_value - start_x_value) for tick in ticks]

    for idx, tick in enumerate(ticks):
        elements.append(
            Text(
                text=labels[idx],
                font_size=font_size,
                pos=Point(x=tick, y=0),
                x_align="center",
                y_align="bottom",
                font=font,
                space=x_axis_space,
            )
        )

    return elements


def build_y_axis(
    y_start: float,
    y_end: float,
    x_start: float,
    bottom_y_value: float,
    top_y_value: float,
    ticks: list[float],
    font: TTFont,
    labels: list[str] | None = None,
) -> ElementCollection:
    y_axis_space = Space(
        top_left=Point(x=x_start, y=y_start),
        bottom_right=Point(x=x_start, y=y_end),
    )

    if labels is None:
        labels = [str(tick) for tick in ticks]

    elements = ElementCollection()
    ticks = [(tick + bottom_y_value) / top_y_value for tick in ticks]

    for idx, tick in enumerate(ticks):
        if tick >= 0 and tick <= 1:
            elements.append(
                Text(
                    text=labels[idx],
                    font_size=16,
                    font=font,
                    pos=Point(x=0, y=tick),
                    space=y_axis_space,
                )
            )

    return elements


def build_y_ticks(
    number_of_ticks: int,
    max_y_value: float,
) -> tuple[list[float], list[str], int]:
    y_step = max_y_value / (number_of_ticks - 1)
    y_step_order_of_magnitude = order_of_magnitude(y_step)

    scale_factor = pow(10, y_step_order_of_magnitude)

    y_steps = [
        round(y_step / scale_factor) * scale_factor * i for i in range(number_of_ticks)
    ]

    if max_y_value > y_steps[-1]:
        y_steps.append(round(y_step / scale_factor) * scale_factor * number_of_ticks)

    multiplier = pow(1000, floor(y_step_order_of_magnitude / 3))
    y_steps = [y_step / multiplier for y_step in y_steps]

    if y_step_order_of_magnitude < 0:
        labels = [f"{y:.{abs(y_step_order_of_magnitude)}f}" for y in y_steps]
    else:
        labels = [str(round(y)) for y in y_steps]

    return y_steps, labels, multiplier


def build_y_grid_lines(
    bottom_y_value: float,
    top_y_value: float,
    ticks: list[float],
    space: Space,
) -> ElementCollection:
    elements = ElementCollection()

    ticks = [(tick + bottom_y_value) / top_y_value for tick in ticks]

    for tick in ticks:
        if tick >= 0 and tick <= 1:
            elements.append(
                Line(
                    from_pos=Point(x=0, y=tick),
                    to_pos=Point(x=1, y=tick),
                    space=space,
                    stroke_width=2,
                    stroke_color="rgba(96, 96, 96, 0.1)",
                )
            )

    return elements
