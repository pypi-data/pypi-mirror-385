from .base import Layout
from ..base import Widget

from pydantic import BaseModel
from django.http import HttpRequest


class FlexContext(BaseModel):
    children: list[str]
    direction: str
    main_element: bool


class Flex(Layout):
    template_name: str = "layout/flex"
    direction: str

    def _build(self, request: HttpRequest) -> FlexContext:
        return FlexContext(
            children=[child.render(request) for child in self.children],
            direction=self.direction,
            main_element=self.main_element,
        )


class FlexColumns(Flex):
    direction: str = "row"


class FlexRows(Flex):
    direction: str = "col"


def build_rows(*children: Widget, span: int = 1) -> FlexRows:
    return FlexRows(children=list(children), span=span)
