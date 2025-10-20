"""Main client for Manhattan T4/T4R TV Box control."""

import asyncio
from enum import Enum
from typing import Optional
import aiohttp
import json

from .exceptions import ManhattanError, ManhattanConnectionError, ManhattanTimeoutError
from .keys import KeyCode, KeyEventType


class ManhattanModel(Enum):
    """Manhattan TV Box models."""
    T4 = "Manhattan T4"
    T4R = "Manhattan T4R"
    UNKNOWN = "Unknown"


class ManhattanRemote:
    """Async client for controlling Manhattan T4/T4R TV Box via HTTP."""

    def __init__(
            self,
            host: str,
            port: int = 80,
            timeout: int = 5,
            session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Initialize Manhattan Remote client.

        Args:
            host: IP address or hostname of the TV box
            port: HTTP port (default: 80)
            timeout: Request timeout in seconds (default: 5)
            session: Optional aiohttp session to reuse
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self._session = session
        self._own_session = session is None
        self._model: Optional[ManhattanModel] = None

    @property
    def base_url(self) -> str:
        """Get base URL for the TV box."""
        return f"http://{self.host}:{self.port}"

    async def __aenter__(self):
        """Async context manager entry."""
        if self._own_session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._own_session and self._session:
            await self._session.close()

    async def _request(self, endpoint: str) -> str:
        """
        Make HTTP request to the TV box.

        Args:
            endpoint: API endpoint path

        Returns:
            JSON response as dict

        Raises:
            ManhattanConnectionError: Connection failed
            ManhattanTimeoutError: Request timed out
            ManhattanError: Other errors
        """
        if not self._session:
            self._session = aiohttp.ClientSession()
            self._own_session = True

        url = f"{self.base_url}{endpoint}"

        try:
            async with self._session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response.raise_for_status()
                return await response.text()
        except asyncio.TimeoutError as e:
            raise ManhattanTimeoutError(f"Request to {url} timed out") from e
        except aiohttp.ClientError as e:
            raise ManhattanConnectionError(f"Connection error: {e}") from e
        except Exception as e:
            raise ManhattanError(f"Unexpected error: {e}") from e

    async def check_alive(self) -> bool:
        """
        Check if TV box is alive and web remote is enabled.

        Returns:
            True if alive, False if disabled
        """
        try:
            response = await self._request("/aliveStatus")
            response_json = json.loads(response)
            return response_json.get("aliveStatus") == "alive"
        except ManhattanError:
            return False

    async def get_model(self) -> ManhattanModel:
        """
        Get the TV box model.

        Returns:
            ManhattanModel enum value

        Raises:
            ManhattanError: If request fails
        """
        response = await self._request("/productModel")
        response_json = json.loads(response)
        model_str = response_json.get("productModel", "")

        if model_str == "Manhattan T4":
            self._model = ManhattanModel.T4
        elif model_str == "Manhattan T4R":
            self._model = ManhattanModel.T4R
        else:
            self._model = ManhattanModel.UNKNOWN

        return self._model

    async def send_key(
            self,
            key_code: KeyCode,
            event_type: KeyEventType = KeyEventType.CLICK
    ) -> None:
        """
        Send a key event to the TV box.

        Args:
            key_code: Key code to send
            event_type: Type of key event (default: CLICK)

        Raises:
            ManhattanError: If request fails
        """
        endpoint = f"/webKeyEvent?code={key_code.value}&keyeventType={event_type.value}"
        await self._request(endpoint)

    async def press_and_hold(
            self,
            key_code: KeyCode,
            duration: float = 0.5,
            repeat_interval: float = 0.1
    ) -> None:
        """
        Press and hold a key for a duration.

        Args:
            key_code: Key code to hold
            duration: How long to hold in seconds
            repeat_interval: Interval between repeat events in seconds
        """
        # Send key down
        await self.send_key(key_code, KeyEventType.KEY_DOWN)

        # Send repeats
        elapsed = 0.0
        while elapsed < duration:
            await asyncio.sleep(repeat_interval)
            elapsed += repeat_interval
            await self.send_key(key_code, KeyEventType.KEY_REPEAT)

        # Send key up
        await self.send_key(key_code, KeyEventType.KEY_UP)

    # Convenience methods for common actions
    async def power(self):
        """Toggle power."""
        await self.send_key(KeyCode.POWER)

    async def mute(self):
        """Toggle mute."""
        await self.send_key(KeyCode.MUTE)

    async def volume_up(self):
        """Increase volume."""
        await self.send_key(KeyCode.VOL_PLUS)

    async def volume_down(self):
        """Decrease volume."""
        await self.send_key(KeyCode.VOL_MINUS)

    async def channel_up(self):
        """Next channel."""
        await self.send_key(KeyCode.CH_PLUS)

    async def channel_down(self):
        """Previous channel."""
        await self.send_key(KeyCode.CH_MINUS)

    async def ok(self):
        """Press OK/Select."""
        await self.send_key(KeyCode.OK)

    async def back(self):
        """Press Back."""
        await self.send_key(KeyCode.BACK)

    async def home(self):
        """Press Home."""
        await self.send_key(KeyCode.HOME)

    async def up(self):
        """Navigate up."""
        await self.send_key(KeyCode.UP)

    async def down(self):
        """Navigate down."""
        await self.send_key(KeyCode.DOWN)

    async def left(self):
        """Navigate left."""
        await self.send_key(KeyCode.LEFT)

    async def right(self):
        """Navigate right."""
        await self.send_key(KeyCode.RIGHT)

    async def play_pause(self):
        """Toggle play/pause."""
        await self.send_key(KeyCode.PLAY_PAUSE)

    async def stop(self):
        """Stop playback."""
        await self.send_key(KeyCode.STOP)

    async def fast_forward(self):
        """Fast forward."""
        await self.send_key(KeyCode.FF)

    async def rewind(self):
        """Rewind."""
        await self.send_key(KeyCode.FB)

    async def guide(self):
        """Open guide."""
        await self.send_key(KeyCode.GUIDE)

    async def info(self):
        """Show info."""
        await self.send_key(KeyCode.INFO)

    async def exit(self):
        """Exit current screen."""
        await self.send_key(KeyCode.EXIT)

    async def number(self, digit: int):
        """
        Press a number key (0-9).

        Args:
            digit: Number to press (0-9)

        Raises:
            ValueError: If digit is not 0-9
        """
        if not 0 <= digit <= 9:
            raise ValueError("Digit must be between 0 and 9")

        key_map = {
            0: KeyCode.NUM_0,
            1: KeyCode.NUM_1,
            2: KeyCode.NUM_2,
            3: KeyCode.NUM_3,
            4: KeyCode.NUM_4,
            5: KeyCode.NUM_5,
            6: KeyCode.NUM_6,
            7: KeyCode.NUM_7,
            8: KeyCode.NUM_8,
            9: KeyCode.NUM_9,
        }
        await self.send_key(key_map[digit])

    async def channel(self, channel_number: int):
        """
        Change to a specific channel by sending digits.

        Args:
            channel_number: Channel number to switch to
        """
        for digit in str(channel_number):
            await self.number(int(digit))
            await asyncio.sleep(0.1)

    async def red(self):
        """Press red color button."""
        await self.send_key(KeyCode.RED)

    async def green(self):
        """Press green color button."""
        await self.send_key(KeyCode.GREEN)

    async def yellow(self):
        """Press yellow color button."""
        await self.send_key(KeyCode.YELLOW)

    async def blue(self):
        """Press blue color button."""
        await self.send_key(KeyCode.BLUE)