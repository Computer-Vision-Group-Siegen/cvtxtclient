from pydantic import BaseModel
from typing import List, Optional
from .rectangle import Rectangle

class BallDetector(BaseModel):
    """Configuration for detecting balls in an image."""
    area: Optional[Rectangle] = None
    """The rectangular area to search within."""
    end_range_value: Optional[int] = 100
    """End of the HSV range to consider."""
    max_ball_diameter: Optional[int] = 20
    """Maximum diameter of a detected ball."""
    min_ball_diameter: Optional[int] = 5
    """Minimum diameter of a detected ball."""
    name: Optional[str] = None
    """Name of the ball detector."""
    rgb: Optional[List[int]] = None
    """Target RGB color for ball detection."""
    start_range_value: Optional[int] = -100
    """Start of the HSV range to consider."""
    tolerance: Optional[float] = 1.0
    """Tolerance for color matching."""