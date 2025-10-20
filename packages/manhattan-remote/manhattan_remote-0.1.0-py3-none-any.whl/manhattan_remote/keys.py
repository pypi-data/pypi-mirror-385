"""Key codes and event types for Manhattan remote control."""

from enum import IntEnum


class KeyEventType(IntEnum):
    """Key event types based on web interface implementation."""
    KEY_UP = 1  # Key released
    KEY_REPEAT = 2  # Key held (repeating)
    CLICK = 3  # Single click (not used in web interface)
    KEY_DOWN = 4  # Key pressed


class KeyCode(IntEnum):
    """Key codes for Manhattan T4/T4R remote control."""

    # Power and mute
    MUTE = 1
    POWER = 2

    # Number keys
    NUM_1 = 3
    NUM_2 = 4
    NUM_3 = 5
    NUM_4 = 6
    NUM_5 = 7
    NUM_6 = 8
    NUM_7 = 9
    NUM_8 = 10
    NUM_9 = 11
    NUM_0 = 13

    # Navigation
    INFO = 16
    VOL_PLUS = 19
    HOME = 20
    CH_PLUS = 21
    VOL_MINUS = 22
    CH_MINUS = 24
    ZOOM = 25
    BACK = 28
    UP = 29
    LEFT = 30
    OK = 31
    RIGHT = 32
    GUIDE = 33
    DOWN = 34
    EXIT = 35

    # Color buttons
    RED = 36
    GREEN = 37
    YELLOW = 38
    BLUE = 39

    # T4R specific - Record button
    REC = 40

    # Playback controls
    STOP = 42
    FB = 44  # Fast backward/rewind
    FF = 45  # Fast forward

    # Other controls
    SWAP = 56
    AD = 66  # Audio description

    # T4R specific - RC/ES button
    RCES = 67

    # Media and search
    PLAY_PAUSE = 75
    SEARCH = 76

    # T4 specific buttons
    FEATURED = 77  # T4 only
    SETTINGS = 78  # T4 only


class T4Keys:
    """Keys specific to Manhattan T4 model."""
    FEATURED = KeyCode.FEATURED
    SETTINGS = KeyCode.SETTINGS


class T4RKeys:
    """Keys specific to Manhattan T4R model."""
    REC = KeyCode.REC
    RCES = KeyCode.RCES