"""
Controllers package for Pepper robot movement.

Modules:
- pepper_connection: Robot connection and initialization
- base_controller: Base movement (wheels)
- body_controller: Arms, head, hands control
- video_controller: Video feed display
"""

from .pepper_connection import PepperConnection
from .base_controller import BaseController
from .body_controller import BodyController
from .video_controller import VideoController

__all__ = [
    'PepperConnection',
    'BaseController',
    'BodyController',
    'VideoController'
]