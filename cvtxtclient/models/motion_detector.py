from pydantic import BaseModel
from typing import Optional
from .rectangle import Rectangle

class MotionDetector(BaseModel):
    """Configuration for detecting motion in an image."""
    area: Optional[Rectangle] = None
    """The rectangular area to search for motion within."""
    name: Optional[str] = None
    """Name of the motion detector."""
    tolerance: Optional[float] = 1.0
    """Tolerance for motion detection."""