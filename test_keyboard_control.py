#!/usr/bin/env python
"""
Keyboard Test Controller for Pepper Robot
=========================================
Use this to test Pepper connectivity and responsiveness before VR testing.

Controls:
---------
MOVEMENT:
  Arrow Keys    - Move base (Up=forward, Down=back, Left/Right=strafe)
  Q/E           - Rotate left/right
  SPACE         - Stop all movement

HEAD:
  W/S           - Head pitch (up/down)
  A/D           - Head yaw (left/right)
  R             - Reset head to center

ARMS:
  U/J           - Left shoulder pitch (up/down)
  I/K           - Right shoulder pitch (up/down)
  O/L           - Left/Right arms to side (shoulder roll)
  
HANDS:
  [/]           - Open/Close left hand
  ;/'           - Open/Close right hand

PRE-MOTIONS:
  1             - Wave
  2             - Dance (if implemented)
  
SYSTEM:
  P             - Print robot status
  ESC           - Emergency stop and exit

Author: VR Pepper Teleoperation Team
Date: October 2025
"""

import qi
import sys
import threading
import time
import logging

# Try to import keyboard library
try:
    from pynput import keyboard
    from pynput.keyboard import Key
except ImportError:
    print("ERROR: pynput not installed. Install with: pip install pynput")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class KeyboardPepperController:
    """Interactive keyboard controller for Pepper robot testing."""
    
    def __init__(self, ip, port=9559):
        self.ip = ip
        self.port = port
        self.running = True
        
        # Movement state
        self.base_x = 0.0  # forward/back
        self.base_y = 0.0  # strafe
        self.base_theta = 0.0  # rotation
        
        self.head_yaw = 0.0
        self.head_pitch = 0.0
        
        # Speed settings
        self.linear_speed = 0.3
        self.angular_speed = 0.5
        self.head_speed = 0.2
        self.arm_speed = 0.2
        
        # Connect to robot
        logger.info(f"Connecting to Pepper at {ip}:{port}...")
        self.session = qi.Session()
        try:
            self.session.connect(f"tcp://{ip}:{port}")
            logger.info("✓ Connected successfully!")
        except qi.Exception as e:
            logger.error(f"Failed to connect: {e}")
            sys.exit(1)
        
        # Get services
        self.motion = self.session.service("ALMotion")
        self.posture = self.session.service("ALRobotPosture")
        self.tts = self.session.service("ALTextToSpeech")
        
        # Initialize robot
        self._initialize_robot()
        
        # Start movement update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        logger.info("🎮 Keyboard controller ready! Press keys to control Pepper.")
        logger.info("    Press ESC to quit, P for status")
    
    def _initialize_robot(self):
        """Prepare robot for control."""
        logger.info("Initializing robot...")
        try:
            # Disable autonomous life
            autonomous_life = self.session.service("ALAutonomousLife")
            autonomous_life.setState("disabled")
        except:
            pass
        
        self.motion.setStiffnesses("Body", 1.0)
        self.posture.goToPosture("Stand", 0.5)
        logger.info("✓ Robot ready")
    
    def _update_loop(self):
        """Continuously update base movement (runs in background thread)."""
        while self.running:
            try:
                if abs(self.base_x) > 0.01 or abs(self.base_y) > 0.01 or abs(self.base_theta) > 0.01:
                    self.motion.moveToward(self.base_x, self.base_y, self.base_theta)
            except Exception as e:
                logger.error(f"Movement update error: {e}")
            time.sleep(0.05)  # 20Hz update rate
    
    def on_press(self, key):
        """Handle key press events."""
        try:
            # Movement controls
            if key == Key.up:
                self.base_x = self.linear_speed
            elif key == Key.down:
                self.base_x = -self.linear_speed
            elif key == Key.left:
                self.base_y = self.linear_speed
            elif key == Key.right:
                self.base_y = -self.linear_speed
            elif hasattr(key, 'char'):
                # Character keys
                if key.char == 'q':
                    self.base_theta = self.angular_speed
                elif key.char == 'e':
                    self.base_theta = -self.angular_speed
                
                # Head controls
                elif key.char == 'w':
                    self.head_pitch = min(0.5, self.head_pitch + 0.1)
                    self.motion.setAngles("HeadPitch", self.head_pitch, self.head_speed)
                elif key.char == 's':
                    self.head_pitch = max(-0.6, self.head_pitch - 0.1)
                    self.motion.setAngles("HeadPitch", self.head_pitch, self.head_speed)
                elif key.char == 'a':
                    self.head_yaw = min(2.0, self.head_yaw + 0.2)
                    self.motion.setAngles("HeadYaw", self.head_yaw, self.head_speed)
                elif key.char == 'd':
                    self.head_yaw = max(-2.0, self.head_yaw - 0.2)
                    self.motion.setAngles("HeadYaw", self.head_yaw, self.head_speed)
                elif key.char == 'r':
                    self.head_yaw = 0.0
                    self.head_pitch = 0.0
                    self.motion.setAngles(["HeadYaw", "HeadPitch"], [0.0, 0.0], self.head_speed)
                    logger.info("Head reset to center")
                
                # Arm controls
                elif key.char == 'u':
                    self.motion.setAngles("LShoulderPitch", -0.5, self.arm_speed)
                elif key.char == 'j':
                    self.motion.setAngles("LShoulderPitch", 1.5, self.arm_speed)
                elif key.char == 'i':
                    self.motion.setAngles("RShoulderPitch", -0.5, self.arm_speed)
                elif key.char == 'k':
                    self.motion.setAngles("RShoulderPitch", 1.5, self.arm_speed)
                elif key.char == 'o':
                    self.motion.setAngles("LShoulderRoll", 0.3, self.arm_speed)
                elif key.char == 'l':
                    self.motion.setAngles("RShoulderRoll", -0.3, self.arm_speed)
                
                # Hand controls
                elif key.char == '[':
                    self.motion.setAngles("LHand", 1.0, 0.3)
                    logger.info("Left hand opened")
                elif key.char == ']':
                    self.motion.setAngles("LHand", 0.0, 0.3)
                    logger.info("Left hand closed")
                elif key.char == ';':
                    self.motion.setAngles("RHand", 1.0, 0.3)
                    logger.info("Right hand opened")
                elif key.char == "'":
                    self.motion.setAngles("RHand", 0.0, 0.3)
                    logger.info("Right hand closed")
                
                # Pre-motions
                elif key.char == '1':
                    logger.info("Playing wave animation...")
                    self.tts.say("Hello!")
                    self._wave()
                elif key.char == '2':
                    logger.info("Dance not implemented yet")
                
                # System commands
                elif key.char == 'p':
                    self._print_status()
                
            # Space bar - stop
            elif key == Key.space:
                self._stop_all()
                logger.info("⏸️  All movement stopped")
            
            # ESC - quit
            elif key == Key.esc:
                logger.info("ESC pressed - shutting down...")
                self.running = False
                self._stop_all()
                return False  # Stop listener
                
        except AttributeError:
            pass  # Ignore special keys we don't handle
        except Exception as e:
            logger.error(f"Error handling key press: {e}")
    
    def on_release(self, key):
        """Handle key release events."""
        try:
            # Stop base movement when keys released
            if key == Key.up or key == Key.down:
                self.base_x = 0.0
            elif key == Key.left or key == Key.right:
                self.base_y = 0.0
            elif hasattr(key, 'char'):
                if key.char in ['q', 'e']:
                    self.base_theta = 0.0
        except:
            pass
    
    def _stop_all(self):
        """Stop all movement."""
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_theta = 0.0
        self.motion.stopMove()
    
    def _wave(self):
        """Simple wave animation."""
        self.motion.setAngles("RShoulderPitch", -0.5, 0.2)
        time.sleep(0.5)
        self.motion.setAngles("RShoulderRoll", -1.2, 0.2)
        time.sleep(0.5)
        self.motion.setAngles("RElbowRoll", 1.5, 0.2)
        time.sleep(0.5)
        
        for _ in range(3):
            self.motion.setAngles("RWristYaw", -1.0, 0.4)
            time.sleep(0.3)
            self.motion.setAngles("RWristYaw", 1.0, 0.4)
            time.sleep(0.3)
        
        self.posture.goToPosture("Stand", 0.5)
    
    def _print_status(self):
        """Print current robot status."""
        try:
            battery = self.session.service("ALBattery")
            battery_level = battery.getBatteryCharge()
            
            stiffness = self.motion.getStiffnesses("Body")
            
            print("\n" + "="*50)
            print("🤖 PEPPER ROBOT STATUS")
            print("="*50)
            print(f"Battery: {battery_level}%")
            print(f"Body Stiffness: {stiffness[0]:.2f}")
            print(f"Head Position: Yaw={self.head_yaw:.2f}, Pitch={self.head_pitch:.2f}")
            print(f"Base Movement: X={self.base_x:.2f}, Y={self.base_y:.2f}, Theta={self.base_theta:.2f}")
            print("="*50 + "\n")
        except Exception as e:
            logger.error(f"Could not retrieve status: {e}")
    
    def run(self):
        """Start the keyboard listener."""
        print("\n" + "="*60)
        print("  KEYBOARD CONTROLS - See docstring for full list")
        print("="*60)
        print("  Arrow Keys: Move  |  Q/E: Rotate  |  Space: Stop")
        print("  WASD: Head  |  U/I: Arms  |  [/]: Hands  |  1: Wave")
        print("  P: Status  |  ESC: Quit")
        print("="*60 + "\n")
        
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
        
        logger.info("Shutting down controller...")
        self.session.close()

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_keyboard_control.py <PEPPER_IP>")
        print("Example: python test_keyboard_control.py 192.168.1.100")
        sys.exit(1)
    
    pepper_ip = sys.argv[1]
    
    try:
        controller = KeyboardPepperController(pepper_ip)
        controller.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()