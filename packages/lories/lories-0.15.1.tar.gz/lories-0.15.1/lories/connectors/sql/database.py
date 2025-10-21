# -*- coding: utf-8 -*-
"""
lories.connectors.sql.database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""

from __future__ import annotations

from collections import OrderedDict
from typing import Any, Dict, Iterator, Mapping, Optional

from sqlalchemy import Connection, Dialect, Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

import pandas as pd
import pytz as tz
from lories.connectors import ConnectionError, Database, DatabaseException, register_connector_type
from lories.connectors.sql import Schema, Table
from lories.core.configs import ConfigurationError
from lories.data.util import hash_value
from lories.typing import Configurations, Resources, Timestamp
from lories.util import to_timezone

# FIXME: Remove this once Python >= 3.9 is a requirement
try:
    from typing import Literal

except ImportError:
    from typing_extensions import Literal


@register_connector_type("sql")
class SqlDatabase(Database, Mapping[str, Table]):
    dialect: Dialect

    host: str
    port: int

    user: str
    password: str
    database: str

    engine: Engine
    _schema: Schema
    _connection: Connection = None

    __tables: Dict[str, Table]

    @property
    def connection(self) -> Connection:
        if not self.is_connected():
            raise ConnectionError(self, "SQL connection not open")
        return self._connection

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__tables = OrderedDict()

    def __iter__(self) -> Iterator[str]:
        return iter(self.__tables)

    def __len__(self) -> int:
        return len(self.__tables)

    def __contains__(self, table: str | Table) -> bool:
        if isinstance(table, str):
            return table in self.__tables.keys()
        if isinstance(table, Table):
            return table in self.__tables.values()
        return False

    def __getitem__(self, name: str) -> Table:
        return self.__tables[name]

    # noinspection PyShadowingBuiltins, PyProtectedMember
    def _get_vars(self) -> Dict[str, Any]:
        vars = super()._get_vars()
        vars.pop("_schema", None)
        if self.is_configured():
            vars["dialect"] = self.dialect.name
            vars["host"] = self.host
            vars["port"] = self.port
            vars["user"] = self.user
            vars["database"] = self.database
        vars["tables"] = f"[{', '.join(c.name for c in self.__tables.values())}]"
        return vars

    def configure(self, configs: Configurations) -> None:
        super().configure(configs)

        self.host = configs.get("host")
        self.port = configs.get_int("port")

        self.user = configs.get("user")
        self.password = configs.get("password")

        self.database = configs.get("database")

        dialect = configs.get("dialect").lower()
        if dialect == "mysql":
            prefix = "mysql+pymysql://"
        elif dialect == "mariadb":
            prefix = "mariadb+pymysql://"
        elif dialect == "postgresql":
            prefix = "postgresql+psycopg2://"
        else:
            raise ConfigurationError(f"Unsupported database type: {dialect}")
        try:
            self.engine = create_engine(
                url=f"{prefix}{self.user}:{self.password}@{self.host}:{self.port}/{self.database}",
                pool_recycle=-1,
            )
            self.dialect = self.engine.dialect

            self._schema = Schema(self.dialect)
            self._schema.configure(configs.get_member("tables", defaults={}))

        except SQLAlchemyError as e:
            raise ConfigurationError(f"Unable to create database engine: {str(e)}")

    def connect(self, resources: Resources) -> None:
        self._logger.debug(f"Connecting to {self.dialect.name} database {self.database}@{self.host}:{self.port}")
        try:
            self._connection = self.engine.connect()

            # Make sure the connection timezone is UTC
            now = pd.Timestamp.now()
            self._set_timezone(tz.UTC)
            if self._select_timezone().utcoffset(now).seconds != 0:
                raise DatabaseException(self, "Error setting connection timezone to UTC")

            self.__tables = self._schema.connect(self.engine, resources)

        except SQLAlchemyError as e:
            self._raise(e)

    def disconnect(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._logger.debug("Disconnected from the database")

    def _select_timezone(self) -> tz.BaseTzInfo:
        if self.dialect.name == "postgresql":
            query = "SHOW TIMEZONE"
        elif self.dialect.name in ("mariadb", "mysql"):
            query = "SELECT @@session.time_zone"
        # elif self.dialect.name == 'sqlite':
        #     query = "SELECT datetime('now')"
        else:
            raise NotImplementedError(f"Timezone setting not implemented for dialect: {self.dialect.name}")
        try:
            result = self.connection.execute(text(query))
            timezone = result.scalar()
            return to_timezone(timezone)
        except KeyError:
            raise ValueError(f"Unsupported database type: {self.dialect.name}")
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error fetching timezone: {e}")

    def _set_timezone(self, timezone: tz.BaseTzInfo) -> None:
        # tz_offset = pd.Timestamp.now(timezone).strftime("%:z")
        tz_offset = pd.Timestamp.now(timezone).strftime("%z")
        tz_offset = tz_offset[:3] + ":" + tz_offset[3:]

        if self.dialect.name == "postgresql":
            query = f"SET TIME ZONE '{tz_offset}'"
        elif self.dialect.name in ("mysql", "mariadb"):
            query = f"SET time_zone = '{tz_offset}'"
        else:
            raise NotImplementedError(f"Timezone setting not implemented for dialect: {self.dialect.name}")

        self.connection.execute(text(query))
        self.connection.commit()

    def hash(
        self,
        resources: Resources,
        start: Optional[Timestamp] = None,
        end: Optional[Timestamp] = None,
        method: Literal["MD5", "SHA1", "SHA256", "SHA512"] = "MD5",
        encoding: str = "UTF-8",
    ) -> Optional[str]:
        hashes = []
        try:
            for table_schema, schema_resources in resources.groupby("schema"):
                for table_name, table_resources in schema_resources.groupby(lambda c: c.get("table", default=c.group)):
                    if table_name not in self.__tables:
                        raise DatabaseException(self, f"Table '{table_name}' not available")

                    table = self.get(table_name)
                    select = table.hash(table_resources, start, end, method=method)
                    result = self.connection.execute(select)

                    # noinspection PyTypeChecker
                    if result.rowcount < 1:
                        continue

                    table_hashes = [r[0] for r in result.fetchall()]
                    if len(table_hashes) > 1:
                        table_hash = hash_value(",".join(table_hashes), method, encoding)
                    else:
                        table_hash = table_hashes[0]
                    hashes.append(table_hash)

        except SQLAlchemyError as e:
            self._raise(e)

        if len(hashes) == 0:
            return None
        elif len(hashes) == 1:
            return hashes[0]

        return hash_value(",".join(hashes), method, encoding)

    def exists(
        self,
        resources: Resources,
        start: Optional[Timestamp] = None,
        end: Optional[Timestamp] = None,
    ) -> bool:
        try:
            for table_schema, schema_resources in resources.groupby("schema"):
                for table_name, table_resources in schema_resources.groupby(lambda c: c.get("table", default=c.group)):
                    if table_name not in self.__tables:
                        raise DatabaseException(self, f"Table '{table_name}' not available")

                    table = self.get(table_name)
                    select = table.exists(table_resources, start, end)
                    result = self.connection.execute(select)

                    # noinspection PyTypeChecker
                    if result.rowcount < 1:
                        continue
                    count = result.scalar()
                    if count is None or int(count) > 1:
                        return True
        except SQLAlchemyError as e:
            self._raise(e)
        return False

    # noinspection PyUnresolvedReferences, PyTypeChecker
    def read(
        self,
        resources: Resources,
        start: Optional[Timestamp] = None,
        end: Optional[Timestamp] = None,
    ) -> pd.DataFrame:
        results = []
        try:
            for table_schema, schema_resources in resources.groupby("schema"):
                for table_name, table_resources in schema_resources.groupby(lambda c: c.get("table", default=c.group)):
                    table_key = table_name if table_schema is None else f"{table_schema}.{table_name}"
                    if table_key not in self.__tables:
                        raise DatabaseException(self, f"Table '{table_key}' not available")

                    table = self.get(table_key)
                    if start is None and end is None:
                        select = table.read(table_resources, order_by="desc").limit(1)
                    else:
                        select = table.read(table_resources, start, end)

                    result = self.connection.execute(select)
                    if result.rowcount > 0:
                        result_data = table.extract(table_resources, result)
                        if not result_data.empty:
                            results.append(result_data)
        except SQLAlchemyError as e:
            self._raise(e)

        if len(results) == 0:
            return pd.DataFrame()
        results = sorted(results, key=lambda d: min(d.index))
        return pd.concat(results, axis="columns")

    # noinspection PyUnresolvedReferences, PyTypeChecker
    def read_first(self, resources: Resources) -> pd.DataFrame:
        results = []
        try:
            for table_schema, schema_resources in resources.groupby("schema"):
                for table_name, table_resources in schema_resources.groupby(lambda c: c.get("table", default=c.group)):
                    if table_name not in self.__tables:
                        raise DatabaseException(self, f"Table '{table_name}' not available")

                    table = self.get(table_name)
                    select = table.read(table_resources, order_by="asc").limit(1)
                    result = self.connection.execute(select)
                    if result.rowcount > 0:
                        result_data = table.extract(table_resources, result)
                        if not result_data.empty:
                            results.append(result_data)
        except SQLAlchemyError as e:
            self._raise(e)

        if len(results) == 0:
            return pd.DataFrame()
        results = sorted(results, key=lambda d: min(d.index))
        return pd.concat(results, axis="columns")

    # noinspection PyUnresolvedReferences, PyTypeChecker
    def read_last(self, resources: Resources) -> pd.DataFrame:
        results = []
        try:
            for table_schema, schema_resources in resources.groupby("schema"):
                for table_name, table_resources in schema_resources.groupby(lambda c: c.get("table", default=c.group)):
                    if table_name not in self.__tables:
                        raise DatabaseException(self, f"Table '{table_name}' not available")

                    table = self.get(table_name)
                    select = table.read(table_resources, order_by="desc").limit(1)
                    result = self.connection.execute(select)
                    if result.rowcount > 0:
                        result_data = table.extract(table_resources, result)
                        if not result_data.empty:
                            results.append(result_data)
        except SQLAlchemyError as e:
            self._raise(e)

        if len(results) == 0:
            return pd.DataFrame()
        results = sorted(results, key=lambda d: min(d.index))
        return pd.concat(results, axis="columns")

    # noinspection PyTypeChecker
    def write(self, data: pd.DataFrame) -> None:
        try:
            for table_schema, schema_resources in self.resources.groupby("schema"):
                for table_name, table_resources in schema_resources.groupby(lambda c: c.get("table", default=c.group)):
                    if table_name not in self.__tables:
                        raise DatabaseException(self, f"Table '{table_name}' not available")
                    table_data = data.loc[:, [r.id for r in table_resources if r.id in data.columns]]
                    table_data = table_data.dropna(axis="index", how="all")
                    if table_data.empty:
                        continue
                    table = self.get(table_name)
                    insert = table.write(table_resources, table_data)
                    self._logger.debug(insert)
                    self.connection.execute(insert)

            self.connection.commit()

        except SQLAlchemyError as e:
            self._raise(e)

    def delete(
        self,
        resources: Resources,
        start: Optional[Timestamp] = None,
        end: Optional[Timestamp] = None,
    ) -> None:
        try:
            for table_schema, schema_resources in resources.groupby("schema"):
                for table_name, table_resources in schema_resources.groupby(lambda c: c.get("table", default=c.group)):
                    if table_name not in self.__tables:
                        raise DatabaseException(self, f"Table '{table_name}' not available")
                    table = self.get(table_name)
                    delete = table.delete(table_resources, start, end)
                    self._logger.debug(delete)
                    self.connection.execute(delete)

            self.connection.commit()

        except SQLAlchemyError as e:
            self._raise(e)

    # noinspection PyProtectedMember
    def is_connected(self) -> bool:
        if self._connection is None:
            return False
        return not self._connection._is_disconnect

    def _raise(self, e: SQLAlchemyError):
        if "syntax" in str(e).lower():
            raise DatabaseException(self, str(e))
        else:
            raise ConnectionError(self, str(e))
