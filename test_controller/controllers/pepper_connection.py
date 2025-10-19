"""
Pepper Robot Connection Handler
Manages connection to Pepper and service initialization.
"""

import qi
import logging

logger = logging.getLogger(__name__)

class PepperConnection:
    """Handles connection to Pepper robot and service initialization."""
    
    def __init__(self, ip, port=9559):
        self.ip = ip
        self.port = port
        self.session = None
        self.motion = None
        self.posture = None
        self.tts = None
        self.battery = None
        
        self._connect()
        self._initialize_services()
        self._initialize_robot()
    
    def _connect(self):
        """Establish connection to Pepper using qi framework."""
        logger.info(f"Connecting to Pepper at {self.ip}:{self.port}...")
        self.session = qi.Session()
        
        try:
            self.session.connect(f"tcp://{self.ip}:{self.port}")
            logger.info("✓ Connected successfully!")
        except qi.Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise ConnectionError(f"Could not connect to Pepper at {self.ip}:{self.port}")
    
    def _initialize_services(self):
        """Initialize all required NAOqi services."""
        try:
            self.motion = self.session.service("ALMotion")
            self.posture = self.session.service("ALRobotPosture")
            self.tts = self.session.service("ALTextToSpeech")
            self.battery = self.session.service("ALBattery")
            logger.info("✓ All services initialized")
            
            # Try to disable autonomous life for full control
            try:
                autonomous_life = self.session.service("ALAutonomousLife")
                current_state = autonomous_life.getState()
                if current_state != "disabled":
                    autonomous_life.setState("disabled")
                    logger.info("✓ Disabled Autonomous Life")
            except Exception as e:
                logger.warning(f"Could not control Autonomous Life: {e}")
                
        except qi.Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
    
    def _initialize_robot(self):
        """Set robot to ready state with stiffness and posture."""
        try:
            logger.info("Initializing robot...")
            self.motion.setStiffnesses("Body", 1.0)
            logger.info("✓ Stiffness set to 1.0")
            
            self.posture.goToPosture("Stand", 0.5)
            logger.info("✓ Robot in Stand posture")
            logger.info("🤖 Robot ready for keyboard control")
        except Exception as e:
            logger.error(f"Failed to initialize robot state: {e}")
            raise
    
    def get_status(self):
        """Get current robot status for monitoring."""
        try:
            battery_level = self.battery.getBatteryCharge()
            stiffness = self.motion.getStiffnesses("Body")
            
            return {
                "battery": battery_level,
                "stiffness": stiffness[0] if stiffness else 0.0,
                "connected": True
            }
        except Exception as e:
            logger.warning(f"Could not retrieve robot status: {e}")
            return {"connected": False}
    
    def emergency_stop(self):
        """Emergency stop - halt all movement and disable stiffness."""
        logger.error("🚨 EMERGENCY STOP")
        try:
            self.motion.stopMove()
            self.motion.setStiffnesses("Body", 0.0)
            logger.info("✓ Robot stopped and stiffness disabled")
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
    
    def close(self):
        """Safely close the connection."""
        logger.info("Closing connection to Pepper...")
        try:
            self.emergency_stop()
            if self.session:
                self.session.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")