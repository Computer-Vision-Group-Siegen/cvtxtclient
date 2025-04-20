from pydantic import BaseModel
from typing import Optional

class Servomotor(BaseModel):
    """Represents a servomotor output."""
    enabled: Optional[bool] = None
    """Indicates if the servomotor is enabled."""
    name: Optional[str] = None
    """Name of the servomotor."""
    value: int
    """The target angle or position of the servomotor."""