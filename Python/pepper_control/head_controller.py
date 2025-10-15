class HeadController:
    """A specialist controller that only handles head pitch and yaw movements."""
    def __init__(self, motion_proxy, limits_util):
        self.motion = motion_proxy
        self.limits = limits_util
        self.joint_names = ["HeadYaw", "HeadPitch"]

    def move(self, yaw, pitch, speed):
        """Moves the head to a target yaw and pitch."""
        # Clamp angles using the utility to prevent mechanical stress
        clamped_yaw = self.limits.clamp("HeadYaw", yaw)
        clamped_pitch = self.limits.clamp("HeadPitch", pitch)
        
        self.motion.setAngles(self.joint_names, [clamped_yaw, clamped_pitch], speed)