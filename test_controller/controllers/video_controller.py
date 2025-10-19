"""
Video Feed Controller
Displays Pepper's camera feed in a window.
"""

import logging
import threading
import urllib.request
import cv2
import numpy as np
from .. import config

logger = logging.getLogger(__name__)

class VideoController:
    """Manages video feed from Pepper's camera."""
    
    def __init__(self, ip):
        self.ip = ip
        self.video_url = f"http://{ip}:{config.VIDEO_PORT}/video_feed"
        self.is_running = False
        self.thread = None
    
    def start(self):
        """Start video feed in a separate thread."""
        if self.is_running:
            logger.warning("Video feed already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._display_loop, daemon=True)
        self.thread.start()
        logger.info("✓ Video feed started")
    
    def stop(self):
        """Stop video feed."""
        self.is_running = False
        cv2.destroyAllWindows()
        logger.info("✓ Video feed stopped")
    
    def _check_server(self):
        """Check if video server is accessible."""
        try:
            # Try to connect to the health endpoint
            health_url = f"http://{self.ip}:{config.VIDEO_PORT}/health"
            urllib.request.urlopen(health_url, timeout=2)
            return True
        except Exception:
            return False
    
    def _display_loop(self):
        """Display video feed (runs in background thread)."""
        # Check if server is running
        if not self._check_server():
            logger.error("=" * 60)
            logger.error("VIDEO SERVER NOT ACCESSIBLE")
            logger.error("=" * 60)
            logger.error(f"Cannot connect to: {self.video_url}")
            logger.error("")
            logger.error("SOLUTION:")
            logger.error("  1. Start the Python server first:")
            logger.error(f"     python Python/main.py --ip {self.ip}")
            logger.error("")
            logger.error("  2. Wait for 'Video streaming server' message")
            logger.error("")
            logger.error("  3. Then press V in this keyboard tester")
            logger.error("=" * 60)
            self.is_running = False
            return
        
        logger.info(f"Connecting to video stream: {self.video_url}")
        
        try:
            stream = urllib.request.urlopen(self.video_url, timeout=config.VIDEO_TIMEOUT)
            bytes_data = b''
            
            logger.info("✓ Video stream connected!")
            logger.info("Press V again to close video window")
            
            while self.is_running:
                try:
                    bytes_data += stream.read(1024)
                    a = bytes_data.find(b'\xff\xd8')  # JPEG start marker
                    b = bytes_data.find(b'\xff\xd9')  # JPEG end marker
                    
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        
                        # Decode and display
                        frame = cv2.imdecode(
                            np.frombuffer(jpg, dtype=np.uint8), 
                            cv2.IMREAD_COLOR
                        )
                        
                        if frame is not None:
                            cv2.imshow('Pepper Camera Feed (Press V to close)', frame)
                            
                            # Check for window close or 'v' key
                            key = cv2.waitKey(1) & 0xFF
                            if key == ord('v') or cv2.getWindowProperty(
                                'Pepper Camera Feed (Press V to close)', 
                                cv2.WND_PROP_VISIBLE
                            ) < 1:
                                self.is_running = False
                                break
                                
                except Exception as e:
                    logger.error(f"Frame processing error: {e}")
                    break
                    
        except urllib.error.URLError as e:
            logger.error(f"Could not connect to video stream: {e}")
            logger.error(f"Is the server running? python Python/main.py --ip {self.ip}")
        except Exception as e:
            logger.error(f"Video stream error: {e}")
        finally:
            cv2.destroyAllWindows()
            self.is_running = False
            logger.info("Video display stopped")
    
    def is_active(self):
        """Check if video feed is currently running."""
        return self.is_running