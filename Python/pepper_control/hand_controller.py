class HandController:
    """A specialist controller that only handles opening and closing the hands."""
    def __init__(self, motion_proxy):
        self.motion = motion_proxy

    def move(self, side, value):
        """Sets the open/close state of a single hand."""
        hand_name = "LHand" if side == "left" else "RHand"
        
        # Clamp value between 0.0 (closed) and 1.0 (open) for safety
        clamped_value = max(0.0, min(1.0, value))
        
        # A fixed speed is fine for the simple hand mechanism
        self.motion.setAngles(hand_name, clamped_value, 0.3)