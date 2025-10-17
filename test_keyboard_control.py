#!/usr/bin/env python
"""
Keyboard Test Controller for Pepper Robot
=========================================
Use this to test Pepper connectivity and responsiveness before VR testing.

Controls:
---------
TOGGLE MODE:
  T             - Switch between CONTINUOUS (hold) and INCREMENTAL (click) modes
  V             - Toggle video feed window

MOVEMENT (mode-dependent):
  CONTINUOUS MODE (default):
    Arrow Keys    - Hold to move (Up=forward, Down=back, Left/Right=strafe)
    Q/E           - Hold to rotate left/right
    SPACE         - Stop all movement
  
  INCREMENTAL MODE:
    Arrow Keys    - Click to move 5cm per press
    Q/E           - Click to rotate ~11° per press
    Z             - Reset accumulated position to origin (0,0,0)

HEAD (always incremental):
  W/S           - Head pitch (up/down) in small steps
  A/D           - Head yaw (left/right) in small steps
  R             - Reset head to center

ARMS (always incremental, reads current position):
  U/J           - Left shoulder pitch (U=up, J=down)
  I/K           - Right shoulder pitch (I=up, K=down)
  7/9           - Left elbow roll (7=bend, 9=straighten)
  8/0           - Right elbow roll (8=bend, 0=straighten)
  O             - Left arm OUT (extend sideways)
  L             - Right arm OUT (extend sideways)
  
  Note: Arms increment from CURRENT position, not absolute.
  Each press moves the joint by ~0.1 radians (~6°)

HANDS:
  [/]           - Open/Close left hand
  ;/'           - Open/Close right hand

PRE-MOTIONS:
  1             - Wave
  2             - Special Dance 😏
  
SYSTEM:
  P             - Print robot status
  V             - Toggle video feed window
  ESC           - Emergency stop and exit

ARM LOGIC EXPLANATION:
---------------------
Pepper's arm joints work as follows:
  - ShoulderPitch: Negative = arm up, Positive = arm down
    Range: -2.0857 to 2.0857 radians (~-120° to +120°)
  
  - ShoulderRoll: Controls arm lateral movement
    LEFT arm:  Positive = out (away from body), Range: 0.0087 to 1.5620
    RIGHT arm: Negative = out (away from body), Range: -1.5620 to -0.0087
  
  - ElbowRoll: Controls elbow bend
    LEFT arm:  Negative = bent, Range: -1.5620 to -0.0087
    RIGHT arm: Positive = bent, Range: 0.0087 to 1.5620

The keyboard controller:
  1. Reads the CURRENT joint angle with getAngles()
  2. Adds/subtracts a small step (0.1 radians)
  3. Clamps to safe limits
  4. Sends new angle with setAngles()

This allows gradual, controlled movement from any starting position.

Author: VR Pepper Teleoperation Team
Date: October 2025
"""

