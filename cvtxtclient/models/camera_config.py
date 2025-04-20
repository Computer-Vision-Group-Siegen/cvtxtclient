from pydantic import BaseModel
from typing import Optional

class CameraConfig(BaseModel):
    """Configuration for the controller's camera."""
    debug: bool = False
    """Enable debug mode for the camera."""
    fps: int = 30
    """Frames per second for the camera stream."""
    height: int = 480
    """Height of the camera image."""
    rotate: bool = False
    """Rotate the camera image."""
    width: int = 640
    """Width of the camera image."""