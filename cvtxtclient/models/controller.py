from pydantic import BaseModel
from typing import Optional

class Controller(BaseModel):
    """Represents information about a controller."""
    api_version: Optional[str] = None
    """API version of the controller."""
    controller_lib_version: Optional[str] = None
    """Version of the controller library."""
    firmware: Optional[str] = None
    """Firmware version of the controller."""
    name: Optional[str] = None
    """Name of the controller."""
    serial_number: Optional[str] = None
    """Serial number of the controller."""
    version: Optional[str] = None
    """Version of the controller."""