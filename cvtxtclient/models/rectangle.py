from pydantic import BaseModel
from typing import Optional

class Rectangle(BaseModel):
    """Represents a rectangular area."""
    height: Optional[int] = None
    """Height of the rectangle."""
    width: Optional[int] = None
    """Width of the rectangle."""
    x: Optional[int] = None
    """X-coordinate of the top-left corner."""
    y: Optional[int] = None
    """Y-coordinate of the top-left corner."""