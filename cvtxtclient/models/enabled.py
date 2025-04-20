from pydantic import BaseModel

class Enabled(BaseModel):
    """Represents a boolean 'enabled' state."""
    enabled: bool
    """The enabled state."""