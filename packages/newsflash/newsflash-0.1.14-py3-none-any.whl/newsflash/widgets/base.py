from typing import TypeVar

from django.http import HttpRequest
from django.template.loader import render_to_string
from pydantic import BaseModel


T = TypeVar("T", bound="Widget")


class Widget(BaseModel):
    template_name: str = ""
    id: str | None = None
    width_in_px: float = 0.0
    height_in_px: float = 0.0
    span: int = 1
    swap_oob: bool = False
    _cancel_update: bool = False

    class Config:
        validate_assignment = True

    class Context(BaseModel):
        width: float
        height: float

    def cancel_update(self) -> None:
        self._cancel_update = True

    def _build(self, request: HttpRequest) -> Context: ...

    def render(self, request: HttpRequest) -> str:
        return render_to_string(
            f"app/widgets/{self.template_name}.html",
            context=self._build(request).model_dump(),
            request=request,
        )

    def update_dimensions(self, width_in_px: float, height_in_px: float) -> None:
        self.width_in_px = width_in_px
        self.height_in_px = height_in_px


class ChartWidget(Widget): ...


class ControlWidget(Widget): ...


class TextWidget(Widget): ...


class LayoutWidget(Widget): ...