# -*- coding: utf-8 -*-
"""
lories.simulation.results
~~~~~~~~~~~~~~~~~~~~~~~~~


"""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from functools import reduce
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence

import pandas as pd
from lories.components import Component
from lories.connectors import Database
from lories.connectors.tables import HDFDatabase
from lories.core import CONSTANTS, Configurator, Constant, Directories, ResourceError, Resources
from lories.core.typing import Configurations, Timestamp
from lories.data.util import resample, scale_energy, scale_power
from lories.simulation import Durations, Progress, Result
from lories.util import parse_freq


class Results(Configurator, Sequence[Result]):
    __list: List[Result]

    __resources: Resources
    __component: Component
    __database: Database

    _freq: Optional[str]

    data: pd.DataFrame

    dirs: Directories

    durations: Durations
    progress: Progress

    def __init__(
        self,
        component: Component,
        database: Database,
        configs: Configurations,
        desc: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(configs)
        if database is None:
            database_configs = component.configs.get_member(
                key="connectors",
                ensure_exists=True,
            ).get_member(
                key="results",
                defaults={},
            )
            database_configs.update(
                {
                    "key": "results",
                    "type": "tables",
                    "file": str(component.configs.dirs.data.joinpath(".results.h5")),
                    "compression_level": 9,
                    "compression_lib": "zlib",
                }
            )
            database = HDFDatabase(component, configs=database_configs)
            database.configure(database_configs)
            component.connectors.add(database)

        self.__list = []
        self.__database = self._assert_database(database)
        self.__component = self._assert_component(component)
        self.__resources = self._extract_resources(component)

        self.dirs = component.configs.dirs
        if not self.dirs.data.exists():
            os.makedirs(self.dirs.data, exist_ok=True)
        self.dirs.tmp = self.dirs.data.joinpath(".results")
        if not self.dirs.tmp.exists():
            os.makedirs(self.dirs.tmp, exist_ok=True)

        if desc is None:
            desc = component.name
        self.progress = Progress(
            desc=desc,
            file=str(self.dirs.data.joinpath("results.json")),
            **kwargs,
        )
        self.durations = Durations(self.dirs.tmp)
        self.data = pd.DataFrame()

    @classmethod
    def _assert_database(cls, database: Database) -> Database:
        if database is None or not isinstance(database, Database):
            raise ResourceError(f"Invalid '{cls.__name__}' database: {type(database)}")
        return database

    @classmethod
    def _assert_component(cls, component: Component) -> Component:
        if component is None or not isinstance(component, Component):
            raise ResourceError(f"Invalid '{cls.__name__}' component: {type(component)}")
        return component

    @staticmethod
    def _extract_resources(component: Component) -> Resources:
        resources = []

        def extend_resources(__component: Component) -> None:
            resources.extend(__component.data.channels)
            for _component in __component.components.values():
                extend_resources(_component)

        extend_resources(component)
        return Resources(resources)

    def configure(self, configs: Configurations) -> None:
        super().configure(configs)
        self._freq = parse_freq(configs.get("freq", default=None))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join(str(r.key) for r in self.__list)})"

    def __str__(self) -> str:
        return f"{type(self).__name__}:\n\t" + "\n\t".join(f"{r.key} = {repr(r)}" for r in self.__list)

    def __contains__(self, result: str | Result) -> bool:
        if isinstance(result, str):
            return any(result == r.key for r in self.__list)
        return result in self.__list

    def __getitem__(self, index: Iterable[str] | str | int):
        if isinstance(index, str):
            for result in self.__list:
                if result.key == index:
                    return result
        if isinstance(index, Iterable):
            return [r for r in self.__list if r.key == index]
        raise KeyError(index)

    def __iter__(self) -> Iterator[Result]:
        return iter(self.__list)

    def __len__(self) -> int:
        return len(self.__list)

    def __add__(self, other):
        return [*self, *other]

    def add(
        self,
        key: str | Constant,
        name: str,
        summary: Any,
        header: str = "Summary",
        **kwargs: Any,
    ) -> None:
        self.__list.append(Result(key, name, summary, header=header, **kwargs))

    def append(self, result: Result) -> None:
        self.__list.append(result)

    def extend(self, results: Iterable[Result]) -> None:
        self.__list.extend(results)

    def __enter__(self, **kwargs) -> Results:
        configs = self.configs
        self.configure(configs)
        self.open()
        return self

    # noinspection PyShadowingBuiltins
    def __exit__(self, type, value, traceback):
        self.close()

    def open(self) -> None:
        self.__database.connect(self.__resources)

    def close(self) -> None:
        self.__database.disconnect()
        self.durations.stop()
        self.progress.close()

    @property
    def key(self) -> str:
        return self.__component.key

    @property
    def name(self) -> str:
        return self.__component.name

    @property
    def start(self) -> Optional[pd.Timestamp]:
        if len(self.data.index) == 0:
            return None
        return self.data.index[0]

    @property
    def end(self) -> Optional[pd.Timestamp]:
        if len(self.data.index) < 2:
            return None
        return self.data.index[-1]

    # noinspection PyShadowingBuiltins
    def filter(self, filter: Callable[[Result], bool]) -> Sequence[Result]:
        return [result for result in self.__list if filter(result)]

    def report(self) -> None:
        self.durations.complete()
        self.progress.complete(**self.to_dict())
        try:
            # TODO: Make reports configurable
            from lories.io import excel

            excel_file = str(self.dirs.data.joinpath("results.xlsx"))
            excel.write(excel_file, "Results", self.to_frame())

            if self.configs.get_bool("include", default=True):
                columns = {c.key: c.full_name(unit=True) for c in CONSTANTS}
                columns.update({r.get("column", default=r.key): r.full_name(unit=True) for r in self.__resources})

                if self._freq is not None:
                    resampled = []
                    for method, resources in self.__resources.groupby("aggregate"):
                        resample_columns = [r.get("column", default=r.key) for r in resources]
                        resample_columns = [c for c in resample_columns if c in self.data.columns]
                        if len(resample_columns) == 0:
                            continue
                        if method is None:
                            self._logger.warning(
                                "Skipping resources for missing aggregate function: "
                                + ", ".join(f"'{r.id}'" for r in resources)
                            )
                            continue
                        resampled.append(resample(self.data[resample_columns], self._freq, method))

                    if len(resampled) == 0:
                        data = pd.DataFrame()
                    else:
                        data = pd.concat(resampled, axis="columns")[self.data.columns]
                        data.rename(inplace=True, columns=columns)
                else:
                    data = self.data.rename(columns=columns)
                excel.write(excel_file, "Timeseries", data)

        except ImportError:
            pass

    # noinspection PyTypeChecker
    def submit(
        self,
        function: Callable[..., pd.DataFrame],
        start: Optional[Timestamp] = None,
        end: Optional[Timestamp] = None,
        *args,
        **kwargs,
    ) -> None:
        columns = {r.get("column", default=r.key): r.id for r in self.__resources}

        if self.__database.exists(self.__resources, start, end):
            data = self.__database.read(self.__resources, start, end)
            data.rename(columns={v: k for k, v in columns.items()}, inplace=True)
        else:
            data = function(start, end, *args, **kwargs)
            self.__database.write(data.rename(columns=columns))

        self.data = pd.concat([self.data, data], axis="index")

    def is_complete(self) -> bool:
        return len(self.__list) > 0 and self.durations.is_complete()

    def is_success(self) -> bool:
        return self.is_complete() and self.progress.status == "success"

    def to_dict(self) -> Dict[str, Any]:
        return {r.key: r.summary for r in self.__list}

    def to_frame(self) -> pd.DataFrame:
        summary = pd.DataFrame(columns=pd.MultiIndex.from_tuples((), names=["System", ""]))
        order = list(dict.fromkeys(r.order for r in self.__list))
        order.sort()
        for result in reduce(lambda r1, r2: r1 + r2, [self.filter(lambda r: r.order == o) for o in order]):
            name = result.name
            value = result.summary
            if re.search(r".*\[.*kWh.*]", name):
                name, value = scale_energy(name, value)
            elif re.search(r".*\[.*W.*]", name):
                name, value = scale_power(name, value)
            summary.loc[self.name, (result.header, name)] = value
        return summary
