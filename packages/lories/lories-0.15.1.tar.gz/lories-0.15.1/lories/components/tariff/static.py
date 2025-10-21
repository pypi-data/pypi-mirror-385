# -*- coding: utf-8 -*-
"""
lories.components.tariff.static
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""

from __future__ import annotations

from typing import Optional

import pandas as pd
from lories.components import ComponentError
from lories.components.tariff import Tariff, register_tariff_type
from lories.typing import Configurations, Timestamp


# noinspection SpellCheckingInspection
@register_tariff_type("static")
class StaticTariff(Tariff):
    _price_import: float
    _price_export: float

    def configure(self, configs: Configurations) -> None:
        super().configure(configs)
        self._price_import = configs.get_float("import")
        self._price_export = configs.get_float("export", default=0)

    def get(
        self,
        start: Optional[Timestamp] = None,
        end: Optional[Timestamp] = None,
        freq: str = "15min",
        **kwargs,
    ) -> pd.DataFrame:
        if any(t is None for t in [start, end]):
            raise ComponentError(self, "Unable to generate static tariff for incomplete or missing time range")
        return pd.DataFrame(
            index=pd.date_range(start=start, end=end, freq=freq),
            data={
                Tariff.PRICE_IMPORT: self._price_import,
                Tariff.PRICE_EXPORT: self._price_export,
            },
        )
