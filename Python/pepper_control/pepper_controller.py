import qi
import logging
from utils.joint_limits import JointLimits
from .base_controller import BaseController
from .head_controller import HeadController
from .hand_controller import HandController
from .arm_controller import ArmController
from .pre_motions import PreMotionPlayer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PepperController:
    """
    The main manager for all robot control operations using qi framework.
    Delegates commands to specialized controllers with improved error handling.
    """
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.session = None
        self.motion = None
        self.posture = None
        self.autonomous_life = None
        
        # Connect and initialize
        self._connect()
        self._initialize_services()
        
        # --- Utilities ---
        self.limits = JointLimits()

        # --- Create and hold instances of all specialists ---
        self.base = BaseController(self.motion)
        self.head = HeadController(self.motion, self.limits)
        self.hand = HandController(self.motion)
        self.arm = ArmController(self.motion, self.limits)
        self.pre_motions = PreMotionPlayer(self.motion, self.posture)
        
        # --- Initial Robot State ---
        self._initialize_robot()
        
    def _connect(self):
        """Establish connection to Pepper using qi framework."""
        try:
            logger.info(f"Connecting to Pepper at {self.ip}:{self.port}...")
            self.session = qi.Session()
            self.session.connect(f"tcp://{self.ip}:{self.port}")
            logger.info("✓ Successfully connected to Pepper via qi framework")
        except qi.Exception as e:
            logger.error(f"Failed to connect to Pepper: {e}")
            raise ConnectionError(f"Could not connect to Pepper at {self.ip}:{self.port}")
    
    def _initialize_services(self):
        """Initialize all required NAOqi services."""
        try:
            self.motion = self.session.service("ALMotion")
            self.posture = self.session.service("ALRobotPosture")
            
            # Try to disable autonomous life for full control
            try:
                self.autonomous_life = self.session.service("ALAutonomousLife")
                current_state = self.autonomous_life.getState()
                if current_state != "disabled":
                    self.autonomous_life.setState("disabled")
                    logger.info("✓ Disabled Autonomous Life")
                else:
                    logger.info("✓ Autonomous Life already disabled")
            except Exception as e:
                logger.warning(f"Could not control Autonomous Life: {e}")
                
        except qi.Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
    
    def _initialize_robot(self):
        """Set robot to ready state with stiffness and posture."""
        try:
            logger.info("Setting initial posture and stiffness...")
            self.motion.setStiffnesses("Body", 1.0)
            logger.info("✓ Stiffness set to 1.0")
            
            # Use async posture to avoid blocking
            self.posture.goToPosture("Stand", 0.5)
            logger.info("✓ Moving to Stand posture")
            logger.info("🤖 Robot is ready for teleoperation")
        except Exception as e:
            logger.error(f"Failed to initialize robot state: {e}")
            raise

    def process_command(self, command):
        """
        The main command router with improved validation and error handling.
        """
        if not isinstance(command, dict):
            logger.warning(f"Invalid command format (not a dict): {command}")
            return
            
        cmd_type = command.get("type")
        if not cmd_type:
            logger.warning(f"Command missing 'type' field: {command}")
            return

        # Prevent live mimicry commands from interfering with a pre-motion
        if self.pre_motions.is_playing() and cmd_type not in ["pre_motion_stop", "emergency_stop"]:
            return
        
        try:
            if cmd_type == "base_move":
                self._validate_base_command(command)
                self.base.move(command['linear'], command['angular'])
                
            elif cmd_type == "head_move":
                self._validate_head_command(command)
                self.head.move(command['yaw'], command['pitch'], command['speed'])
                
            elif cmd_type == "hand_move":
                self._validate_hand_command(command)
                self.hand.move(command['side'], command['value'])
                
            elif cmd_type == "arm_move":
                self._validate_arm_command(command)
                self.arm.move(command['side'], command['joints'], command['speed'])
                
            elif cmd_type == "pre_motion":
                motion_name = command.get('motion_name')
                if motion_name:
                    self.pre_motions.play(motion_name)
                else:
                    logger.warning("pre_motion command missing 'motion_name'")
                    
            else:
                logger.warning(f"Unknown command type: {cmd_type}")
                
        except KeyError as e:
            logger.error(f"Command missing required field {e}: {command}")
        except Exception as e:
            logger.error(f"Error processing command {cmd_type}: {e}")

    def _validate_base_command(self, cmd):
        """Validate base movement command structure."""
        if 'linear' not in cmd or 'angular' not in cmd:
            raise KeyError("base_move requires 'linear' and 'angular'")
        if not isinstance(cmd['linear'], (list, tuple)) or len(cmd['linear']) < 2:
            raise ValueError("'linear' must be a list/tuple with at least 2 values")
    
    def _validate_head_command(self, cmd):
        """Validate head movement command structure."""
        required = ['yaw', 'pitch', 'speed']
        for field in required:
            if field not in cmd:
                raise KeyError(f"head_move requires '{field}'")
    
    def _validate_hand_command(self, cmd):
        """Validate hand command structure."""
        if 'side' not in cmd or 'value' not in cmd:
            raise KeyError("hand_move requires 'side' and 'value'")
        if cmd['side'] not in ['left', 'right']:
            raise ValueError("'side' must be 'left' or 'right'")
    
    def _validate_arm_command(self, cmd):
        """Validate arm command structure."""
        if 'side' not in cmd or 'joints' not in cmd or 'speed' not in cmd:
            raise KeyError("arm_move requires 'side', 'joints', and 'speed'")
        if cmd['side'] not in ['left', 'right']:
            raise ValueError("'side' must be 'left' or 'right'")

    def emergency_stop(self):
        """Critical safety function to halt all robot movement."""
        logger.error("🚨 EMERGENCY STOP: Halting all motion")
        try:
            self.base.stop()
            self.motion.setStiffnesses("Body", 0.0)
            logger.info("✓ Robot stopped and stiffness disabled")
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
    
    def get_robot_status(self):
        """Get current robot status for monitoring."""
        try:
            battery = self.session.service("ALBattery")
            battery_level = battery.getBatteryCharge()
            
            temp = self.session.service("ALBodyTemperature")
            temperatures = temp.getTemperatureStatus()
            
            return {
                "battery": battery_level,
                "temperatures": temperatures,
                "stiffness": self.motion.getStiffnesses("Body")
            }
        except Exception as e:
            logger.warning(f"Could not retrieve robot status: {e}")
            return None
    
    def close(self):
        """Safely close the connection."""
        logger.info("Closing connection to Pepper...")
        try:
            self.emergency_stop()
            if self.session:
                self.session.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")