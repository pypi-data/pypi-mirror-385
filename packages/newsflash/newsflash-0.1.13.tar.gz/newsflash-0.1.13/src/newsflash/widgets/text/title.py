from django.http import HttpRequest
from django.utils.text import slugify

from pydantic import BaseModel, model_validator
from ..base import TextWidget
from typing import Literal, Self


type TextAlign = Literal["left"] | Literal["center"] | Literal["right"]


class TitleContext(BaseModel):
    id: str
    title: str
    text_size: str
    level: int
    navbar_text_size: str
    navbar_margin_y: str | None
    navbar_margin_start: str | None
    align: TextAlign


def map_title_level_to_title_text_size(title_level: int) -> str:
    match title_level:
        case 1:
            return "4xl"
        case 2:
            return "3xl"
        case 3:
            return "2xl"
        case _:
            raise ValueError("invalid title level")
        

def map_title_level_to_navbar_text_size(title_level: int) -> str:
    match title_level:
        case 1:
            return "2-5xl"
        case 2:
            return "2xl"
        case 3:
            return "xl"
        case _:
            raise ValueError("invalid title level")
        

def map_title_level_to_margin_y(title_level: int) -> str | None:
    match title_level:
        case 1:
            return "3"
        case 2:
            return "1"
        case 3:
            return None
        case _:
            raise ValueError("invalid title level")
        

def map_title_level_to_margin_start(title_level: int) -> str | None:
    match title_level:
        case 1:
            return None
        case 2:
            return "2"
        case 3:
            return "4"
        case _:
            raise ValueError("invalid title level")


class Title(TextWidget):
    template_name: str = "text/title"
    title: str
    text_size: str | None = None
    navbar_text_size: str | None = None
    align: TextAlign = "left"
    level: int = 1

    @model_validator(mode="after")
    def assert_text_size(self) -> Self:
        if self.text_size is None:
            self.text_size = map_title_level_to_title_text_size(self.level)
        return self
    
    @model_validator(mode="after")
    def assert_navbar_text_size(self) -> Self:
        if self.navbar_text_size is None:
            self.navbar_text_size = map_title_level_to_navbar_text_size(self.level)
        return self
    
    @model_validator(mode="after")
    def assert_id(self) -> Self:
        if self.id is None:
            self.id = slugify(self.title)
        return self

    def update_title(self, new_title: str) -> None:
        self.title = new_title

    def _build(self, request: HttpRequest) -> TitleContext:
        assert self.id is not None
        assert self.text_size is not None
        assert self.navbar_text_size is not None

        return TitleContext(
            id=self.id, 
            title=self.title, 
            text_size=self.text_size,
            level=self.level,
            navbar_text_size=self.navbar_text_size,
            navbar_margin_y=map_title_level_to_margin_y(self.level),
            navbar_margin_start=map_title_level_to_margin_start(self.level),
            align=self.align,
        )


class SubTitle(Title):
    level: int = 2


class SubSubTitle(Title):
    level: int = 3
