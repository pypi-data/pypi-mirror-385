"""Module to support Daly smart BMS.

Project: aiobmsble, https://pypi.org/p/aiobmsble/
License: Apache-2.0, http://www.apache.org/licenses/
"""

from typing import Final

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.uuids import normalize_uuid_str

from aiobmsble import BMSDp, BMSInfo, BMSSample, BMSValue, MatcherPattern
from aiobmsble.basebms import BaseBMS, barr2str, crc_modbus


class BMS(BaseBMS):
    """Daly smart BMS class implementation."""

    INFO: BMSInfo = {"default_manufacturer": "Daly", "default_model": "smart BMS"}
    HEAD_READ: Final[bytes] = b"\xd2\x03"
    CMD_INFO: Final[bytes] = b"\x00\x00\x00\x3e\xd7\xb9"
    MOS_INFO: Final[bytes] = b"\x00\x3e\x00\x09\xf7\xa3"
    VER_INFO: Final[bytes] = b"\x00\xa9\x00\x20\x87\x91"
    HEAD_LEN: Final[int] = 3
    CRC_LEN: Final[int] = 2
    MAX_CELLS: Final[int] = 32
    MAX_TEMP: Final[int] = 8
    INFO_LEN: Final[int] = 84 + HEAD_LEN + CRC_LEN + MAX_CELLS + MAX_TEMP
    MOS_TEMP_POS: Final[int] = HEAD_LEN + 8
    MOS_NOT_AVAILABLE: Final[tuple[str]] = ("DL-FB4C2E0",)
    _FIELDS: Final[tuple[BMSDp, ...]] = (
        BMSDp("voltage", 80, 2, False, lambda x: x / 10),
        BMSDp("current", 82, 2, False, lambda x: (x - 30000) / 10),
        BMSDp("battery_level", 84, 2, False, lambda x: x / 10),
        BMSDp("cycle_charge", 96, 2, False, lambda x: x / 10),
        BMSDp("cell_count", 98, 2, False, lambda x: min(x, BMS.MAX_CELLS)),
        BMSDp("temp_sensors", 100, 2, False, lambda x: min(x, BMS.MAX_TEMP)),
        BMSDp("cycles", 102, 2, False, lambda x: x),
        BMSDp("delta_voltage", 112, 2, False, lambda x: x / 1000),
        BMSDp("problem_code", 116, 8, False, lambda x: x % 2**64),
    )

    def __init__(self, ble_device: BLEDevice, keep_alive: bool = True) -> None:
        """Intialize private BMS members."""
        super().__init__(ble_device, keep_alive)

    @staticmethod
    def matcher_dict_list() -> list[MatcherPattern]:
        """Provide BluetoothMatcher definition."""
        return [
            MatcherPattern(
                local_name="DL-*",
                service_uuid=BMS.uuid_services()[0],
                connectable=True,
            )
        ] + [
            MatcherPattern(
                manufacturer_id=m_id,
                connectable=True,
            )
            for m_id in (0x102, 0x104, 0x0302, 0x0303, 0x0402)
        ]

    @staticmethod
    def uuid_services() -> list[str]:
        """Return list of 128-bit UUIDs of services required by BMS."""
        return [normalize_uuid_str("fff0")]

    @staticmethod
    def uuid_rx() -> str:
        """Return 16-bit UUID of characteristic that provides notification/read property."""
        return "fff1"

    @staticmethod
    def uuid_tx() -> str:
        """Return 16-bit UUID of characteristic that provides write property."""
        return "fff2"

    async def _fetch_device_info(self) -> BMSInfo:
        """Fetch the device information via BLE."""
        await self._await_reply(BMS.HEAD_READ + BMS.VER_INFO)
        return {
            "sw_version": barr2str(self._data[3:19]),
            "hw_version": barr2str(self._data[19:35]),
            # "manuf.date": barr2str(self._data[35:51]),
        }

    @staticmethod
    def _calc_values() -> frozenset[BMSValue]:
        return frozenset(
            {
                "cycle_capacity",
                "power",
                "battery_charging",
                "runtime",
                "temperature",
            }
        )

    def _notification_handler(
        self, _sender: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        self._log.debug("RX BLE data: %s", data)

        if (
            len(data) < BMS.HEAD_LEN
            or data[0:2] != BMS.HEAD_READ
            or data[2] + 1 != len(data) - len(BMS.HEAD_READ) - BMS.CRC_LEN
        ):
            self._log.debug("response data is invalid")
            return

        if (crc := crc_modbus(data[:-2])) != int.from_bytes(
            data[-2:], byteorder="little"
        ):
            self._log.debug(
                "invalid checksum 0x%X != 0x%X",
                int.from_bytes(data[-2:], byteorder="little"),
                crc,
            )
            self._data.clear()
            return

        self._data = data.copy()
        self._data_event.set()

    async def _async_update(self) -> BMSSample:
        """Update battery status information."""
        result: BMSSample = {}
        if (  # do not query devices that do not support MOS temperature, e.g. Bulltron
            not self.name.startswith(BMS.MOS_NOT_AVAILABLE)
        ):
            try:
                # request MOS temperature (possible outcome: response, empty response, no response)
                await self._await_reply(BMS.HEAD_READ + BMS.MOS_INFO)

                if sum(self._data[BMS.MOS_TEMP_POS :][:2]):
                    self._log.debug("MOS info: %s", self._data)
                    result["temp_values"] = [
                        int.from_bytes(
                            self._data[BMS.MOS_TEMP_POS :][:2],
                            byteorder="big",
                            signed=True,
                        )
                        - 40
                    ]
            except TimeoutError:
                self._log.debug("no MOS temperature available.")

        await self._await_reply(BMS.HEAD_READ + BMS.CMD_INFO)

        if len(self._data) != BMS.INFO_LEN:
            self._log.debug("incorrect frame length: %i", len(self._data))
            return {}

        result |= BMS._decode_data(BMS._FIELDS, self._data, offset=BMS.HEAD_LEN)

        # add temperature sensors
        result.setdefault("temp_values", []).extend(
            BMS._temp_values(
                self._data,
                values=result.get("temp_sensors", 0),
                start=64 + BMS.HEAD_LEN,
                offset=40,
            )
        )

        # get cell voltages
        result["cell_voltages"] = BMS._cell_voltages(
            self._data, cells=result.get("cell_count", 0), start=BMS.HEAD_LEN
        )

        return result
