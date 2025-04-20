from pydantic import BaseModel
from typing import List, Optional

class Output(BaseModel):
    """Represents a generic output device."""
    enabled: Optional[bool] = None
    """Indicates if the output is enabled."""
    name: Optional[str] = None
    """Name of the output."""
    values: List[int]
    """List of output values."""