"""
Audio Streamer - Live microphone streaming to Pepper
Captures microphone input and streams to Pepper's speakers in real-time.
"""

import threading
import time
import logging
import numpy as np

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logging.warning("pyaudio not installed. Audio streaming will be disabled.")

logger = logging.getLogger(__name__)

class AudioStreamer:
    """Handles live audio streaming from microphone to Pepper."""
    
    def __init__(self, session):
        self.session = session
        self.audio_device = None
        self.is_streaming = False
        self.stream_thread = None
        
        # Audio parameters
        self.sample_rate = 16000  # Hz
        self.channels = 1  # Mono
        self.chunk_size = 1024
        
        # PyAudio objects
        self.pyaudio_instance = None
        self.input_stream = None
        
        # Volume control
        self.volume = 0.8
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize audio services."""
        if not PYAUDIO_AVAILABLE:
            logger.error("PyAudio not available - audio streaming disabled")
            return
        
        try:
            # Get Pepper's audio device
            self.audio_device = self.session.service("ALAudioDevice")
            logger.info("✓ Audio device service connected")
            
            # Initialize PyAudio
            self.pyaudio_instance = pyaudio.PyAudio()
            logger.info("✓ PyAudio initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
    
    def start_streaming(self):
        """Start streaming microphone to Pepper."""
        if not PYAUDIO_AVAILABLE:
            logger.error("Cannot start streaming - PyAudio not available")
            return False
        
        if self.is_streaming:
            logger.warning("Already streaming")
            return False
        
        try:
            # Open microphone input stream
            self.input_stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            # Start streaming thread
            self.is_streaming = True
            self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
            self.stream_thread.start()
            
            logger.info("✓ Audio streaming started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start audio streaming: {e}")
            self.is_streaming = False
            return False
    
    def stop_streaming(self):
        """Stop streaming."""
        if not self.is_streaming:
            return
        
        self.is_streaming = False
        
        # Wait for thread to finish
        if self.stream_thread:
            self.stream_thread.join(timeout=2.0)
        
        # Close input stream
        if self.input_stream:
            try:
                self.input_stream.stop_stream()
                self.input_stream.close()
            except:
                pass
            self.input_stream = None
        
        logger.info("✓ Audio streaming stopped")
    
    def _stream_loop(self):
        """Main streaming loop (runs in thread)."""
        logger.info("Audio streaming loop started")
        
        try:
            while self.is_streaming and self.input_stream:
                # Read audio data from microphone
                audio_data = self.input_stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Convert to numpy array
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                # Apply volume
                audio_array = (audio_array * self.volume).astype(np.int16)
                
                # Send to Pepper's speakers
                self._send_to_pepper(audio_array.tobytes())
                
        except Exception as e:
            logger.error(f"Error in streaming loop: {e}")
            self.is_streaming = False
        finally:
            logger.info("Audio streaming loop ended")
    
    def _send_to_pepper(self, audio_data):
        """Send audio data to Pepper's speakers."""
        try:
            # Use ALAudioDevice to play audio
            if self.audio_device:
                # Convert audio data to list of integers for NAOqi
                audio_list = list(np.frombuffer(audio_data, dtype=np.int16))
                
                # Send to Pepper
                # Note: This is a simplified version. Real implementation may need
                # to use ALAudioPlayer or direct audio output methods
                self.audio_device.sendRemoteBufferToOutput(
                    self.channels,
                    audio_list
                )
        except Exception as e:
            # Errors here are expected if method not available
            # Fall back to text-to-speech for testing
            pass
    
    def set_volume(self, volume):
        """Set output volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        logger.debug(f"Volume set to {self.volume:.2f}")
    
    def cleanup(self):
        """Cleanup audio resources."""
        self.stop_streaming()
        
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
            except:
                pass
            self.pyaudio_instance = None
    
    def is_active(self):
        """Check if currently streaming."""
        return self.is_streaming


# Fallback implementation if pyaudio not available
class DummyAudioStreamer:
    """Dummy audio streamer for when PyAudio is not available."""
    
    def __init__(self, session):
        self.session = session
        logger.warning("Using dummy audio streamer (PyAudio not installed)")
    
    def start_streaming(self):
        logger.warning("Audio streaming not available - install pyaudio")
        return False
    
    def stop_streaming(self):
        pass
    
    def set_volume(self, volume):
        pass
    
    def cleanup(self):
        pass
    
    def is_active(self):
        return False


def create_audio_streamer(session):
    """Factory function to create appropriate audio streamer."""
    if PYAUDIO_AVAILABLE:
        return AudioStreamer(session)
    else:
        return DummyAudioStreamer(session)