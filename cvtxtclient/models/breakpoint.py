from pydantic import BaseModel
from typing import Optional

class Breakpoint(BaseModel):
    """Represents a breakpoint in the debugger."""
    enabled: Optional[bool] = None
    """Indicates if the breakpoint is enabled."""
    filename: str
    """Filename where the breakpoint is located."""
    id: Optional[int] = None
    """ID of the breakpoint."""
    line: int
    """Line number where the breakpoint is located."""