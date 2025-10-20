"""Module to support Felicity BMS.

Project: aiobmsble, https://pypi.org/p/aiobmsble/
License: Apache-2.0, http://www.apache.org/licenses/
"""

from collections.abc import Callable
from json import JSONDecodeError, loads
from typing import Any, Final

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.uuids import normalize_uuid_str

from aiobmsble import BMSInfo, BMSSample, BMSValue, MatcherPattern
from aiobmsble.basebms import BaseBMS


class BMS(BaseBMS):
    """Felicity BMS implementation."""

    INFO: BMSInfo = {
        "default_manufacturer": "Felicity Solar",
        "default_model": "LiFePo4 battery",
    }
    _HEAD: Final[bytes] = b"{"
    _TAIL: Final[bytes] = b"}"
    _CMD_PRE: Final[bytes] = b"wifilocalMonitor:"  # CMD prefix
    _CMD_BI: Final[bytes] = b"get dev basice infor"
    _CMD_DT: Final[bytes] = b"get Date"
    _CMD_RT: Final[bytes] = b"get dev real infor"
    _FIELDS: Final[list[tuple[BMSValue, str, Callable[[list], Any]]]] = [
        ("voltage", "Batt", lambda x: x[0][0] / 1000),
        ("current", "Batt", lambda x: x[1][0] / 10),
        (
            "cycle_charge",
            "BatsocList",
            lambda x: (int(x[0][0]) * int(x[0][2])) / 1e7,
        ),
        ("battery_level", "BatsocList", lambda x: x[0][0] / 100),
    ]

    def __init__(self, ble_device: BLEDevice, keep_alive: bool = True) -> None:
        """Initialize BMS."""
        super().__init__(ble_device, keep_alive)
        self._data_final: dict = {}

    @staticmethod
    def matcher_dict_list() -> list[MatcherPattern]:
        """Provide BluetoothMatcher definition."""
        return [
            {"local_name": pattern, "connectable": True} for pattern in ("F07*", "F10*")
        ]

    @staticmethod
    def uuid_services() -> list[str]:
        """Return list of 128-bit UUIDs of services required by BMS."""
        return [normalize_uuid_str("6e6f736a-4643-4d44-8fa9-0fafd005e455")]

    @staticmethod
    def uuid_rx() -> str:
        """Return 128-bit UUID of characteristic that provides notification/read property."""
        return "49535458-8341-43f4-a9d4-ec0e34729bb3"

    @staticmethod
    def uuid_tx() -> str:
        """Return 128-bit UUID of characteristic that provides write property."""
        return "49535258-184d-4bd9-bc61-20c647249616"

    async def _fetch_device_info(self) -> BMSInfo:
        """Fetch the device information via BLE."""
        await self._await_reply(BMS._CMD_PRE + BMS._CMD_BI)
        return {
            "fw_version": self._data_final.get("M1SwVer", []),
            "sw_version": self._data_final.get("version", []),
            "model_id": self._data_final.get("Type", []),
            "serial_number": self._data_final.get("DevSN", []),
        }

    @staticmethod
    def _calc_values() -> frozenset[BMSValue]:
        return frozenset(
            {
                "battery_charging",
                "cycle_capacity",
                "delta_voltage",
                "power",
                "runtime",
                "temperature",
            }
        )  # calculate further values from BMS provided set ones

    def _notification_handler(
        self, _sender: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        """Handle the RX characteristics notify event (new data arrives)."""

        if data.startswith(BMS._HEAD):
            self._data = bytearray()

        self._data += data
        self._log.debug(
            "RX BLE data (%s): %s", "start" if data == self._data else "cnt.", data
        )

        if not data.endswith(BMS._TAIL):
            return

        try:
            self._data_final = loads(self._data)
        except (JSONDecodeError, UnicodeDecodeError):
            self._log.debug("JSON decode error: %s", self._data)
            return

        if (ver := self._data_final.get("CommVer", 0)) != 1:
            self._log.debug("Unknown protocol version (%i)", ver)
            return

        self._data_event.set()

    @staticmethod
    def _conv_data(data: dict) -> BMSSample:
        result: BMSSample = {}
        for key, itm, func in BMS._FIELDS:
            result[key] = func(data.get(itm, []))
        return result

    @staticmethod
    def _conv_cells(data: dict) -> list[float]:
        return [(value / 1000) for value in data.get("BatcelList", [])[0]]

    @staticmethod
    def _conv_temp(data: dict) -> list[float]:
        return [
            (value / 10) for value in data.get("BtemList", [])[0] if value != 0x7FFF
        ]

    async def _async_update(self) -> BMSSample:
        """Update battery status information."""

        await self._await_reply(BMS._CMD_PRE + BMS._CMD_RT)

        return (
            BMS._conv_data(self._data_final)
            | {"temp_values": BMS._conv_temp(self._data_final)}
            | {"cell_voltages": BMS._conv_cells(self._data_final)}
            | {
                "problem_code": int(
                    self._data_final.get("Bwarn", 0) + self._data_final.get("Bfault", 0)
                )
            }
        )
