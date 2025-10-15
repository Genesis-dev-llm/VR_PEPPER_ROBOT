class BaseController:
    """A specialist controller that only handles base (wheel) movements."""
    def __init__(self, motion_proxy):
        self.motion = motion_proxy
        # Define safe maximum speeds
        self.max_linear = 0.55
        self.max_angular = 1.5

    def move(self, linear, angular):
        """Controls translation and rotation using NAOqi's moveToward."""
        # Unpack and clamp linear velocities
        vx = max(-self.max_linear, min(self.max_linear, linear[0])) # Forward/Back
        vy = max(-self.max_linear, min(self.max_linear, linear[1])) # Strafe
        
        # Clamp angular velocity
        theta = max(-self.max_angular, min(self.max_angular, angular)) # Turn
        
        self.motion.moveToward(vx, vy, theta)

    def stop(self):
        """Stops all base movement immediately."""
        self.motion.stopMove()