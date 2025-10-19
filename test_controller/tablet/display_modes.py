"""
Display Mode Management
Handles different tablet display modes and transitions.
"""

from enum import Enum

class DisplayMode(Enum):
    """Available display modes for the tablet."""
    STATUS = "status"           # Status + Action display
    CAMERA = "camera"           # Camera mirror feed
    GREETING = "greeting"       # Greeting with optional image
    
    def next(self):
        """Get the next mode in the cycle."""
        modes = list(DisplayMode)
        current_index = modes.index(self)
        next_index = (current_index + 1) % len(modes)
        return modes[next_index]
    
    def __str__(self):
        """String representation."""
        return self.value.upper()