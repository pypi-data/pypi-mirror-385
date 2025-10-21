# -*- coding: utf-8 -*-
"""
lories.data.databases
~~~~~~~~~~~~~~~~~~~~~


"""

from __future__ import annotations

import logging
from typing import Any, Collection, Optional

import tzlocal

import pandas as pd
from lories.connectors import ConnectorContext, ConnectType, Database
from lories.core import Configurations, Configurator, ResourceError
from lories.data.channels import Channel, Channels
from lories.data.context import DataContext
from lories.data.replication import Replications
from lories.data.retention import Retention, Retentions
from lories.util import floor_date, parse_freq, to_bool, to_timedelta, to_timezone


class Databases(ConnectorContext, Configurator):
    TYPE: str = "databases"

    # noinspection PyProtectedMember, PyUnresolvedReferences
    def __init__(self, context: DataContext, configs: Configurations) -> None:
        super().__init__(context, configs=configs.get_member(Databases.TYPE, defaults={}))
        self.load(configure=False, sort=False)
        self.configure()

        for database in context.connectors.filter(lambda c: c.is_enabled() and isinstance(c, Database)):
            self._add(database)
        self.sort()

    # noinspection PyProtectedMember
    @classmethod
    def _assert_configs(cls, configs: Configurations) -> Configurations:
        if configs is None:
            raise ResourceError(f"Invalid '{cls.__name__}' NoneType configurations")
        return super()._assert_configs(configs)

    def load(self, **kwargs: Any) -> Collection[Database]:
        databases = self._load(
            self,
            self.configs,
            configs_file=self.configs.name,
            configs_dir=self.configs.dirs.conf.joinpath(self.configs.name.replace(".conf", ".d")),
            includes=Database.INCLUDES,
            **kwargs,
        )
        # for database in databases:
        #     database._connect_type = ConnectType.NONE
        return databases

    # noinspection PyProtectedMember, PyUnresolvedReferences
    def connect(self, channels: Optional[Channels] = None) -> None:
        self.context._connect(*self.filter(self.__is_connectable), channels=channels, force=True)

    # noinspection PyProtectedMember, PyUnresolvedReferences
    def _connect(self, database: Database, channels: Optional[Channels] = None) -> None:
        if self.__is_connectable(database):
            self.context._connect(database, channels=channels, force=True)

    # noinspection PyProtectedMember
    @staticmethod
    def __is_connectable(database: Database) -> bool:
        return database._connect_type == ConnectType.NONE or not database._is_connected()

    # noinspection PyProtectedMember, PyUnresolvedReferences
    def disconnect(self):
        self.context._disconnect(*self.filter(self.__is_disconnectable))

    # noinspection PyProtectedMember, PyUnresolvedReferences
    def _disconnect(self, database: Database) -> None:
        if self.__is_disconnectable(database):
            self.context._disconnect(database)

    # noinspection PyProtectedMember
    @staticmethod
    def __is_disconnectable(database: Database) -> bool:
        return database._connect_type == ConnectType.NONE and database._is_connected()

    # noinspection PyProtectedMember
    def replicate(self, channels: Channels, full: bool = False, force: bool = False, **kwargs) -> None:
        replications = Replications()

        def build_replication(channel: Channel) -> Channel:
            channel = channel.from_logger()
            channel.replication = replications.build(self, channel, **kwargs)
            return channel

        channels = channels.apply(build_replication).filter(lambda c: c.replication is not None)

        for database in self.values():
            database_channels = channels.filter(lambda c: c.replication.database.id == database.id)
            if len(database_channels) == 0:
                continue

            self._connect(database, channels=database_channels)
            try:
                for logger, logger_channels in database_channels.groupby(lambda c: c.logger._connector):
                    self._connect(logger, channels=logger_channels)
                    try:
                        for replication, replication_channels in logger_channels.groupby(lambda c: c.replication):
                            replication.replicate(replication_channels, full=to_bool(full), force=to_bool(force))

                    except ResourceError as e:
                        self._logger.warning(f"Error replicating database '{database.id}': {str(e)}")
                        if self._logger.getEffectiveLevel() <= logging.DEBUG:
                            self._logger.exception(e)
                    finally:
                        self._disconnect(logger)
            finally:
                self._disconnect(database)

    # noinspection PyProtectedMember
    def rotate(self, channels: Channels, full: bool = False) -> None:
        retentions = Retentions()

        def build_rotation(channel: Channel) -> Channel:
            channel = channel.from_logger()
            channel.rotate = parse_freq(channel.get("rotate", default=None))
            channel.retentions = Retention.build(self.configs, channel)
            retentions.extend(channel.retentions, unique=True)
            return channel

        channels = channels.apply(build_rotation).filter(lambda c: c.rotate is not None or len(c.retentions) > 0)
        for database in self.values():
            database_channels = channels.filter(lambda c: c.has_logger(database.id))
            if len(database_channels) == 0:
                continue

            self._connect(database, channels=database_channels)
            try:
                for rotation, rotation_channels in database_channels.groupby(lambda c: c.rotate):
                    if rotation is None:
                        continue
                    freq = self.configs.get("freq", default="D")
                    timezone = to_timezone(self.configs.get("timezone", default=tzlocal.get_localzone_name()))
                    rotate = floor_date(pd.Timestamp.now(tz=timezone) - to_timedelta(rotation), freq=freq)

                    for _, deletion_channels in rotation_channels.groupby(lambda c: c.group):
                        start = database.read_first_index(deletion_channels)
                        if start is None or start > rotate:
                            self._logger.debug(
                                f"Skip rotating values of resource{'s' if len(deletion_channels) > 1 else ''} "
                                + ", ".join([f"'{r.id}'" for r in deletion_channels])
                                + " without any values found"
                            )
                            continue

                        self._logger.info(
                            f"Deleting values of resource{'s' if len(deletion_channels) > 1 else ''} "
                            + ", ".join([f"'{r.id}'" for r in deletion_channels])
                            + f" up to {rotate.strftime('%d.%m.%Y (%H:%M:%S)')}"
                        )
                        database.delete(deletion_channels, end=rotate)

                retentions.sort()
                for retention in retentions:
                    if not retention.enabled:
                        self._logger.debug(f"Skipping disabled retention '{retention.keep}'")
                        continue
                    try:
                        # noinspection PyProtectedMember
                        def has_retention(channel: Channel) -> bool:
                            return (
                                channel.logger.enabled
                                and isinstance(channel.logger._connector, Database)
                                and retention in channel.retentions
                            )

                        retention.aggregate(database_channels.filter(has_retention), full=to_bool(full))

                    except ResourceError as e:
                        self._logger.warning(
                            f"Error aggregating '{retention.method}' retaining {retention.keep}: {str(e)}"
                        )
            finally:
                self._disconnect(database)
