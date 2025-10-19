"""
Body Controller
Handles Pepper's upper body: head, arms, wrists, and hands.
"""

import logging
from .. import config

logger = logging.getLogger(__name__)

class BodyController:
    """Controls Pepper's head, arms, wrists, and hands."""
    
    def __init__(self, motion_service):
        self.motion = motion_service
        
        # Body movement speed (can be adjusted with [/] keys)
        self.body_speed = config.BODY_SPEED_DEFAULT
        
        # Current head position
        self.head_yaw = 0.0
        self.head_pitch = 0.0
    
    # ========================================================================
    # HEAD CONTROL
    # ========================================================================
    
    def move_head(self, direction):
        """Move head incrementally."""
        if direction == 'up':
            self.head_pitch = config.clamp_joint(
                'HeadPitch',
                self.head_pitch + config.HEAD_STEP
            )
        elif direction == 'down':
            self.head_pitch = config.clamp_joint(
                'HeadPitch',
                self.head_pitch - config.HEAD_STEP
            )
        elif direction == 'left':
            self.head_yaw = config.clamp_joint(
                'HeadYaw',
                self.head_yaw + config.HEAD_STEP
            )
        elif direction == 'right':
            self.head_yaw = config.clamp_joint(
                'HeadYaw',
                self.head_yaw - config.HEAD_STEP
            )
        
        self.motion.setAngles(["HeadYaw", "HeadPitch"], 
                             [self.head_yaw, self.head_pitch], 
                             self.body_speed)
        logger.info(f"Head: yaw={self.head_yaw:.2f}, pitch={self.head_pitch:.2f}")
    
    def reset_head(self):
        """Reset head to center position."""
        self.head_yaw = 0.0
        self.head_pitch = 0.0
        self.motion.setAngles(["HeadYaw", "HeadPitch"], [0.0, 0.0], self.body_speed)
        logger.info("Head reset to center")
    
    # ========================================================================
    # ARM CONTROL - SHOULDERS
    # ========================================================================
    
    def move_shoulder_pitch(self, side, direction):
        """Move shoulder pitch (up/down)."""
        joint_name = f"{side}ShoulderPitch"
        current = self.motion.getAngles(joint_name, True)[0]
        
        if direction == 'up':
            new_angle = current - config.ARM_STEP
        else:  # down
            new_angle = current + config.ARM_STEP
        
        new_angle = config.clamp_joint(joint_name, new_angle)
        self.motion.setAngles(joint_name, new_angle, self.body_speed)
        logger.info(f"{joint_name}: {new_angle:.2f}")
    
    def move_shoulder_roll(self, side, direction='out'):
        """Move shoulder roll (extend arm sideways)."""
        joint_name = f"{side}ShoulderRoll"
        current = self.motion.getAngles(joint_name, True)[0]
        
        if side == 'L':
            # Left arm: positive = out
            new_angle = current + config.ARM_STEP if direction == 'out' else current - config.ARM_STEP
        else:  # Right arm
            # Right arm: negative = out
            new_angle = current - config.ARM_STEP if direction == 'out' else current + config.ARM_STEP
        
        new_angle = config.clamp_joint(joint_name, new_angle)
        self.motion.setAngles(joint_name, new_angle, self.body_speed)
        logger.info(f"{joint_name}: {new_angle:.2f}")
    
    # ========================================================================
    # ARM CONTROL - ELBOWS
    # ========================================================================
    
    def move_elbow_roll(self, side, direction):
        """Move elbow roll (bend/straighten)."""
        joint_name = f"{side}ElbowRoll"
        current = self.motion.getAngles(joint_name, True)[0]
        
        if side == 'L':
            # Left arm: more negative = more bent
            if direction == 'bend':
                new_angle = current - config.ARM_STEP
            else:  # straighten
                new_angle = current + config.ARM_STEP
        else:  # Right arm
            # Right arm: more positive = more bent
            if direction == 'bend':
                new_angle = current + config.ARM_STEP
            else:  # straighten
                new_angle = current - config.ARM_STEP
        
        new_angle = config.clamp_joint(joint_name, new_angle)
        self.motion.setAngles(joint_name, new_angle, self.body_speed)
        logger.info(f"{joint_name}: {new_angle:.2f}")
    
    # ========================================================================
    # WRIST CONTROL (NEW!)
    # ========================================================================
    
    def rotate_wrist(self, side, direction):
        """Rotate wrist."""
        joint_name = f"{side}WristYaw"
        current = self.motion.getAngles(joint_name, True)[0]
        
        if direction == 'ccw':  # Counter-clockwise
            new_angle = current + config.WRIST_STEP
        else:  # cw (clockwise)
            new_angle = current - config.WRIST_STEP
        
        new_angle = config.clamp_joint(joint_name, new_angle)
        self.motion.setAngles(joint_name, new_angle, self.body_speed)
        logger.info(f"{joint_name} rotated: {new_angle:.2f}")
    
    # ========================================================================
    # HAND CONTROL
    # ========================================================================
    
    def move_hand(self, side, state):
        """Open or close hand."""
        joint_name = f"{side}Hand"
        value = 1.0 if state == 'open' else 0.0
        self.motion.setAngles(joint_name, value, 0.3)
        logger.info(f"{joint_name} {state}")
    
    # ========================================================================
    # SPEED CONTROL
    # ========================================================================
    
    def increase_speed(self):
        """Increase body movement speed."""
        self.body_speed = config.clamp(
            self.body_speed + config.SPEED_STEP,
            config.MIN_SPEED,
            config.MAX_SPEED
        )
        logger.info(f"Body speed increased: {self.body_speed:.2f}")
        return self.body_speed
    
    def decrease_speed(self):
        """Decrease body movement speed."""
        self.body_speed = config.clamp(
            self.body_speed - config.SPEED_STEP,
            config.MIN_SPEED,
            config.MAX_SPEED
        )
        logger.info(f"Body speed decreased: {self.body_speed:.2f}")
        return self.body_speed