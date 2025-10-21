# -*- coding: utf-8 -*-
"""
lories.components.errors
~~~~~~~~~~~~~~~~~~~~~~~~


"""

from __future__ import annotations

from lories._core._component import Component  # noqa
from lories.core.errors import ResourceError, ResourceUnavailableError


class ComponentError(ResourceError):
    """
    Raise if an error occurred accessing the connector.

    """

    # noinspection PyArgumentList
    def __init__(self, component: Component, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.component = component


class ComponentUnavailableError(ResourceUnavailableError, ComponentError):
    """
    Raise if an accessed connector can not be found.

    """
