"""
Wave Dance Animation
Simple friendly wave gesture.
"""

import time
import logging
from .base_dance import BaseDance

logger = logging.getLogger(__name__)

class WaveDance(BaseDance):
    """Simple wave animation."""
    
    def perform(self):
        """Perform wave animation."""
        logger.info("🎭 Starting Wave animation...")
        
        self.ensure_stiffness()
        
        # Raise arm
        self.safe_set_angles("RShoulderPitch", -0.5, 0.2)
        time.sleep(0.5)
        
        # Extend arm sideways
        self.safe_set_angles("RShoulderRoll", -1.2, 0.2)
        time.sleep(0.5)
        
        # Bend elbow
        self.safe_set_angles("RElbowRoll", 1.5, 0.2)
        time.sleep(0.5)
        
        # Wave wrist back and forth (3 times)
        for _ in range(3):
            self.safe_set_angles("RWristYaw", -1.0, 0.4)
            time.sleep(0.3)
            self.safe_set_angles("RWristYaw", 1.0, 0.4)
            time.sleep(0.3)
        
        # Return to stand
        self.return_to_stand()
        logger.info("✓ Wave animation complete")