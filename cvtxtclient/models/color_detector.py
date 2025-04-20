from pydantic import BaseModel
from typing import Optional
from .rectangle import Rectangle

class ColorDetector(BaseModel):
    """Configuration for detecting colors in an image."""
    area: Optional[Rectangle] = None
    """The rectangular area to search within."""
    contrast: Optional[float] = 1.0
    """Contrast adjustment for color detection."""
    name: Optional[str] = None
    """Name of the color detector."""