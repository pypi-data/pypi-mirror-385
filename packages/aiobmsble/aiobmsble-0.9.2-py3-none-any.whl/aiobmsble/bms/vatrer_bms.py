"""Module to support Vatrer BMS.

Project: aiobmsble, https://pypi.org/p/aiobmsble/
License: Apache-2.0, http://www.apache.org/licenses/
"""

from functools import cache
from typing import Final

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice

from aiobmsble import BMSSample, BMSValue, MatcherPattern
from aiobmsble.basebms import BaseBMS, BMSDp, BMSInfo, crc_modbus


class BMS(BaseBMS):
    """Vatrer BMS implementation."""

    INFO: BMSInfo = {"default_manufacturer": "Vatrer", "default_model": "smart BMS"}
    _HEAD: Final[bytes] = b"\x02\x03"  # beginning of frame
    _FRAME_LEN: Final[int] = 5  # head + len + CRC
    _MAX_CELLS: Final[int] = 0x1F
    _MAX_TEMP: Final[int] = 6
    _FIELDS: Final[tuple[BMSDp, ...]] = (
        BMSDp("voltage", 3, 2, False, lambda x: x / 100, 0x28),
        BMSDp("current", 5, 4, True, lambda x: x / 100, 0x28),
        BMSDp("battery_level", 9, 2, False, idx=0x28),
        BMSDp("cycle_charge", 11, 2, False, lambda x: x / 100, 0x28),
        BMSDp("cell_count", 3, 2, False, lambda x: min(x, BMS._MAX_CELLS), 0x3E),
        BMSDp("temp_sensors", 3, 2, False, lambda x: min(x, BMS._MAX_TEMP), 0x24),
        BMSDp("cycles", 15, 2, False, lambda x: x, 0x28),
        BMSDp("delta_voltage", 29, 2, False, lambda x: x / 1000, 0x28),
        BMSDp("problem", 17, 15, False, lambda x: (x != 0), 0x24),
    )
    _RESPS: Final[set[int]] = {field.idx for field in _FIELDS}
    _CMDS: Final[tuple[tuple[int, int], ...]] = (
        (0x0, 0x14),
        (0x34, 0x12),
        (0x15, 0x1F),
    )

    def __init__(self, ble_device: BLEDevice, keep_alive: bool = True) -> None:
        """Initialize BMS."""
        super().__init__(ble_device, keep_alive)
        self._data_final: dict[int, bytearray] = {}

    @staticmethod
    def matcher_dict_list() -> list[MatcherPattern]:
        """Provide BluetoothMatcher definition."""
        return [
            {  # name is likely YYMMDDVVVAAAAxx (date, V, Ah)
                "local_name": "[2-9]???[0-3]?512??00??",
                "service_uuid": BMS.uuid_services()[0],
                "connectable": True,
            }
        ]

    # async def _fetch_device_info(self) -> BMSInfo: use default

    @staticmethod
    def uuid_services() -> list[str]:
        """Return list of 128-bit UUIDs of services required by BMS."""
        return ["6e400001-b5a3-f393-e0a9-e50e24dcca9e"]

    @staticmethod
    def uuid_rx() -> str:
        """Return 16-bit UUID of characteristic that provides notification/read property."""
        return "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

    @staticmethod
    def uuid_tx() -> str:
        """Return 16-bit UUID of characteristic that provides write property."""
        return "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

    @staticmethod
    def _calc_values() -> frozenset[BMSValue]:
        return frozenset(
            {"power", "battery_charging", "temperature", "runtime", "cycle_capacity"}
        )  # calculate further values from BMS provided set ones

    def _notification_handler(
        self, _sender: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        """Handle the RX characteristics notify event (new data arrives)."""
        self._log.debug("RX BLE data: %s", data)

        if not data.startswith(BMS._HEAD):
            self._log.debug("incorrect SOF")
            return

        if len(data) < BMS._FRAME_LEN or len(data) != data[2] + BMS._FRAME_LEN:
            self._log.debug("incorrect frame length")
            return

        if (crc := crc_modbus(data[:-2])) != int.from_bytes(
            data[-2:], byteorder="little"
        ):
            self._log.debug(
                "invalid checksum 0x%X != 0x%X",
                int.from_bytes(data[-2:], "little"),
                crc,
            )
            return

        self._data_final[data[2]] = data.copy()
        self._data_event.set()

    @staticmethod
    @cache
    def _cmd(addr: int, words: int) -> bytes:
        """Assemble a Vatrer BMS command."""
        frame = (
            bytearray(BMS._HEAD)
            + addr.to_bytes(2, byteorder="big")
            + words.to_bytes(2, byteorder="big")
        )
        frame.extend(crc_modbus(frame).to_bytes(2, "little"))
        return bytes(frame)

    async def _async_update(self) -> BMSSample:
        """Update battery status information."""
        for addr, length in BMS._CMDS:
            await self._await_reply(BMS._cmd(addr, length))
        if not BMS._RESPS.issubset(set(self._data_final.keys())):
            self._log.debug("Incomplete data set %s", self._data_final.keys())
            raise TimeoutError("BMS data incomplete.")

        result = BMS._decode_data(BMS._FIELDS, self._data_final)
        result["cell_voltages"] = BMS._cell_voltages(
            self._data_final[0x3E], cells=result["cell_count"], start=5
        )
        result["temp_values"] = BMS._temp_values(
            self._data_final[0x24], values=result["temp_sensors"] + 2, start=5
        )  # MOS sensor is last (pos 6 of 4)

        return result
