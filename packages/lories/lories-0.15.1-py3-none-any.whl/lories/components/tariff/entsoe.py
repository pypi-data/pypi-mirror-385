# -*- coding: utf-8 -*-
"""
lories.components.tariff.entsoe
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""

from __future__ import annotations

import pandas as pd
from lories import Constant
from lories.components.tariff import Tariff, TariffProvider, register_tariff_type
from lories.connectors.entsoe import EntsoeConnector
from lories.typing import Configurations


# noinspection SpellCheckingInspection
@register_tariff_type("entsoe", "entso_e")
class EntsoeProvider(TariffProvider):
    PRICE_DAY_AHEAD = Constant(float, "price_day_ahead", name="Day-Ahead Tariff Price", unit="€/MWh")

    _offset: float = 0

    def configure(self, configs: Configurations) -> None:
        super().configure(configs)
        self._offset = configs.get_float("offset", default=0)

        entsoe_connector = EntsoeConnector(
            self,
            key="entsoe_connector",
            name="ENTSO-e Connector",
            configs=configs,
        )
        self.connectors.add(entsoe_connector)
        self.data.add(
            EntsoeProvider.PRICE_DAY_AHEAD,
            method=EntsoeConnector.DAY_AHEAD,
            aggregate="mean",
            connector=entsoe_connector.id,
            logger={"enabled": False},
        )

    def activate(self) -> None:
        super().activate()
        self.data.register(self._on_tariff_received, EntsoeProvider.PRICE_DAY_AHEAD, unique=False)

    def _on_tariff_received(self, data: pd.DataFrame) -> None:
        timestamp = data.index[0]
        import_data = data[EntsoeProvider.PRICE_DAY_AHEAD] / 10.0 + self._offset
        import_channel = self.data.get(Tariff.PRICE_IMPORT)
        import_channel.set(timestamp, import_data)
