"""
PyQt5 GUI Package for Pepper Control Center
Professional graphical interface for controlling Pepper robot.

Modules:
- main_window: Main application window
- camera_panel: Camera feed display widgets
- control_panel: Movement and dance controls
- audio_streamer: Live microphone streaming
- file_handler: Drag & drop file manager
- styles: Qt stylesheet definitions
"""

from .main_window import PepperControlGUI, launch_gui

__all__ = ['PepperControlGUI', 'launch_gui']