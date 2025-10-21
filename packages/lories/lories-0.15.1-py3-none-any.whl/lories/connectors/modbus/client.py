# -*- coding: utf-8 -*-
"""
lories.connectors.modbus.client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""

from __future__ import annotations

from typing import Mapping

from pymodbus import FramerType, ModbusException
from pymodbus.client import ModbusBaseSyncClient, ModbusSerialClient, ModbusTcpClient, ModbusUdpClient

import pandas as pd
import pytz as tz
from lories._core import ChannelState  # noqa
from lories.connectors import ConnectionError, Connector, ConnectorError, register_connector_type
from lories.connectors.modbus import ModbusRegister
from lories.core.configs import ConfigurationError
from lories.typing import Configurations, Resources

# FIXME: Remove this once Python >= 3.9 is a requirement
try:
    from typing import Literal

except ImportError:
    from typing_extensions import Literal


@register_connector_type("modbus")
class ModbusClient(Connector):
    __client: ModbusBaseSyncClient
    __registers: Mapping[str, ModbusRegister]

    _endian: Literal["big", "little"]

    # noinspection SpellCheckingInspection
    def configure(self, configs: Configurations) -> None:
        super().configure(configs)
        _endian = configs.get("endian", default="big").lower()
        if _endian not in ["big", "little"]:
            raise ConnectorError(self, f"Invalid modbus word order '{_endian}'")
        self._endian = _endian

        timeout = configs.get_int("timeout", default=3)
        retries = configs.get_int("retries", default=3)

        protocol = configs.get("protocol").lower()
        if protocol == "tcp":
            self.__client = ModbusTcpClient(
                host=configs.get("host"),
                port=configs.get_int("port", 502),
                framer=FramerType.SOCKET,
                timeout=timeout,
                retries=retries,
                # source_address=("localhost", 0),
            )
        elif protocol == "udp":
            self.__client = ModbusUdpClient(
                host=configs.get("host"),
                port=configs.get_int("port", 502),
                framer=FramerType.SOCKET,
                timeout=timeout,
                retries=retries,
                # source_address=None,
            )
        elif protocol in ["rtu", "serial"]:
            self.__client = ModbusSerialClient(
                port=configs.get("port"),
                framer=FramerType.RTU,
                timeout=timeout,
                retries=retries,
                baudrate=configs.get_int("baudrate"),
                bytesize=configs.get_int("bytesize", default=8),
                stopbits=configs.get_int("stopbits", default=1),
                parity=configs.get("parity", default="N"),
                # handle_local_echo=False,
            )
        else:
            raise ConnectorError(self, f"Unknown modbus protocol type '{protocol}'")

    # noinspection PyUnresolvedReferences
    def is_connected(self) -> bool:
        return self.__client.connected

    def connect(self, resources: Resources) -> None:
        super().connect(resources)
        try:
            self._logger.info(f"Connecting to '{self.__client}'")
            self.__client.connect()
            self.__registers = {r.id: ModbusRegister.from_resource(r) for r in resources}

        except ModbusException as e:
            self._logger.warning(f"Error connecting to '{self.__client}': {e}")
            raise ConnectionError(self, e)
        except IOError as e:
            raise ConnectorError(self, e)

    def disconnect(self) -> None:
        super().disconnect()
        self.__client.close()

    # noinspection PyTypeChecker, PyShadowingBuiltins
    def read(self, resources: Resources) -> pd.DataFrame:
        timestamp = pd.Timestamp.now(tz.UTC).floor(freq="s")
        data = pd.DataFrame(index=[timestamp], columns=resources.ids)
        try:
            for device, device_resources in resources.groupby("device"):
                if device is None:
                    device = 1

                # TODO: Implement reading adjacent blocks of registers of same device ID
                for resource in device_resources:
                    try:
                        register = self.__registers[resource.id]
                        function = getattr(self.__client, f"read_{register.function}s")
                        result = function(register.address, count=register.length, slave=device)
                        if result.isError():
                            data.at[timestamp, resource.id] = ChannelState.UNKNOWN_ERROR
                            self._logger.warning(f"Error reading register '{resource.id}'")
                            continue

                        value = self.__client.convert_from_registers(
                            result.registers, register.type, word_order=self._endian
                        )
                        data.at[timestamp, resource.id] = value

                        self._logger.debug(f"Read {register.type} value of register {register.address}: {value}")

                    except ConfigurationError as e:
                        data.at[timestamp, resource.id] = ChannelState.ARGUMENT_SYNTAX_ERROR
                        self._logger.warning(f"Invalid register configuration for resource '{resource.id}': {e}")
                        continue
                    except KeyError:
                        data.at[timestamp, resource.id] = ChannelState.NOT_AVAILABLE
                        continue
            return data

        except ModbusException as e:
            raise ConnectionError(self, e)
        except IOError as e:
            raise ConnectorError(self, e)

    def write(self, data: pd.DataFrame) -> None:
        try:
            for device, device_channels in self.channels.groupby("device"):
                if device is None:
                    device = 1

                for channel in device_channels:
                    if channel.id not in data.columns:
                        continue
                    channel_data = data.loc[:, channel.id].dropna(axis="index", how="all")
                    if channel_data.empty:
                        continue
                    register = self.__registers[channel.id]
                    try:
                        values = self.__client.convert_to_registers(
                            channel_data.iloc[-1], register.type, word_order=self._endian
                        )
                        self.__client.write_registers(register.address, values, slave=device)

                    except ConfigurationError as e:
                        self._logger.warning(f"Invalid register configuration for channel '{channel.id}': {e}")
                        continue

        except ModbusException as e:
            raise ConnectionError(self, e)
        except IOError as e:
            raise ConnectorError(self, e)
