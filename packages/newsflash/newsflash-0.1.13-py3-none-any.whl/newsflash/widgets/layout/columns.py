from .base import Layout
from ..base import Widget


class Columns(Layout):
    template_name: str = "layout/columns"
    grow: bool = False


def build_columns(*children: Widget, span: int = 1) -> Columns:
    return Columns(children=list(children), span=span)
