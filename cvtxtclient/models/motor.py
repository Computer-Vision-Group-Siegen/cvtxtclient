from pydantic import BaseModel
from .output import Output
from enum import Enum
from typing import Optional

class Direction(str, Enum):
    """Possible directions for a motor."""
    CW = "CW"
    """Clockwise direction."""
    CCW = "CCW"
    """Counter-clockwise direction."""

class Motor(Output):
    """Represents a motor output."""

    direction: Optional[Direction] = None
    """Direction of the motor (CW or CCW)."""