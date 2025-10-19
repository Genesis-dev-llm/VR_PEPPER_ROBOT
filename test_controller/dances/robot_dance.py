"""
Robot Dance Animation
Mechanical, choppy movements with sharp angles and pauses.
"""

import time
import logging
from .base_dance import BaseDance
from .. import config

logger = logging.getLogger(__name__)

class RobotDance(BaseDance):
    """Mechanical robot-style dance with choppy movements."""
    
    def perform(self):
        """Perform robot dance animation."""
        logger.info("🤖 Starting Robot Dance animation...")
        
        self.ensure_stiffness()
        
        # === SEQUENCE 1: Head snap left-right ===
        logger.info("Sequence 1: Head snaps")
        self.safe_set_angles("HeadYaw", 1.5, config.ROBOT_SPEED)
        time.sleep(config.ROBOT_PAUSE)
        self.safe_set_angles("HeadYaw", -1.5, config.ROBOT_SPEED)
        time.sleep(config.ROBOT_PAUSE)
        self.safe_set_angles("HeadYaw", 0.0, config.ROBOT_SPEED)
        time.sleep(config.ROBOT_PAUSE)
        
        # === SEQUENCE 2: Right arm up ===
        logger.info("Sequence 2: Right arm up")
        self.safe_set_angles("RShoulderPitch", -1.5, config.ROBOT_SPEED)
        time.sleep(config.ROBOT_PAUSE)
        self.safe_set_angles("RElbowRoll", 1.5, config.ROBOT_SPEED)
        time.sleep(config.ROBOT_PAUSE)
        
        # === SEQUENCE 3: Left arm out ===
        logger.info("Sequence 3: Left arm out")
        self.safe_set_angles("LShoulderRoll", 1.5, config.ROBOT_SPEED)
        time.sleep(config.ROBOT_PAUSE)
        self.safe_set_angles("LElbowRoll", -1.5, config.ROBOT_SPEED)
        time.sleep(config.ROBOT_PAUSE)
        
        # === SEQUENCE 4: Both arms forward ===
        logger.info("Sequence 4: Arms forward")
        self.safe_set_angles(
            ["RShoulderPitch", "LShoulderPitch"],
            [0.0, 0.0],
            config.ROBOT_SPEED
        )
        time.sleep(config.ROBOT_PAUSE)
        self.safe_set_angles(
            ["RShoulderRoll", "LShoulderRoll"],
            [0.0, 0.0],
            config.ROBOT_SPEED
        )
        time.sleep(config.ROBOT_PAUSE)
        
        # === SEQUENCE 5: Elbows bend sharp ===
        logger.info("Sequence 5: Sharp elbow bends")
        self.safe_set_angles(
            ["RElbowRoll", "LElbowRoll"],
            [1.5, -1.5],
            config.ROBOT_SPEED
        )
        time.sleep(config.ROBOT_PAUSE)
        self.safe_set_angles(
            ["RElbowRoll", "LElbowRoll"],
            [0.1, -0.1],
            config.ROBOT_SPEED
        )
        time.sleep(config.ROBOT_PAUSE)
        
        # === SEQUENCE 6: Wrist rotation ===
        logger.info("Sequence 6: Wrist rotations")
        self.safe_set_angles(
            ["RWristYaw", "LWristYaw"],
            [1.8, -1.8],
            config.ROBOT_SPEED
        )
        time.sleep(config.ROBOT_PAUSE)
        self.safe_set_angles(
            ["RWristYaw", "LWristYaw"],
            [-1.8, 1.8],
            config.ROBOT_SPEED
        )
        time.sleep(config.ROBOT_PAUSE)
        self.safe_set_angles(
            ["RWristYaw", "LWristYaw"],
            [0.0, 0.0],
            config.ROBOT_SPEED
        )
        time.sleep(config.ROBOT_PAUSE)
        
        # === SEQUENCE 7: Finale - Both arms up ===
        logger.info("Sequence 7: Finale")
        self.safe_set_angles(
            ["RShoulderPitch", "LShoulderPitch"],
            [-1.5, -1.5],
            config.ROBOT_SPEED
        )
        time.sleep(config.ROBOT_PAUSE)
        self.safe_set_angles(
            ["RElbowRoll", "LElbowRoll"],
            [1.5, -1.5],
            config.ROBOT_SPEED
        )
        time.sleep(0.5)
        
        # Return to stand
        logger.info("🤖 Robot Dance complete!")
        self.return_to_stand()