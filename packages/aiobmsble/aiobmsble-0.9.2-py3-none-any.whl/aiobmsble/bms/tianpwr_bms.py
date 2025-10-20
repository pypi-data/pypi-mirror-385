"""Module to support TianPwr BMS.

Project: aiobmsble, https://pypi.org/p/aiobmsble/
License: Apache-2.0, http://www.apache.org/licenses/
"""

from typing import Final

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.uuids import normalize_uuid_str

from aiobmsble import BMSDp, BMSInfo, BMSSample, BMSValue, MatcherPattern
from aiobmsble.basebms import BaseBMS, barr2str


class BMS(BaseBMS):
    """TianPwr BMS implementation."""

    INFO: BMSInfo = {"default_manufacturer": "TianPwr", "default_model": "smart BMS"}
    _HEAD: Final[bytes] = b"\x55"
    _TAIL: Final[bytes] = b"\xaa"
    _RDCMD: Final[bytes] = b"\x04"
    _MAX_CELLS: Final[int] = 16
    _MAX_TEMP: Final[int] = 6
    _MIN_LEN: Final[int] = 4
    _DEF_LEN: Final[int] = 20
    _FIELDS: Final[tuple[BMSDp, ...]] = (
        BMSDp("battery_level", 3, 2, False, lambda x: x, 0x83),
        BMSDp("voltage", 5, 2, False, lambda x: x / 100, 0x83),
        BMSDp("current", 13, 2, True, lambda x: x / 100, 0x83),
        BMSDp("problem_code", 11, 8, False, lambda x: x, 0x84),
        BMSDp("cell_count", 3, 1, False, lambda x: x, 0x84),
        BMSDp("temp_sensors", 4, 1, False, lambda x: x, 0x84),
        BMSDp("design_capacity", 5, 2, False, lambda x: x // 100, 0x84),
        BMSDp("cycle_charge", 7, 2, False, lambda x: x / 100, 0x84),
        BMSDp("cycles", 9, 2, False, lambda x: x, 0x84),
    )
    _CMDS: Final[set[int]] = set({field.idx for field in _FIELDS}) | set({0x87})

    def __init__(self, ble_device: BLEDevice, keep_alive: bool = True) -> None:
        """Initialize BMS."""
        super().__init__(ble_device, keep_alive)
        self._data_final: dict[int, bytearray] = {}

    @staticmethod
    def matcher_dict_list() -> list[MatcherPattern]:
        """Provide BluetoothMatcher definition."""
        return [{"local_name": "TP_*", "connectable": True}]

    @staticmethod
    def uuid_services() -> list[str]:
        """Return list of 128-bit UUIDs of services required by BMS."""
        return [normalize_uuid_str("ff00")]

    @staticmethod
    def uuid_rx() -> str:
        """Return 16-bit UUID of characteristic that provides notification/read property."""
        return "ff01"

    @staticmethod
    def uuid_tx() -> str:
        """Return 16-bit UUID of characteristic that provides write property."""
        return "ff02"

    async def _fetch_device_info(self) -> BMSInfo:
        """Fetch the device information via BLE."""
        for cmd in (0x81, 0x82):
            await self._await_reply(BMS._cmd(cmd))
        return {
            "sw_version": barr2str(self._data_final[0x81][3:-1]),
            "hw_version": barr2str(self._data_final[0x82][3:-1]),
        }

    @staticmethod
    def _calc_values() -> frozenset[BMSValue]:
        return frozenset(
            {
                "battery_charging",
                "cycle_capacity",
                "delta_voltage",
                "power",
                "temperature",
            }
        )  # calculate further values from BMS provided set ones

    def _notification_handler(
        self, _sender: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        """Handle the RX characteristics notify event (new data arrives)."""
        self._log.debug("RX BLE data: %s", data)

        # verify that data is long enough
        if len(data) != BMS._DEF_LEN:
            self._log.debug("incorrect frame length")
            return

        if not data.startswith(BMS._HEAD):
            self._log.debug("incorrect SOF.")
            return

        if not data.endswith(BMS._TAIL):
            self._log.debug("incorrect EOF.")
            return

        self._data_final[data[2]] = data.copy()
        self._data_event.set()

    @staticmethod
    def _cmd(addr: int) -> bytes:
        """Assemble a TianPwr BMS command."""
        return BMS._HEAD + BMS._RDCMD + addr.to_bytes(1) + BMS._TAIL

    async def _async_update(self) -> BMSSample:
        """Update battery status information."""

        self._data_final.clear()
        for cmd in BMS._CMDS:
            await self._await_reply(BMS._cmd(cmd))

        result: BMSSample = BMS._decode_data(BMS._FIELDS, self._data_final)

        for cmd in range(
            0x88, 0x89 + min(result.get("cell_count", 0), BMS._MAX_CELLS) // 8
        ):
            await self._await_reply(BMS._cmd(cmd))
            result["cell_voltages"] = result.setdefault(
                "cell_voltages", []
            ) + BMS._cell_voltages(
                self._data_final.get(cmd, bytearray()), cells=8, start=3
            )

        if {0x83, 0x87}.issubset(self._data_final):
            result["temp_values"] = [
                int.from_bytes(
                    self._data_final[0x83][idx : idx + 2], byteorder="big", signed=True
                )
                / 10
                for idx in (7, 11)  # take ambient and mosfet temperature
            ] + BMS._temp_values(
                self._data_final.get(0x87, bytearray()),
                values=min(BMS._MAX_TEMP, result.get("temp_sensors", 0)),
                start=3,
                divider=10,
            )

        return result
