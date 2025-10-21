# -*- coding: utf-8 -*-
"""
lories.data.manager
~~~~~~~~~~~~~~~~~~~


"""

from __future__ import annotations

import logging
import os
import signal
import time
from collections.abc import Callable
from concurrent import futures
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError
from functools import partial
from threading import Event, Thread
from typing import Any, Dict, Mapping, Optional, Type

import pandas as pd
import pytz as tz
from lories._core import _Context, _DataManager  # noqa
from lories.components import Component, ComponentContext
from lories.connectors import Connector, ConnectorContext, ConnectorError
from lories.connectors.tasks import CheckTask, ConnectTask, LogTask, ReadTask, WriteTask
from lories.core.activator import Activator
from lories.core.configs import ConfigurationError, Configurations
from lories.core.register import Registrator, RegistratorContext
from lories.core.typing import ChannelsArgument, Timestamp
from lories.data.channels import Channel, ChannelConnector, ChannelConverter, Channels, ChannelState
from lories.data.context import DataContext
from lories.data.converters import ConverterContext
from lories.data.databases import Database, Databases
from lories.data.listeners import ListenerContext
from lories.data.replication import Replication
from lories.data.retention import Retention
from lories.util import floor_date, parse_type, to_bool, to_timedelta, validate_key

# FIXME: Remove this once Python >= 3.9 is a requirement
try:
    from typing import Literal

except ImportError:
    from typing_extensions import Literal


