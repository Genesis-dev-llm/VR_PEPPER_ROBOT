"""
Tablet Display System for Pepper Robot
Provides professional UI on Pepper's chest tablet.

Modules:
- tablet_controller: Main tablet control logic
- display_modes: Different display mode handlers
- html_templates: Professional HTML/CSS templates
"""

from .tablet_controller import TabletController
from .display_modes import DisplayMode

__all__ = [
    'TabletController',
    'DisplayMode'
]