from naoqi import ALProxy
from utils.joint_limits import JointLimits
from .base_controller import BaseController
from .head_controller import HeadController
from .hand_controller import HandController
from .arm_controller import ArmController
from .pre_motions import PreMotionPlayer

class PepperController:
    """
    The main manager for all robot control operations.
    It does not contain direct NAOqi calls for movement. Instead, it holds
    instances of specialized controllers and delegates commands to them.
    This is the central hub of the robot's logic.
    """
    def __init__(self, ip, port):
        # --- Proxies to pass to specialists ---
        self.motion = ALProxy("ALMotion", ip, port)
        self.posture = ALProxy("ALRobotPosture", ip, port)
        
        try:
            # Attempt to disable autonomous life for full control
            ALProxy("ALAutonomousLife", ip, port).setState("disabled")
        except Exception as e:
            print(f"Warning: Could not disable Autonomous Life: {e}")

        # --- Utilities ---
        self.limits = JointLimits()

        # --- Create and hold instances of all specialists ---
        self.base = BaseController(self.motion)
        self.head = HeadController(self.motion, self.limits)
        self.hand = HandController(self.motion)
        self.arm = ArmController(self.motion, self.limits)
        self.pre_motions = PreMotionPlayer(self.motion, self.posture)
        
        # --- Initial Robot State ---
        print("Setting initial posture and stiffness...")
        self.motion.setStiffnesses("Body", 1.0)
        self.posture.goToPosture("Stand", 0.5)
        print("Robot is ready.")

    def process_command(self, command):
        """
        The main command router. Receives a command dictionary from the network
        layer and delegates it to the correct specialist controller.
        """
        cmd_type = command.get("type")

        # Prevent live mimicry commands from interfering with a pre-motion
        if self.pre_motions.is_playing() and cmd_type not in ["pre_motion_stop", "emergency_stop"]:
            return # Ignore the command
            
        if cmd_type == "base_move":
            self.base.move(command['linear'], command['angular'])
        elif cmd_type == "head_move":
            self.head.move(command['yaw'], command['pitch'], command['speed'])
        elif cmd_type == "hand_move":
            self.hand.move(command['side'], command['value'])
        elif cmd_type == "arm_move":
            self.arm.move(command['side'], command['joints'], command['speed'])
        elif cmd_type == "pre_motion":
            self.pre_motions.play(command['motion_name'])
        else:
            print(f"Warning: Unknown command type received: {cmd_type}")

    def emergency_stop(self):
        """A critical safety function to halt all robot movement."""
        print("\033[91mEMERGENCY STOP: Halting all motion.\033[0m")
        self.base.stop()
        # You could add logic here to stop pre-motions as well