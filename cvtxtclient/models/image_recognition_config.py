from pydantic import BaseModel
from typing import List, Optional
from .ball_detector import BallDetector
from .rectangle import Rectangle
from .color_detector import ColorDetector
from .line_detector import LineDetector
from .motion_detector import MotionDetector

class ImageRecognitionConfig(BaseModel):
    """Configuration for image recognition on the camera."""
    ball_detectors: Optional[List[BallDetector]] = None
    """List of ball detectors."""
    blocked_areas: Optional[List[Rectangle]] = None
    """List of blocked rectangular areas in the image."""
    color_detectors: Optional[List[ColorDetector]] = None
    """List of color detectors."""
    line_detectors: Optional[List[LineDetector]] = None
    """List of line detectors."""
    motion_detectors: Optional[List[MotionDetector]] = None
    """List of motion detectors."""