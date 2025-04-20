from pydantic import BaseModel
from typing import Optional
from .rectangle import Rectangle

class LineDetector(BaseModel):
    """Configuration for detecting lines in an image."""
    area: Optional[Rectangle] = None
    """The rectangular area to search within."""
    end_range_value: Optional[int] = 100
    """End of the grayscale range to consider."""
    invert: Optional[bool] = None
    """Invert the grayscale image for detection."""
    max_line_width: Optional[int] = 20
    """Maximum width of a detected line."""
    min_line_width: Optional[int] = 5
    """Minimum width of a detected line."""
    name: Optional[str] = None
    """Name of the line detector."""
    number_of_lines: Optional[int] = 1
    """Number of lines to detect."""
    start_range_value: Optional[int] = -100
    """Start of the grayscale range to consider."""