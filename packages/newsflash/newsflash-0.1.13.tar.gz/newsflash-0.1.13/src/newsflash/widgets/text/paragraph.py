from django.http import HttpRequest

from ..base import TextWidget
from pydantic import BaseModel


class ParagraphContext(BaseModel):
    text: str


class Paragraph(TextWidget):
    template_name: str = "text/paragraph"
    text: str

    def _build(self, request: HttpRequest) -> ParagraphContext:
        return ParagraphContext(
            text=self.text,
        )
