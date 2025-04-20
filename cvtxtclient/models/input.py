from pydantic import BaseModel
from enum import Enum
from typing import Optional

class InputDevice(str, Enum):
    """Enumeration of possible input devices."""
    MINI_SWITCH = "MINI_SWITCH"
    PHOTO_RESISTOR = "PHOTO_RESISTOR"
    ULTRASONIC_DISTANCE_METER = "ULTRASONIC_DISTANCE_METER"
    PHOTO_TRANSISTOR = "PHOTO_TRANSISTOR"
    COLOR_SENSOR = "COLOR_SENSOR"
    NTC_RESISTOR = "NTC_RESISTOR"
    TRAIL_FOLLOWER = "TRAIL_FOLLOWER"

class Input(BaseModel):
    """Represents an input device on the controller."""
    device: Optional[InputDevice] = None
    """Type of the input device."""
    enabled: Optional[bool] = None
    """Indicates if the input is enabled."""
    name: Optional[str] = None
    """Name of the input."""
    value: Optional[int] = None
    """Current value of the input."""