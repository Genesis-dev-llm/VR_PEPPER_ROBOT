"""
Pepper Robot Keyboard Test Controller
======================================
Modular keyboard control system for testing Pepper robot.

Package Structure:
- main.py: Entry point
- config.py: Configuration and settings
- controllers/: Movement control modules
- dances/: Dance animation modules
- input_handler.py: Keyboard input processing

Author: VR Pepper Teleoperation Team
Date: October 2025
"""

__version__ = "2.0.0"
__author__ = "VR Pepper Teleoperation Team"

from .main import run

__all__ = ['run']