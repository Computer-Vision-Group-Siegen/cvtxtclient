from pydantic import BaseModel
from typing import Optional

class Counter(BaseModel):
    """Represents a counter on the controller."""
    count: Optional[int] = None
    """Current count value."""
    digital: Optional[bool] = None
    """Indicates if the counter is digital."""
    enabled: Optional[bool] = None
    """Indicates if the counter is enabled."""
    name: Optional[str] = None
    """Name of the counter."""
    state: Optional[int] = None
    """Current state of the counter."""