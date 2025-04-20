from pydantic import BaseModel
from typing import Optional

class ProgramLocation(BaseModel):
    """Represents a location in the program."""
    current_frame: Optional[bool] = False
    """Indicates if this is the current frame."""
    filename: Optional[str] = None
    """Filename of the current location."""
    line: Optional[int] = None
    """Line number of the current location."""
    methodname: Optional[str] = None
    """Name of the current method."""