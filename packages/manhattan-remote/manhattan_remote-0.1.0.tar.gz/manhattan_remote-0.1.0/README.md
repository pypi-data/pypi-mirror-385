# Manhattan Remote

Async Python library for controlling Manhattan T4 and T4R TV Boxes via their HTTP interface.

## Features

- **Async/await support** - Built with `aiohttp` for non-blocking I/O
- **Full remote control** - All remote buttons mapped and available
- **Model detection** - Automatically detects T4 vs T4R models
- **Press and hold** - Support for long-press actions
- **Type hints** - Full typing support for better IDE integration
- **Context manager** - Clean resource management with async context managers

## Installation

Using `uv`:

```bash
uv pip install manhattan-remote
```

Using `pip`:

```bash
pip install manhattan-remote
```

## Quick Start

```python
import asyncio
from manhattan_remote import ManhattanRemote

async def main():
    # Using context manager (recommended)
    async with ManhattanRemote("192.168.1.100") as remote:
        # Check if device is available
        if await remote.check_alive():
            print("TV Box is online!")
            
            # Get model
            model = await remote.get_model()
            print(f"Model: {model.value}")
            
            # Navigate and select
            await remote.up()
            await remote.right()
            await remote.ok()
            
            # Volume control
            await remote.volume_up()
            await remote.mute()
            
            # Change channel
            await remote.channel(105)

asyncio.run(main())
```

## Usage

### Basic Remote Control

```python
async with ManhattanRemote("192.168.1.100") as remote:
    # Navigation
    await remote.up()
    await remote.down()
    await remote.left()
    await remote.right()
    await remote.ok()
    await remote.back()
    
    # Home and menu
    await remote.home()
    await remote.guide()
    await remote.info()
    await remote.exit()
    
    # Volume and channels
    await remote.volume_up()
    await remote.volume_down()
    await remote.channel_up()
    await remote.channel_down()
    await remote.mute()
    
    # Playback
    await remote.play_pause()
    await remote.stop()
    await remote.fast_forward()
    await remote.rewind()
    
    # Color buttons
    await remote.red()
    await remote.green()
    await remote.yellow()
    await remote.blue()
    
    # Numbers
    await remote.number(5)
    await remote.channel(123)  # Changes to channel 123
```

### Advanced Features

```python
from manhattan_remote import ManhattanRemote, KeyCode, KeyEventType

async with ManhattanRemote("192.168.1.100", timeout=10) as remote:
    # Check connection
    is_alive = await remote.check_alive()
    
    # Detect model
    model = await remote.get_model()
    if model == ManhattanModel.T4:
        print("This is a T4 model")
    
    # Send raw key codes
    await remote.send_key(KeyCode.POWER)
    
    # Press and hold (e.g., for volume)
    await remote.press_and_hold(KeyCode.VOL_PLUS, duration=2.0)
    
    # Custom key event types
    await remote.send_key(KeyCode.OK, KeyEventType.KEY_DOWN)
    await asyncio.sleep(0.5)
    await remote.send_key(KeyCode.OK, KeyEventType.KEY_UP)
```

### Reusing aiohttp Session

```python
import aiohttp
from manhattan_remote import ManhattanRemote

async with aiohttp.ClientSession() as session:
    remote1 = ManhattanRemote("192.168.1.100", session=session)
    remote2 = ManhattanRemote("192.168.1.101", session=session)
    
    await remote1.power()
    await remote2.power()
```

## Key Codes

All remote control buttons are available as methods or via the `KeyCode` enum:

### Common Keys (T4 & T4R)
- Power, Mute
- Numbers 0-9
- Navigation (Up, Down, Left, Right, OK)
- Back, Home, Exit, Guide, Info
- Volume +/-, Channel +/-
- Play/Pause, Stop, Fast Forward, Rewind
- Color buttons (Red, Green, Yellow, Blue)
- Search, Swap, Zoom, AD (Audio Description)

### T4 Specific
- Settings
- Featured

### T4R Specific
- Rec (Record)
- RC/ES

## Configuration

The `ManhattanRemote` constructor accepts the following parameters:

- `host` (str): IP address or hostname of the TV box (required)
- `port` (int): HTTP port (default: 80)
- `timeout` (int): Request timeout in seconds (default: 5)
- `session` (aiohttp.ClientSession): Optional session to reuse

## Error Handling

```python
from manhattan_remote import (
    ManhattanRemote,
    ManhattanError,
    ManhattanConnectionError,
    ManhattanTimeoutError
)

async with ManhattanRemote("192.168.1.100") as remote:
    try:
        await remote.power()
    except ManhattanTimeoutError:
        print("Request timed out")
    except ManhattanConnectionError:
        print("Could not connect to TV box")
    except ManhattanError as e:
        print(f"Error: {e}")
```

## Requirements

- Python 3.8+
- aiohttp 3.8.0+

## Web Remote Setup

The web remote interface must be enabled on your Manhattan T4/T4R box:

1. Go to **Settings** → **Internet** → **Browsing Options**
2. Enable **Web Remote**

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Based on the Manhattan T4/T4R web remote control interface.