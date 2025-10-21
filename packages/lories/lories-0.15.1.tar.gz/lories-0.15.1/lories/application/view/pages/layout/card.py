# -*- coding: utf-8 -*-
"""
lories.application.view.pages.layout.card
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""

from __future__ import annotations

from collections.abc import MutableSequence
from typing import Any, Dict, Iterable, List, Optional

import dash_bootstrap_components as dbc
from dash import html


class PageCardItem(dbc.ListGroupItem):
    focus: bool

    # noinspection PyPep8Naming
    def __init__(
        self,
        children: Any,
        class_name: Optional[str] = None,
        className: Optional[str] = None,
        focus: bool = False,
        **kwargs,
    ) -> None:
        if class_name is None or len(class_name) == 0:
            class_name = className
        if class_name is None or len(class_name) == 0:
            class_name = "card-item"
        else:
            class_name = f"{class_name} card-item"

        self.focus = focus
        if focus:
            class_name = class_name.replace("card-item", "card-focus")

        super().__init__(children=children, class_name=class_name, **kwargs)


class PageCard(dbc.Card, MutableSequence[PageCardItem]):
    items = List[PageCardItem]

    def __init__(self, horizontal: bool = True, style: Dict[str, Any] = None, **kwargs) -> None:
        self.items = []
        self._body = dbc.CardBody([dbc.ListGroup(self.items, horizontal=horizontal, flush=True, style=style)])
        super().__init__(children=[self._body], **kwargs)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> PageCardItem:
        return self.items[index]

    def __setitem__(self, index: int, item: PageCardItem) -> None:
        self.items[index] = item

    def __delitem__(self, index: int) -> None:
        del self.items[index]

    def insert(self, index: int, item: PageCardItem) -> None:
        self.items.insert(index, item)

    def append(self, *children: Any, focus: bool = False) -> None:
        self.items.append(PageCardItem(list(children), focus=focus))

    def extend(self, items: Iterable[PageCardItem] | PageCard) -> None:
        if isinstance(items, PageCard):
            items = items.items
        self.items.extend(items)

    def has_items(self) -> bool:
        return len(self.items) > 0

    def add_title(self, title: str) -> None:
        self._body.children.insert(0, html.H4(title, className="card-title"))

    def add_header(self, *children: Any, **kwargs) -> None:
        children = list(children)
        self.children.insert(0, dbc.CardHeader(children, **kwargs))

    def add_footer(self, *children: Any, href: Optional[str] = None, **kwargs) -> None:
        children = list(children)
        if href is not None and len(href) > 0:
            children.append(dbc.Button("More", class_name="card-button", href=href))
        self.children.append(dbc.CardFooter(children, **kwargs))
