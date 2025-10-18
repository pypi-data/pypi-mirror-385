from .base import Layout
from ..base import Widget


class Space(Layout):
    template_name: str = "layout/space"
    children: list[Widget] = []
