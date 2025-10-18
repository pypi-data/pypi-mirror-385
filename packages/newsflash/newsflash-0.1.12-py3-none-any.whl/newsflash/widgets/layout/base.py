from ..base import LayoutWidget, Widget
from typing import Type, TypeVar

from pydantic import BaseModel
from django.http import HttpRequest


T = TypeVar("T")


class LayoutContext(BaseModel):
    children_and_span: list[tuple[str, int]]
    grow: bool
    main_element: bool


class Layout(LayoutWidget):
    main_element: bool = False
    children: list[Widget]
    grow: bool = False

    def get_all_children(self) -> list[Widget]:
        graphs: list[Widget] = []

        for child in self.children:
            if isinstance(child, Layout):
                graphs.append(child)
                graphs.extend(child.get_all_children())
            else:
                graphs.append(child)

        return graphs

    def query_one(self, id: str, type: Type[T]) -> T | None:
        for child in self.children:
            if child.id == id and isinstance(child, type):
                return child
            elif isinstance(child, Layout):
                child_query_one_result = child.query_one(id, type)
                if child_query_one_result is not None:
                    return child_query_one_result

        return None
    
    def query_all(self, type: Type[T], widgets: list[T] = []) -> list[T]:
        for child in self.children:
            if isinstance(child, type):
                widgets.append(child)
            elif isinstance(child, Layout):
                widgets = child.query_all(type=type, widgets=widgets)
        
        return widgets

    def query_type_one(self, id: str) -> Type[Widget] | None:
        for child in self.children:
            if child.id == id:
                return type(child)
            elif isinstance(child, Layout):
                child_query_type_result = child.query_type_one(id)
                if child_query_type_result is not None:
                    return child_query_type_result
    
    def _build(self, request: HttpRequest) -> LayoutContext:
        return LayoutContext(
            children_and_span=list(
                zip(
                    [c.render(request) for c in self.children],
                    [c.span for c in self.children],
                )
            ),
            grow=self.grow,
            main_element=self.main_element,
        )
