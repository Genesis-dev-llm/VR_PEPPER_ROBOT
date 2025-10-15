class ArmController:
    """
    A specialist controller that only handles arm movements.
    It knows the joint names for arms and uses the limits utility
    to ensure all commands are safe before sending them to NAOqi.
    """
    def __init__(self, motion_proxy, limits_util):
        self.motion = motion_proxy
        self.limits = limits_util

    def move(self, side, joints, speed):
        """Moves a single arm based on a set of joint angles from Unity."""
        prefix = "L" if side == "left" else "R"
        
        joint_names = [
            f"{prefix}ShoulderPitch", f"{prefix}ShoulderRoll",
            f"{prefix}ElbowYaw", f"{prefix}ElbowRoll", f"{prefix}WristYaw"
        ]
        
        # Clamp each angle individually using the utility
        angles = [
            self.limits.clamp(joint_names[0], joints['shoulderPitch']),
            self.limits.clamp(joint_names[1], joints['shoulderRoll']),
            self.limits.clamp(joint_names[2], joints['elbowYaw']),
            self.limits.clamp(joint_names[3], joints['elbowRoll']),
            self.limits.clamp(joint_names[4], joints['wristYaw'])
        ]
        
        self.motion.setAngles(joint_names, angles, speed)