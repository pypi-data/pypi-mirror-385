from .base import Layout


class Rows(Layout):
    template_name: str = "layout/rows"
    grow: bool = False
