from bleak import BleakClient, BleakScanner
import asyncio
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class SqueggData:
    """Data class for the Squegg device"""
    strength: float
    is_squeezing: bool
    battery_charge: int


class Squegg:
    """Class for the Squegg (squeeze egg) BLE device"""

    _squegg_uuids = {
        "Service UUID": "8e400001-f315-4f60-9fb8-838830daea50",
        "Characteristic UUID": "0000ffb0-0000-1000-8000-00805f9b34fb",
        "Characteristic UUID notify": "0000ffb2-0000-1000-8000-00805f9b34fb",
        "Write without response, Characteristic": "0000ffb1-0000-1000-8000-00805f9b34fb",
    }
    SQUEGG_SERVICE_UUID = _squegg_uuids["Service UUID"]
    CHAR_UUID = _squegg_uuids["Characteristic UUID"]
    CHAR_UUID_NOTIFY = _squegg_uuids["Characteristic UUID notify"]
    CHAR_UUID_WRITE_WITHOUT_RESPONSE = _squegg_uuids["Write without response, Characteristic"]

    def __init__(self, target_name: str = "Squegg_1"):
        """Initializes the Squegg BLE device"""
        self.TARGET_NAME = target_name
        self.client: Optional[BleakClient] = None
        self.notifications_started = False
        self.connected = False

    async def scan_and_connect(self, timeout: float = 20.0) -> bool:
        """Scan and connect to the device"""
        if self.client and self.client.is_connected:
            return True

        print("Scanning for Squegg devices...")
        devices = await BleakScanner.discover(timeout=timeout)
        for d in devices:
            if d.name and (d.name == self.TARGET_NAME or d.name.startswith(self.TARGET_NAME)):
                print(f'Found "{d.name}" @ {d.address}')
                self.client = BleakClient(d.address)
                break

        if not self.client:
            print("No Squegg device found.")
            return False

        await self.client.connect()
        if self.client.is_connected:
            print(f"Connected to {self.TARGET_NAME} @ {self.client.address}")
            return True
        else:
            print("Connection failed.")
            return False

    def data_view_to_array(self, data: bytearray) -> List[int]:
        """Turns data array to a list of ints"""
        return list(data)

    def _from_char_codes(self, codes: List[int]) -> List[str]:
        """Deciphers character codes"""
        return [chr(c) for c in codes]

    def _parse_battery_charge(self, raw: str) -> int:
        """Parses battery charge percentage"""
        return 10 * (int(raw) + 1)

    def _parse_squeezing(self, raw: str) -> bool:
        """Parses if device is being squeezed"""
        return bool(int(raw))

    def _parse_strength(self, chars: List[str]) -> float:
        """Parses squeeze strength"""
        raw = "".join(chars)
        cleaned = raw.replace('\x00', '').strip()
        return round(float(cleaned), 1)

    def parse_squegg(self, char_codes: List[int]) -> SqueggData:
        """Parses raw Squegg data into SqueggData"""
        vals = self._from_char_codes(char_codes)
        if len(vals) < 4:
            raise ValueError("Unexpected payload length")

        vals.pop(0)  # discard unknown
        raw_batt = vals.pop(0)
        raw_squeeze = vals.pop(0)
        strength = self._parse_strength(vals)
        is_squeeze = self._parse_squeezing(raw_squeeze)
        batt_pct = self._parse_battery_charge(raw_batt)

        return SqueggData(strength=strength,
                          is_squeezing=is_squeeze,
                          battery_charge=batt_pct)

    def notification_handler(self, sender: int, data: bytearray):
        """Handles notifications from device"""
        codes = self.data_view_to_array(data)
        parsed = self.parse_squegg(codes)
        print(f"Strength: {parsed.strength:.1f}, "
              f"Squeezing: {parsed.is_squeezing}, "
              f"Battery: {parsed.battery_charge}%")

    async def start_notifications(self):
        """Start reading notifications"""
        if not self.client or not self.client.is_connected:
            raise RuntimeError("Not connected")
        if not self.notifications_started:
            await self.client.start_notify(self.CHAR_UUID_NOTIFY,
                                           self.notification_handler)
            self.notifications_started = True

    async def run(self, duration: int = 3):
        """Run loop to keep connection alive"""
        if await self.scan_and_connect():
            self.connected = True
            await self.start_notifications()
            try:
                while True:
                    await asyncio.sleep(duration)
            finally:
                print("Disconnecting from Squegg...")
                if self.notifications_started:
                    await self.client.stop_notify(self.CHAR_UUID_NOTIFY)
                await self.client.disconnect()
                print("Disconnected.")

    async def end_connection(self):
        """Disconnect from device"""
        if self.client and self.client.is_connected:
            print("Disconnecting...")
            if self.notifications_started:
                await self.client.stop_notify(self.CHAR_UUID_NOTIFY)
            await self.client.disconnect()
            print("Disconnected.")