# noinspection PyProtectedMember
class DataManager(_DataManager, DataContext, Activator):
    _converters: ConverterContext
    _connectors: ConnectorContext
    _components: ComponentContext

    _listeners: ListenerContext

    _executor: ThreadPoolExecutor
    __runner: Thread
    __interrupt: Event

    _interval: int

    def __init__(self, configs: Configurations, name: str, **kwargs) -> None:
        super().__init__(configs=configs, key=validate_key(name), name=name, **kwargs)
        self.__interrupt = Event()
        self.__interrupt.set()

        self._converters = ConverterContext(self)
        self._connectors = ConnectorContext(self)
        self._components = ComponentContext(self)
        self._listeners = ListenerContext(self)
        self._executor = ThreadPoolExecutor(
            thread_name_prefix=self.name,
            max_workers=max(int((os.cpu_count() or 1) / 2), 1),
        )
        self.__runner = Thread(name=self.name, target=self.run)

        signal.signal(signal.SIGINT, self.interrupt)
        signal.signal(signal.SIGTERM, self.deactivate)

    # noinspection PyArgumentList
    def __contains__(self, item: str | Channel | Connector | Component) -> bool:
        channels = _Context.__getattribute__(self, f"{_Context.__name__}__map")
        if isinstance(item, str):
            return item in channels.keys()
        if isinstance(item, Channel):
            return item in channels.values()
        if isinstance(item, Connector):
            return item in self._connectors.values()
        if isinstance(item, Component):
            return item in self._components.values()
        return False

    # noinspection PyShadowingBuiltins
    def _create(self, id: str, key: str, type: Type, **configs: Any) -> Channel:
        # noinspection PyShadowingBuiltins
        def build_args(
            registrator_context: RegistratorContext,
            registrator_type: str,
            name: Optional[str] = None,
        ) -> Dict[str, Any]:
            if name is None:
                name = registrator_type
            registrator_configs = configs.pop(name, None)
            if registrator_configs is None:
                return {registrator_type: None}
            if isinstance(registrator_configs, str):
                registrator_configs = {registrator_type: registrator_configs}
            elif not isinstance(registrator_configs, Mapping):
                raise ConfigurationError(f"Invalid channel {name} type: " + str(registrator_configs))
            elif registrator_type not in registrator_configs:
                return {registrator_type: None}

            registrator_id = registrator_configs.pop(registrator_type)
            if registrator_id is not None and "." not in registrator_id:
                registrator_path = id.split(".")
                for i in reversed(range(1, len(registrator_path))):
                    _registrator_id = ".".join([*registrator_path[:i], registrator_id])
                    if _registrator_id in registrator_context.keys():
                        registrator_id = _registrator_id
                        break
            registrator = registrator_context.get(registrator_id, None) if registrator_id else None
            return {registrator_type: registrator, **registrator_configs}

        if "converter" not in configs:
            converter = ChannelConverter(self._converters.get_by_dtype(parse_type(type)))
        else:
            converter = ChannelConverter(**build_args(self._converters, "converter"))
        connector = ChannelConnector(**build_args(self._connectors, "connector"))
        logger = ChannelConnector(**build_args(self._connectors, "connector", "logger"))

        return Channel(
            id=id, key=key, type=type, context=self, converter=converter, connector=connector, logger=logger, **configs
        )

    def configure(self, configs: Configurations) -> None:
        super().configure(configs)
        self._interval = configs.get_int("interval", default=1)

    def _at_configure(self, configs: Configurations) -> None:
        super()._at_configure(configs)
        self._load(self, configs, sort=False)

        self._converters.load(configure=False, sort=False)
        self._converters.configure()

        self._connectors.load(configure=False, sort=False)
        self._connectors.configure()

        self._components.load(configure=False, sort=False)
        self._components.configure()

    def _on_configure(self, configs: Configurations) -> None:
        super()._on_configure(configs)
        self._converters.sort()
        self._connectors.sort()
        self._components.sort()
        self.sort()

    # noinspection PyShadowingBuiltins
    def activate(self, filter: Optional[Callable[[Registrator], bool]] = None) -> None:
        super().activate()
        self._connect(*self._connectors.filter(_filter(filter)))
        self._activate(*self._components.filter(_filter(filter)))

    def _activate(self, *component: Component) -> None:
        for component in component:
            if not component.is_enabled():
                self._logger.debug(
                    f"Skipping to activate disabled {type(component).__name__} '{component.name}': {component.id}"
                )
                continue
            self.__activate(component)

    def __activate(self, component: Component) -> None:
        self._logger.debug(f"Activating {type(component).__name__} '{component.name}': {component.id}")
        component.activate()

        self._logger.info(f"Activated {type(component).__name__} '{component.name}': {component.id}")

    # noinspection PyShadowingBuiltins
    def connect(
        self,
        filter: Optional[Callable[[Registrator], bool]] = None,
        channels: Optional[Channels] = None,
        timeout: Optional[float] = None,
    ) -> None:
        self._connect(*self._connectors.filter(_filter(filter)), channels=channels, timeout=timeout)

    def _connect(
        self,
        *connectors: Connector,
        channels: Optional[Channels] = None,
        timeout: Optional[float] = None,
        force: bool = False,
    ) -> None:
        connect_futures = {}
        for connector in connectors:
            if not connector.is_enabled():
                self._logger.debug(
                    f"Skipping to connect disabled {type(connector).__name__} '{connector.name}': {connector.id}"
                )
                continue

            if connector._is_connected():
                self._logger.debug(
                    f"Skipping already connected {type(connector).__name__} '{connector.name}': {connector.id}"
                )
                continue

            if not connector._is_connectable() and not force:
                self._logger.debug(
                    f"Skipping not connectable {type(connector).__name__} '{connector.name}': {connector.id}"
                )
                continue

            connect_task = self.__connect(connector, channels)
            connect_future = self._executor.submit(connect_task)
            connect_futures[connect_future] = connect_task

        self.__connect_futures(connect_futures, timeout)

    def __connect(self, connector: Connector, channels: Optional[Channels] = None) -> ConnectTask:
        self._logger.debug(f"Connecting {type(connector).__name__} '{connector.name}': {connector.id}")
        if channels is None:
            channels = self.channels.filter(lambda c: c.has_connector(connector.id))
            channels.update(self.channels.filter(lambda c: c.has_logger(connector.id)).apply(lambda c: c.from_logger()))

        return ConnectTask(connector, channels)

    def __connect_futures(
        self,
        tasks: Dict[Future, ConnectTask],
        timeout: Optional[float] = None,
    ) -> None:
        try:
            for future in futures.as_completed(tasks, timeout=timeout):
                tasks.pop(future)
                self.__connect_callback(future)

        except TimeoutError:
            for future, task in tasks.items():
                self._logger.warning(f"Timed out opening connector '{task.connector.id}' after {timeout} seconds")
                future.cancel()

    def __connect_callback(self, future: Future) -> None:
        try:
            connector = future.result()
            self._logger.info(f"Connected {type(connector).__name__} '{connector.name}': {connector.id}")

        except ConnectorError as e:
            self._logger.warning(f"Failed opening connector '{e.connector.id}': {str(e)}")
            if self._logger.getEffectiveLevel() <= logging.DEBUG:
                self._logger.exception(e)

    # noinspection PyShadowingBuiltins
    def reconnect(
        self,
        filter: Optional[Callable[[Registrator], bool]] = None,
    ) -> None:
        self._reconnect(*self._connectors.filter(_filter(filter)))

    def _reconnect(self, *connectors: Connector) -> None:
        for connector in connectors:
            if not connector.is_enabled():
                self._logger.debug(
                    f"Skipping reconnecting disabled {type(connector).__name__} '{connector.name}': {connector.id}"
                )
                continue

            if not connector._is_connected() and connector._connected:
                # Connection aborted and not yet disconnected properly
                self._disconnect(connector)
                continue

            connect_task = self.__connect(connector)
            connect_future = self._executor.submit(connect_task)
            connect_future.add_done_callback(self.__connect_callback)

    # noinspection PyShadowingBuiltins
    def disconnect(
        self,
        filter: Optional[Callable[[Registrator], bool]] = None,
    ) -> None:
        self._disconnect(*self._connectors.filter(_filter(filter)))

    def _disconnect(self, *connectors: Connector) -> None:
        for connector in reversed(connectors):
            if not connector._is_connected():
                self._logger.debug(
                    f"Skipping to disconnect unconnected {type(connector).__name__} '{connector.name}': {connector.id}"
                )
                continue
            self.__disconnect(connector)

    def __disconnect(self, connector: Connector) -> None:
        try:
            self._logger.debug(f"Disconnecting {type(connector).__name__} '{connector.name}': {connector.id}")
            connector.set_channels(ChannelState.DISCONNECTING)
            connector.disconnect()

            self._logger.info(f"Disconnected {type(connector).__name__} '{connector.name}': {connector.id}")

        except Exception as e:
            self._logger.warning(f"Failed closing connector '{connector.id}': {str(e)}")
            if self._logger.getEffectiveLevel() <= logging.DEBUG:
                self._logger.exception(e)
        finally:
            connector.set_channels(ChannelState.DISCONNECTED)

    # noinspection PyShadowingBuiltins
    def deactivate(self, *_, filter: Optional[Callable[[Registrator], bool]] = None) -> None:
        self.interrupt()
        super().deactivate()
        self._deactivate(*self._components.filter(_filter(filter)))
        self._disconnect(*self._connectors.filter(_filter(filter)))

    def _deactivate(self, *components: Component) -> None:
        for component in reversed(list(components)):
            if not component.is_active():
                self._logger.debug(
                    f"Skipping to deactivate already deactivated {type(component).__name__} '{component.name}': "
                    f"{component.id}"
                )
                return
            self.__deactivate(component)

    def __deactivate(self, component: Component) -> None:
        if not component.is_active():
            self._logger.debug(
                f"Skipping to deactivate already deactivated {type(component).__name__} '{component.name}': "
                f"{component.id}"
            )
            return
        try:
            self._logger.debug(f"Deactivating {type(component).__name__} '{component.name}': {component.id}")
            component.deactivate()

            self._logger.info(f"Deactivated {type(component).__name__} '{component.name}': {component.id}")

        except Exception as e:
            self._logger.warning(f"Failed deactivating component '{component.id}': {str(e)}")
            if self._logger.getEffectiveLevel() <= logging.DEBUG:
                self._logger.exception(e)

    def interrupt(self, *_) -> None:
        self.__interrupt.set()

        # FIXME: Add cancel_futures argument again, once Python >= 3.9 is a requirement
        self._executor.shutdown(wait=True)  # , cancel_futures=True)
        if self.__runner.is_alive():
            self.__runner.join()

    def register(
        self,
        function: Callable[[pd.DataFrame], None],
        channels: Optional[ChannelsArgument] = None,
        how: Literal["any", "all"] = "any",
        unique: bool = False,
    ) -> None:
        self._listeners.register(function, self._filter_by_args(channels), how=how, unique=unique)

    @property
    def converters(self) -> ConverterContext:
        return self._converters

    @property
    def connectors(self) -> ConnectorContext:
        return self._connectors

    @property
    def components(self) -> ComponentContext:
        return self._components

    @property
    def listeners(self) -> ListenerContext:
        return self._listeners

    def notify(
        self,
        channels: Optional[ChannelsArgument] = None,
        timeout: Optional[float] = None,
    ) -> None:
        channels = self._filter_by_args(channels)
        now = pd.Timestamp.now(tz.UTC)

        def _submit_listeners(_timeout: float) -> bool:
            _futures = []
            with self.listeners:
                for _listener in self.listeners.notify(*channels):
                    _future = self._executor.submit(_listener, now)
                    _future.add_done_callback(self._notify_callback)
                    _futures.append(_future)
            if len(_futures) > 0:
                futures.wait(_futures, timeout=_timeout)
                return True
            return False

        while _submit_listeners(timeout):
            if timeout is not None:
                timeout -= (pd.Timestamp.now(tz.UTC) - now).total_seconds()
                if timeout <= 0:
                    break

    # noinspection PyUnresolvedReferences
    def _notify_callback(self, future: Future) -> None:
        exception = future.exception()
        if exception is not None:
            listener = exception.listener
            self._logger.warning(f"Failed notifying listener '{listener.id}': {str(exception)}")
            if self._logger.getEffectiveLevel() <= logging.DEBUG:
                self._logger.exception(exception)

    def start(self, wait: bool = True) -> None:
        self._logger.info(f"Starting {type(self).__name__}: {self.name}")
        self.__interrupt.clear()
        self.__runner.start()
        if wait:
            self.__runner.join()

    # noinspection PyShadowingBuiltins, PyProtectedMember
    def run(self, **kwargs) -> None:
        now = pd.Timestamp.now(tz.UTC)

        channels = self.channels.filter(lambda c: self.__is_reading(c, now))
        if len(channels) > 0:
            self.read(channels, inplace=True, **kwargs)

        interval = f"{self._interval}s"
        _sleep(interval)

        while not self.__interrupt.is_set():
            try:
                now = pd.Timestamp.now(tz.UTC)

                self.__read(now, timeout=self._interval / 4)

                self.reconnect(lambda c: c._is_reconnectable())
                self.notify(timeout=self._interval / 4)
                self.log()

                _sleep(interval, self.__interrupt.wait)

            except KeyboardInterrupt:
                self.interrupt()
                break

        self.notify()
        self.log()

    # noinspection PyShadowingBuiltins
    def has_logged(
        self,
        channels: Optional[ChannelsArgument] = None,
        start: Optional[Timestamp] = None,
        end: Optional[Timestamp] = None,
        timeout: Optional[float] = None,
    ) -> bool:
        channels = self._filter_by_args(channels)

        check_futures = {}
        for id, connector in self.connectors.items():
            if not connector._is_connected():
                continue

            def has_database(channel: Channel) -> bool:
                return channel.has_logger(id) and channel.logger.is_database()

            check_channels = channels.filter(has_database).apply(lambda c: c.from_logger())
            if len(check_channels) == 0:
                continue

            check_task = CheckTask(connector, check_channels)
            check_future = self._executor.submit(check_task, start=start, end=end)
            check_futures[check_future] = check_task

        check_results = []
        try:
            for check_future in futures.as_completed(check_futures, timeout=timeout):
                check_task = check_futures.pop(check_future)
                try:
                    check_exists = check_future.result()
                    check_results.append(check_exists)

                except ConnectorError as e:
                    self._logger.warning(f"Failed checking connector '{check_task.connector.id}': {str(e)}")
                    if self._logger.getEffectiveLevel() <= logging.DEBUG:
                        self._logger.exception(e)

                    check_results.append(False)

        except TimeoutError:
            for check_future, check_task in check_futures.items():
                self._logger.warning(
                    f"Timed out checking connector '{check_task.connector.id}' after {timeout} seconds"
                )
                check_future.cancel()
                check_results.append(False)

        if len(check_results) == 0:
            return False
        return all(check_results)

    # noinspection PyShadowingBuiltins
    def read_logged(
        self,
        channels: Optional[ChannelsArgument] = None,
        start: Optional[Timestamp] = None,
        end: Optional[Timestamp] = None,
        timeout: Optional[float] = None,
    ) -> pd.DataFrame:
        channels = self._filter_by_args(channels)

        read_futures = {}
        for id, connector in self.connectors.items():
            if not connector._is_connected():
                continue

            def has_database(channel: Channel) -> bool:
                return channel.has_logger(id) and channel.logger.is_database()

            read_channels = channels.filter(has_database).apply(lambda c: c.from_logger())
            if len(read_channels) == 0:
                continue

            read_task = ReadTask(connector, read_channels)
            read_future = self._executor.submit(read_task, start=start, end=end)
            read_futures[read_future] = read_task

        return self._read_futures(read_futures, timeout)

    # noinspection PyShadowingBuiltins, PyTypeChecker
    def read(
        self,
        channels: Optional[ChannelsArgument] = None,
        timeout: Optional[float] = None,
        inplace: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        channels = self._filter_by_args(channels)

        read_futures = {}
        for id, connector in self.connectors.items():
            if not connector._is_connected():
                continue

            read_channels = channels.filter(lambda c: c.has_connector(id))
            if len(read_channels) == 0:
                continue

            read_task = ReadTask(connector, read_channels)
            read_future = self._executor.submit(read_task, inplace=inplace, **kwargs)
            read_futures[read_future] = read_task

        return self._read_futures(read_futures, timeout, inplace)

    def _read_futures(
        self,
        tasks: Dict[Future, ReadTask],
        timeout: Optional[float] = None,
        inplace: bool = False,
    ) -> pd.DataFrame:
        results = []
        try:
            for future in futures.as_completed(tasks, timeout=timeout):
                task = tasks.pop(future)
                data = self._read_callback(task, future, inplace)
                if data is not None:
                    results.append(data)

        except TimeoutError:
            for future, task in tasks.items():
                self._logger.warning(f"Timed out reading connector '{task.connector.id}' after {timeout} seconds")
                future.cancel()
                if inplace:
                    channels = task.channels
                    channels.set_state(ChannelState.TIMEOUT)

        if len(results) == 0:
            return pd.DataFrame()
        results = sorted(results, key=lambda d: min(d.index))
        return pd.concat(results, axis="columns")

    def _read_callback(
        self,
        task: ReadTask,
        future: Future,
        inplace: bool = False,
    ) -> Optional[pd.DataFrame]:
        channels = task.channels
        try:
            return future.result()

        except ConnectorError as e:
            self._logger.warning(f"Failed reading connector '{task.connector.id}': {str(e)}")
            if self._logger.getEffectiveLevel() <= logging.DEBUG:
                self._logger.exception(e)
            if inplace:
                channels.set_state(ChannelState.READ_ERROR)
        return None

    # noinspection PyShadowingBuiltins, PyTypeChecker
    def __read(
        self,
        timestamp: Timestamp,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> None:
        channels = self.channels.filter(lambda c: self.__is_reading(c, timestamp))
        if len(channels) < 1:
            return
        self._logger.debug(f"Reading {len(channels)} channels of application: {self.name}")

        read_futures = []
        for id, connector in self.connectors.items():
            if not connector._is_connected():
                continue

            read_channels = channels.filter(lambda c: c.has_connector(id))
            if len(read_channels) == 0:
                continue

            read_task = ReadTask(connector, read_channels)
            read_future = self._executor.submit(read_task, inplace=True, **kwargs)
            read_future.add_done_callback(partial(self._read_callback, read_task, inplace=True))
            read_futures.append(read_future)

            def update_timestamp(read_channel: Channel) -> None:
                read_channel.connector.timestamp = timestamp

            read_channels.apply(update_timestamp, inplace=True)

        futures.wait(read_futures, timeout=timeout)

    def __is_reading(self, channel: Channel, timestamp: pd.Timestamp) -> bool:
        freq = channel.freq
        if (
            freq is None
            or not channel.has_connector()
            or not self.connectors.get(channel.connector.id, False)
            or not self.connectors.get(channel.connector.id).is_connected()
        ):
            return False
        if pd.isna(channel.connector.timestamp):
            return True
        next_reading = _next(freq, channel.connector.timestamp)
        return timestamp >= next_reading

    # noinspection PyShadowingBuiltins, PyShadowingNames, PyTypeChecker
    def write(
        self,
        data: pd.DataFrame,
        channels: Optional[ChannelsArgument] = None,
        timeout: Optional[float] = None,
        inplace: bool = False,
    ) -> None:
        channels = self._filter_by_args(channels)

        write_futures = {}
        for id, connector in self.connectors.items():
            if not connector._is_connected():
                continue

            write_channels = channels.filter(lambda c: (c.has_connector(id) and c.id in data.columns))
            if len(write_channels) == 0:
                continue

            write_channels.set_frame(data)
            write_task = WriteTask(connector, write_channels)
            write_future = self._executor.submit(write_task)
            write_futures[write_future] = write_task

        self._write_futures(write_futures, timeout)

    def _write_futures(
        self,
        tasks: Dict[Future, WriteTask | LogTask],
        timeout: Optional[float] = None,
        inplace: bool = False,
    ) -> None:
        try:
            for future in futures.as_completed(tasks, timeout=timeout):
                task = tasks.pop(future)
                self._write_callback(task, future, inplace)

        except TimeoutError:
            for future, task in tasks.items():
                self._logger.warning(f"Timed out writing connector '{task.connector.id}' after {timeout} seconds")
                future.cancel()
                if inplace:
                    channels = task.channels
                    channels.set_state(ChannelState.TIMEOUT)

    def _write_callback(
        self,
        task: WriteTask,
        future: Future,
        inplace: bool = False,
    ) -> None:
        channels = task.channels
        try:
            future.result()

        except ConnectorError as e:
            self._logger.warning(f"Failed writing connector '{task.connector.id}': {str(e)}")
            if self._logger.getEffectiveLevel() <= logging.DEBUG:
                self._logger.exception(e)
            if inplace:
                channels.set_state(ChannelState.WRITE_ERROR)

    # noinspection PyShadowingBuiltins, PyTypeChecker
    def log(
        self,
        channels: Optional[ChannelsArgument] = None,
        timeout: Optional[float] = None,
        blocking: bool = False,
        force: bool = False,
    ) -> None:
        if channels is None:
            channels = self.channels

        log_futures = {}
        for id, connector in self.connectors.items():
            if not connector._is_connected():
                continue

            def has_update(channel: Channel) -> bool:
                if force:
                    return True
                if channel.freq is None:
                    return pd.isna(channel.logger.timestamp) or channel.timestamp > channel.logger.timestamp
                if pd.isna(channel.logger.timestamp):
                    logger_timestamp = floor_date(channel.timestamp, freq=channel.freq)
                    if logger_timestamp == channel.timestamp:
                        logger_timestamp -= channel.timedelta
                    channel.logger.timestamp = logger_timestamp

                return channel.timestamp >= channel.logger.timestamp + channel.timedelta

            log_channels = channels.filter(lambda c: (c.has_logger(id) and c.is_valid() and has_update(c)))
            if len(log_channels) == 0:
                continue

            log_task = LogTask(connector, log_channels)
            log_future = self._executor.submit(log_task)
            log_futures[log_future] = log_task
            if not blocking:
                log_future.add_done_callback(partial(self._write_callback, log_task, inplace=False))

            def update_timestamp(channel: Channel) -> None:
                channel.logger.timestamp = channel.timestamp

            log_channels.apply(update_timestamp, inplace=True)

        if blocking:
            self._write_futures(log_futures, timeout, inplace=False)

    def rotate(
        self,
        channels: Optional[Channels] = None,
        full: bool = False,
        **kwargs,
    ) -> None:
        if channels is None:
            channels = self.channels

        defaults = self.configs.get_member(Retention.TYPE, defaults={})
        configs = Configurations(f"{Retention.TYPE}.conf", self.configs.dirs, defaults=defaults)
        configs._load(require=False)
        kwargs["full"] = configs.pop("full", default=full)

        databases = Databases(self, configs)
        databases.rotate(channels, **kwargs)

    def replicate(
        self,
        channels: Optional[Channels] = None,
        full: bool = False,
        force: bool = False,
        **kwargs,
    ) -> None:
        if channels is None:
            channels = self.channels.filter(lambda c: self.__is_replicating(c))

        defaults = self.configs.get_member(Replication.TYPE, defaults={})
        configs = Configurations(f"{Replication.TYPE}.conf", self.configs.dirs, defaults=defaults)
        configs._load(require=False)
        if not configs.enabled:
            self._logger.error(f"Unable to replicate for disabled configuration type '{Replication.TYPE}'")
            return
        kwargs["full"] = configs.pop("full", default=full)
        kwargs["force"] = configs.pop("force", default=force)
        kwargs.update({k: v for k, v in configs.items() if k not in configs.members})

        databases = Databases(self, configs)
        databases.replicate(channels, **kwargs)

    # noinspection PyMethodMayBeStatic
    def __is_replicating(self, channel: Channel, timestamp: Optional[Timestamp] = None) -> bool:
        replication = channel.get(Replication.TYPE, default=None)
        if not (
            replication is not None
            and "database" in replication
            and to_bool(replication.get("enabled", True))
            and channel.logger.enabled
            and isinstance(channel.logger._connector, Database)
        ):
            return False
        if timestamp is None:
            return True
        return timestamp <= floor_date(timestamp, freq=replication.get("freq", Replication.freq))


# noinspection PyShadowingBuiltins
def _sleep(freq: str, sleep: Callable = time.sleep) -> None:
    now = pd.Timestamp.now(tz.UTC)
    next = _next(freq, now)
    seconds = (next - now).total_seconds()
    sleep(seconds)


# noinspection PyShadowingBuiltins, PyShadowingNames
def _next(freq: str, now: Optional[pd.Timestamp] = None) -> pd.Timestamp:
    if now is None:
        now = pd.Timestamp.now(tz.UTC)
    next = floor_date(now, freq=freq)
    while next <= now:
        next += to_timedelta(freq)
    return next


def _filter(*filters: Optional[Callable[[Connector | Component], bool]]) -> Callable[[...], bool]:
    def _all_filters(registrator: Connector | Component) -> bool:
        return all(f(registrator) for f in filters if f is not None)

    return _all_filters