import qi
import sys
import os
import threading
import time
import logging
import urllib.request
import cv2
import numpy as np

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
        
        # Video feed settings
        self.show_video = False
        self.video_url = f"http://{ip}:8080/video_feed"
        self.video_thread = None
        
        # Movement mode toggle
        self.continuous_mode = True  # True = hold to move, False = click to increment
        
        # Movement state (continuous mode)
        self.base_x = 0.0  # forward/back
        self.base_y = 0.0  # strafe
        self.base_theta = 0.0  # rotation
        
        # Accumulated position (incremental mode)
        self.accumulated_x = 0.0
        self.accumulated_y = 0.0
        self.accumulated_theta = 0.0
        
        self.head_yaw = 0.0
        self.head_pitch = 0.0
        
        # Speed settings
        self.linear_speed = 0.3
        self.angular_speed = 0.5
        self.head_speed = 0.2
        self.arm_speed = 0.2
        
        # Incremental movement step sizes
        self.linear_step = 0.05  # 5cm per press
        self.angular_step = 0.2  # ~11 degrees per press
        self.head_step = 0.1  # radians
        self.arm_step = 0.1  # radians
        
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
        logger.info("    Press V to toggle video, ESC to quit, P for status")
    
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
                if self.continuous_mode:
                    # Continuous movement mode - hold keys to move
                    if abs(self.base_x) > 0.01 or abs(self.base_y) > 0.01 or abs(self.base_theta) > 0.01:
                        self.motion.moveToward(self.base_x, self.base_y, self.base_theta)
                else:
                    # Incremental mode - doesn't use this loop
                    self.motion.stopMove()
            except Exception as e:
                logger.error(f"Movement update error: {e}")
            time.sleep(0.05)  # 20Hz update rate
    
    def _video_display_loop(self):
        """Display video feed from Pepper's camera."""
        logger.info(f"Starting video display from {self.video_url}")
        
        try:
            stream = urllib.request.urlopen(self.video_url, timeout=5)
            bytes_data = b''
            
            while self.show_video and self.running:
                try:
                    bytes_data += stream.read(1024)
                    a = bytes_data.find(b'\xff\xd8')  # JPEG start
                    b = bytes_data.find(b'\xff\xd9')  # JPEG end
                    
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        
                        # Decode and display
                        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if frame is not None:
                            cv2.imshow('Pepper Camera Feed (Press V to close)', frame)
                            if cv2.waitKey(1) & 0xFF == ord('v'):
                                self.show_video = False
                                break
                                
                except Exception as e:
                    logger.error(f"Video frame error: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Could not connect to video stream: {e}")
            logger.error(f"Make sure the server is running: python Python/main.py --ip {self.ip}")
        finally:
            cv2.destroyAllWindows()
            logger.info("Video display stopped")
    
    def _toggle_video(self):
        """Toggle video feed window."""
        self.show_video = not self.show_video
        
        if self.show_video:
            # Start video thread
            self.video_thread = threading.Thread(target=self._video_display_loop, daemon=True)
            self.video_thread.start()
            logger.info("✓ Video feed enabled (press V again to close)")
        else:
            logger.info("✓ Video feed disabled")
            cv2.destroyAllWindows()
    
    def on_press(self, key):
        """Handle key press events."""
        try:
            # Toggle movement mode
            if hasattr(key, 'char') and key.char == 't':
                self.continuous_mode = not self.continuous_mode
                mode = "CONTINUOUS (hold keys)" if self.continuous_mode else "INCREMENTAL (click to step)"
                logger.info(f"Movement mode: {mode}")
                if not self.continuous_mode:
                    self._stop_all()  # Stop any continuous movement
                return
            
            # Movement controls
            if self.continuous_mode:
                # CONTINUOUS MODE - Hold to move
                if key == Key.up:
                    self.base_x = self.linear_speed
                elif key == Key.down:
                    self.base_x = -self.linear_speed
                elif key == Key.left:
                    self.base_y = self.linear_speed
                elif key == Key.right:
                    self.base_y = -self.linear_speed
                elif hasattr(key, 'char'):
                    if key.char == 'q':
                        self.base_theta = self.angular_speed
                    elif key.char == 'e':
                        self.base_theta = -self.angular_speed
            else:
                # INCREMENTAL MODE - Click to step
                if key == Key.up:
                    self.accumulated_x += self.linear_step
                    self.motion.moveTo(self.accumulated_x, self.accumulated_y, self.accumulated_theta)
                    logger.info(f"Step forward: position=({self.accumulated_x:.2f}, {self.accumulated_y:.2f})")
                elif key == Key.down:
                    self.accumulated_x -= self.linear_step
                    self.motion.moveTo(self.accumulated_x, self.accumulated_y, self.accumulated_theta)
                    logger.info(f"Step back: position=({self.accumulated_x:.2f}, {self.accumulated_y:.2f})")
                elif key == Key.left:
                    self.accumulated_y += self.linear_step
                    self.motion.moveTo(self.accumulated_x, self.accumulated_y, self.accumulated_theta)
                    logger.info(f"Step left: position=({self.accumulated_x:.2f}, {self.accumulated_y:.2f})")
                elif key == Key.right:
                    self.accumulated_y -= self.linear_step
                    self.motion.moveTo(self.accumulated_x, self.accumulated_y, self.accumulated_theta)
                    logger.info(f"Step right: position=({self.accumulated_x:.2f}, {self.accumulated_y:.2f})")
                elif hasattr(key, 'char'):
                    if key.char == 'q':
                        self.accumulated_theta += self.angular_step
                        self.motion.moveTo(self.accumulated_x, self.accumulated_y, self.accumulated_theta)
                        logger.info(f"Rotate left: theta={self.accumulated_theta:.2f}")
                    elif key.char == 'e':
                        self.accumulated_theta -= self.angular_step
                        self.motion.moveTo(self.accumulated_x, self.accumulated_y, self.accumulated_theta)
                        logger.info(f"Rotate right: theta={self.accumulated_theta:.2f}")
            
            if hasattr(key, 'char'):
                # Toggle video feed
                if key.char == 'v':
                    self._toggle_video()
                    return
                
                # Head controls (always incremental)
                if key.char == 'w':
                    self.head_pitch = min(0.5, self.head_pitch + self.head_step)
                    self.motion.setAngles("HeadPitch", self.head_pitch, self.head_speed)
                    logger.info(f"Head up: pitch={self.head_pitch:.2f}")
                elif key.char == 's':
                    self.head_pitch = max(-0.6, self.head_pitch - self.head_step)
                    self.motion.setAngles("HeadPitch", self.head_pitch, self.head_speed)
                    logger.info(f"Head down: pitch={self.head_pitch:.2f}")
                elif key.char == 'a':
                    self.head_yaw = min(2.0, self.head_yaw + self.head_step)
                    self.motion.setAngles("HeadYaw", self.head_yaw, self.head_speed)
                    logger.info(f"Head left: yaw={self.head_yaw:.2f}")
                elif key.char == 'd':
                    self.head_yaw = max(-2.0, self.head_yaw - self.head_step)
                    self.motion.setAngles("HeadYaw", self.head_yaw, self.head_speed)
                    logger.info(f"Head right: yaw={self.head_yaw:.2f}")
                elif key.char == 'r':
                    self.head_yaw = 0.0
                    self.head_pitch = 0.0
                    self.motion.setAngles(["HeadYaw", "HeadPitch"], [0.0, 0.0], self.head_speed)
                    logger.info("Head reset to center")
                
                # Arm controls (incremental, each press moves arm)
                elif key.char == 'u':
                    # Left shoulder pitch UP
                    current = self.motion.getAngles("LShoulderPitch", True)[0]
                    new_angle = max(-2.0857, current - self.arm_step)
                    self.motion.setAngles("LShoulderPitch", new_angle, self.arm_speed)
                    logger.info(f"Left arm up: {new_angle:.2f}")
                elif key.char == 'j':
                    # Left shoulder pitch DOWN
                    current = self.motion.getAngles("LShoulderPitch", True)[0]
                    new_angle = min(2.0857, current + self.arm_step)
                    self.motion.setAngles("LShoulderPitch", new_angle, self.arm_speed)
                    logger.info(f"Left arm down: {new_angle:.2f}")
                elif key.char == 'i':
                    # Right shoulder pitch UP
                    current = self.motion.getAngles("RShoulderPitch", True)[0]
                    new_angle = max(-2.0857, current - self.arm_step)
                    self.motion.setAngles("RShoulderPitch", new_angle, self.arm_speed)
                    logger.info(f"Right arm up: {new_angle:.2f}")
                elif key.char == 'k':
                    # Right shoulder pitch DOWN
                    current = self.motion.getAngles("RShoulderPitch", True)[0]
                    new_angle = min(2.0857, current + self.arm_step)
                    self.motion.setAngles("RShoulderPitch", new_angle, self.arm_speed)
                    logger.info(f"Right arm down: {new_angle:.2f}")
                elif key.char == 'o':
                    # Left shoulder roll OUT (extend left arm sideways)
                    current = self.motion.getAngles("LShoulderRoll", True)[0]
                    new_angle = min(1.5620, current + self.arm_step)  # Positive = out
                    self.motion.setAngles("LShoulderRoll", new_angle, self.arm_speed)
                    logger.info(f"Left arm out: {new_angle:.2f}")
                elif key.char == 'l':
                    # Right shoulder roll OUT (extend right arm sideways)
                    current = self.motion.getAngles("RShoulderRoll", True)[0]
                    new_angle = max(-1.5620, current - self.arm_step)  # Negative = out
                    self.motion.setAngles("RShoulderRoll", new_angle, self.arm_speed)
                    logger.info(f"Right arm out: {new_angle:.2f}")
                
                # Elbow controls (NEW - for better arm control)
                elif key.char == '7':
                    # Left elbow roll BEND
                    current = self.motion.getAngles("LElbowRoll", True)[0]
                    new_angle = max(-1.5620, current - self.arm_step)  # More negative = more bent
                    self.motion.setAngles("LElbowRoll", new_angle, self.arm_speed)
                    logger.info(f"Left elbow bent: {new_angle:.2f}")
                elif key.char == '9':
                    # Left elbow roll STRAIGHTEN
                    current = self.motion.getAngles("LElbowRoll", True)[0]
                    new_angle = min(-0.0087, current + self.arm_step)  # Less negative = straighter
                    self.motion.setAngles("LElbowRoll", new_angle, self.arm_speed)
                    logger.info(f"Left elbow straightened: {new_angle:.2f}")
                elif key.char == '8':
                    # Right elbow roll BEND
                    current = self.motion.getAngles("RElbowRoll", True)[0]
                    new_angle = min(1.5620, current + self.arm_step)  # More positive = more bent
                    self.motion.setAngles("RElbowRoll", new_angle, self.arm_speed)
                    logger.info(f"Right elbow bent: {new_angle:.2f}")
                elif key.char == '0':
                    # Right elbow roll STRAIGHTEN
                    current = self.motion.getAngles("RElbowRoll", True)[0]
                    new_angle = max(0.0087, current - self.arm_step)  # Less positive = straighter
                    self.motion.setAngles("RElbowRoll", new_angle, self.arm_speed)
                    logger.info(f"Right elbow straightened: {new_angle:.2f}")
                
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
                    logger.info("💃 Playing SPECIAL DANCE...")
                    self.tts.say("Let's dance!")
                    self._special_dance()
                
                # System commands
                elif key.char == 'p':
                    self._print_status()
                elif key.char == 'z':
                    # Reset accumulated position
                    self.accumulated_x = 0.0
                    self.accumulated_y = 0.0
                    self.accumulated_theta = 0.0
                    logger.info("Position reset to origin (0, 0, 0)")
                
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
            # Only stop continuous movement when keys released
            if self.continuous_mode:
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
    
    def _special_dance(self):
        """Special dance animation - Pepper gets DOWN! 💃🕺"""
        logger.info("🎵 Pepper is about to DROP IT! 🎵")
        
        # Enable full body stiffness
        self.motion.setStiffnesses("Body", 1.0)
        time.sleep(0.2)
        
        # Get LOW - hip movement simulation (Pepper doesn't have hips but we'll fake it)
        # Use knee bend + lean
        self.motion.setAngles("KneePitch", 0.5, 0.3)  # Bend knees
        time.sleep(0.3)
        
        # The TWERK - rapid hip oscillation simulation
        # We'll use head + torso coordination
        for cycle in range(6):  # 6 cycles of twerking
            # Down position - lean back slightly
            self.motion.setAngles(["HipPitch", "HeadPitch"], [0.15, -0.2], 0.8)
            time.sleep(0.15)
            
            # Up position - lean forward slightly  
            self.motion.setAngles(["HipPitch", "HeadPitch"], [-0.15, 0.2], 0.8)
            time.sleep(0.15)
        
        # Add some arm flair while twerking (last 4 cycles)
        for cycle in range(4):
            # Arms UP
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [-1.0, -1.0], 0.6)
            self.motion.setAngles(["HipPitch"], [0.15], 0.8)
            time.sleep(0.15)
            
            # Arms DOWN  
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.6)
            self.motion.setAngles(["HipPitch"], [-0.15], 0.8)
            time.sleep(0.15)
        
        # FINALE - Big move!
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [-1.5, -1.5], 0.4)  # Arms way up
        self.motion.setAngles("KneePitch", 0.8, 0.3)  # REALLY low
        time.sleep(0.5)
        
        # Pop back up!
        self.motion.setAngles("KneePitch", 0.0, 0.5)
        time.sleep(0.3)
        
        # Victory pose
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch", "LElbowRoll", "RElbowRoll"], 
                            [-0.5, -0.5, -1.5, 1.5], 0.3)
        time.sleep(0.5)
        
        # Return to normal
        logger.info("💃 DANCE COMPLETE! Pepper's got MOVES!")
        self.posture.goToPosture("Stand", 0.6)
        time.sleep(1.0)
    
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
        mode_str = "CONTINUOUS (hold)" if self.continuous_mode else "INCREMENTAL (click)"
        print("\n" + "="*60)
        print("  KEYBOARD CONTROLS")
        print("="*60)
        print(f"  Movement Mode: {mode_str}")
        print("  Press T to toggle CONTINUOUS/INCREMENTAL")
        print("  Press V to toggle VIDEO FEED")
        print()
        print("  CONTINUOUS MODE (hold keys):")
        print("    Arrow Keys: Hold to move | Q/E: Hold to rotate")
        print()
        print("  INCREMENTAL MODE (click to step):")
        print("    Arrow Keys: Click to move 5cm | Q/E: Click to rotate")
        print("    Z: Reset position to origin")
        print()
        print("  Arms & Elbows:")
        print("    U/I/J/K: Shoulder pitch | O/L: Shoulder roll (out)")
        print("    7/9: Left elbow (bend/straight)")
        print("    8/0: Right elbow (bend/straight)")
        print()
        print("  Always available:")
        print("    WASD: Head | [/]/;/': Hands | 1: Wave | 2: Dance 💃")
        print("    P: Status | V: Video | ESC: Quit")
        print("="*60 + "\n")
        
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
        
        logger.info("Shutting down controller...")
        cv2.destroyAllWindows()
        self.session.close()

def main():
    """Main entry point."""
    pepper_ip = None
    
    # Try to get IP from command line
    if len(sys.argv) >= 2:
        pepper_ip = sys.argv[1]
    # Try to load from saved file
    elif os.path.exists(".pepper_ip"):
        try:
            with open(".pepper_ip", "r") as f:
                pepper_ip = f.read().strip()
            print(f"Using saved Pepper IP: {pepper_ip}")
        except:
            pass
    
    # If still no IP, ask user
    if not pepper_ip:
        print("No Pepper IP provided.")
        print("\nOptions:")
        print("  1. Run with IP: python test_keyboard_control.py 192.168.1.100")
        print("  2. Enter IP now")
        print()
        pepper_ip = input("Enter Pepper's IP address: ").strip()
        
        if not pepper_ip:
            print("No IP provided. Exiting.")
            sys.exit(1)
    
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