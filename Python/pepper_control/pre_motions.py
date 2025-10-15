import time
import threading

class PreMotionPlayer:
    """
    A specialist controller for handling long-running, pre-recorded animations.
    It uses threading to avoid blocking the main command server loop, allowing
    the system to remain responsive.
    """
    def __init__(self, motion_proxy, posture_proxy):
        self.motion = motion_proxy
        self.posture = posture_proxy
        self._is_playing = False
        self.lock = threading.Lock()

    def is_playing(self):
        """Safely checks if a motion is currently active."""
        with self.lock:
            return self._is_playing

    def play(self, motion_name):
        """Plays a pre-motion in a non-blocking background thread."""
        if self.is_playing():
            print("Already playing a pre-motion, request ignored.")
            return

        # Start the animation in a new thread
        motion_thread = threading.Thread(target=self._run_motion, args=(motion_name,))
        motion_thread.daemon = True # Allows main program to exit even if thread is running
        motion_thread.start()

    def _run_motion(self, motion_name):
        """The private method that executes in the background thread."""
        with self.lock:
            self._is_playing = True

        print(f"Starting pre-motion: {motion_name}")
        try:
            # --- Animation Logic ---
            if motion_name == "wave":
                self._wave_motion()
            elif motion_name == "dance":
                # TODO: Implement a dance animation
                print("Dance motion not yet implemented.")
            else:
                print(f"Unknown pre-motion: {motion_name}")
        finally:
            # --- Cleanup ---
            # Ensure robot returns to a safe, neutral state after the animation
            self.posture.goToPosture("Stand", 0.5)
            print(f"Finished pre-motion: {motion_name}")
            with self.lock:
                self._is_playing = False

    def _wave_motion(self):
        """A simple, hard-coded wave animation sequence."""
        self.motion.setStiffnesses("RARM", 1.0)
        self.motion.setAngles("RShoulderPitch", -0.5, 0.2)
        time.sleep(0.5)
        self.motion.setAngles("RShoulderRoll", -1.2, 0.2)
        time.sleep(0.5)
        self.motion.setAngles("RElbowRoll", 1.5, 0.2)
        time.sleep(0.5)
        
        for _ in range(3):
            self.motion.setAngles("RWristYaw", -1.0, 0.4)
            time.sleep(0.5)
            self.motion.setAngles("RWristYaw", 1.0, 0.4)
            time.sleep(0.5)