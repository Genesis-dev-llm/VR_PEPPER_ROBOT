"""
Voice Command System - HYBRID APPROACH (BEST)
Uses Pepper's microphones + STT, Python NLP, and Pepper's TTS
No external services, full NLP processing!
"""

import logging
import threading
import time
import re

logger = logging.getLogger(__name__)

class HybridVoiceCommander:
    """
    Best of both worlds:
    - Pepper's hardware (mics + speakers)
    - Python NLP processing (full flexibility)
    """
    
    def __init__(self, pepper_conn, controllers, dances, tablet):
        self.pepper = pepper_conn
        self.session = pepper_conn.session
        self.controllers = controllers
        self.dances = dances
        self.tablet = tablet
        
        self.is_listening = False
        self.speech_reco = None
        self.tts = None
        self.memory = None
        
        # Stored names
        self.known_names = {}
        
        # Initialize Pepper's services
        try:
            self.speech_reco = self.session.service("ALSpeechRecognition")
            self.tts = self.session.service("ALAnimatedSpeech")
            self.memory = self.session.service("ALMemory")
            
            # Set language
            self.speech_reco.setLanguage("English")
            
            logger.info("✓ Hybrid voice system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            self.speech_reco = None
    
    def start_listening(self):
        """Start continuous speech recognition with full text output."""
        if not self.speech_reco:
            logger.error("Speech recognition not available")
            return False
        
        if self.is_listening:
            return False
        
        try:
            # Enable "full sentence" mode (not just vocabulary)
            # This captures complete phrases, not just keywords
            self.speech_reco.setLanguage("English")
            
            # Subscribe to events
            self.memory.subscribeToEvent(
                "SpeechDetected",
                "VoiceCommander",
                "onSpeechDetected"
            )
            
            # Start recognition
            self.speech_reco.subscribe("VoiceCommander")
            self.is_listening = True
            
            # Start processing thread
            listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            listen_thread.start()
            
            logger.info("✓ Hybrid voice recognition started")
            self.tts.say("Voice commands ready!")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start: {e}")
            return False
    
    def stop_listening(self):
        """Stop listening."""
        if not self.is_listening:
            return
        
        try:
            self.is_listening = False
            
            if self.speech_reco:
                self.speech_reco.unsubscribe("VoiceCommander")
            
            logger.info("✓ Voice recognition stopped")
            
        except Exception as e:
            logger.error(f"Error stopping: {e}")
    
    def _listen_loop(self):
        """Main listening loop - processes full text from Pepper's STT."""
        logger.info("Hybrid voice listening started")
        
        while self.is_listening:
            try:
                # Get recognized speech text from Pepper
                # NOTE: Pepper's ALSpeechRecognition returns phrases in memory
                recognized_text = self._get_recognized_text()
                
                if recognized_text:
                    logger.info(f"Recognized: '{recognized_text}'")
                    
                    # NOW WE USE NLP! Full text processing
                    self._process_with_nlp(recognized_text)
                    
                    # Small delay to avoid re-processing
                    time.sleep(0.5)
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Listen loop error: {e}")
                if not self.is_listening:
                    break
        
        logger.info("Hybrid voice listening ended")
    
    def _get_recognized_text(self):
        """
        Get recognized text from Pepper's speech recognition.
        Pepper stores recognized phrases in ALMemory.
        """
        try:
            # Pepper stores last recognized phrase
            data = self.memory.getData("LastWordRecognized")
            
            if data and isinstance(data, str) and len(data) > 0:
                return data
            
            return None
            
        except Exception as e:
            logger.debug(f"Error getting text: {e}")
            return None
    
    def _process_with_nlp(self, text):
        """
        Process recognized text with full NLP.
        This is where we extract intent, entities, names, etc.
        """
        text_lower = text.lower()
        
        # === HANDSHAKE WITH NAME EXTRACTION (NLP!) ===
        name = self._extract_name_nlp(text_lower)
        if name:
            self._execute_handshake(name)
            return
        
        # === GREETING ===
        if re.search(r'\b(hi|hello|hey)\s+(pepper|robot)\b', text_lower):
            self._execute_dance('wave', "Hello there!")
            return
        
        # === DANCE COMMANDS (NLP patterns) ===
        if re.search(r'\b(wave|waving)\b', text_lower):
            self._execute_dance('wave', "I'll wave for you!")
            return
        
        if re.search(r'\b(special|twerk)\s*dance\b', text_lower):
            self._execute_dance('special', "Let's dance!")
            return
        
        if re.search(r'\brobot\s*dance\b', text_lower):
            self._execute_dance('robot', "Beep boop!")
            return
        
        if re.search(r'\bmoonwalk\b|michael\s*jackson', text_lower):
            self._execute_dance('moonwalk', "Shamone!")
            return
        
        if re.search(r'\b(dance|perform|show\s+me)\b', text_lower):
            self._execute_dance('wave', "Here's a dance!")
            return
        
        # === MOVEMENT COMMANDS (NLP) ===
        if re.search(r'\b(move|go|walk)\s+(forward|ahead)\b', text_lower):
            self._execute_movement('forward', 2.0)
            return
        
        if re.search(r'\b(move|go)\s+(back|backward)\b', text_lower):
            self._execute_movement('back', 2.0)
            return
        
        if re.search(r'\b(turn|rotate|spin)\s+(left)\b', text_lower):
            self._execute_rotation('left', 1.5)
            return
        
        if re.search(r'\b(turn|rotate|spin)\s+(right)\b', text_lower):
            self._execute_rotation('right', 1.5)
            return
        
        if re.search(r'\bstop\b', text_lower):
            self._execute_stop()
            return
        
        # === STATUS QUERIES (NLP) ===
        if re.search(r'\bhow\s+are\s+you\b|\bhow.*doing\b', text_lower):
            self._report_status()
            return
        
        if re.search(r'\bbattery\b|\bcharge\b|\bpower\b', text_lower):
            self._report_battery()
            return
        
        # If we reach here, command not understood
        logger.info(f"Command not recognized: '{text}'")
        self.tts.say("Sorry, I didn't understand that.")
    
    def _extract_name_nlp(self, text):
        """
        Extract name using NLP patterns.
        Handles variations like:
        - "Hi Pepper I'm John"
        - "Hello Pepper my name is Sarah"
        - "I'm Alice"
        - "My name is Bob"
        """
        # Pattern 1: "hi/hello pepper i'm NAME"
        match = re.search(r'(?:hi|hello|hey)\s+pepper\s+(?:i\'m|i\s+am|my\s+name\s+is)\s+([a-z]+)', text)
        if match:
            return match.group(1).capitalize()
        
        # Pattern 2: "my name is NAME"
        match = re.search(r'my\s+name\s+is\s+([a-z]+)', text)
        if match:
            return match.group(1).capitalize()
        
        # Pattern 3: "i'm NAME" or "i am NAME"
        match = re.search(r'(?:i\'m|i\s+am)\s+([a-z]+)', text)
        if match:
            name_candidate = match.group(1)
            # Filter out common words that aren't names
            if name_candidate not in ['fine', 'good', 'okay', 'here', 'ready']:
                return name_candidate.capitalize()
        
        return None
    
    def _execute_handshake(self, name):
        """Execute handshake with extracted name."""
        logger.info(f"Handshake for: {name}")
        
        if name in self.known_names:
            greeting = f"Nice to see you again, {name}!"
        else:
            greeting = f"Nice to meet you, {name}!"
            self.known_names[name] = True
        
        self.tts.say(greeting)
        self.tablet.set_action("Handshake", f"Meeting {name}")
        
        thread = threading.Thread(target=self._handshake_sequence, args=(name,), daemon=True)
        thread.start()
    
    def _handshake_sequence(self, name):
        """Physical handshake sequence."""
        try:
            motion = self.pepper.motion
            
            logger.info("Extending hand...")
            motion.setAngles("RShoulderPitch", 0.0, 0.3)
            time.sleep(0.5)
            motion.setAngles("RShoulderRoll", -0.3, 0.3)
            time.sleep(0.5)
            motion.setAngles("RElbowRoll", 0.5, 0.3)
            time.sleep(0.5)
            
            logger.info("Waiting for handshake...")
            timeout = 10
            start_time = time.time()
            touched = False
            
            while time.time() - start_time < timeout:
                try:
                    touch = self.memory.getData("HandRightBackTouched")
                    if touch > 0.5:
                        touched = True
                        logger.info("Hand touched!")
                        break
                    time.sleep(0.1)
                except:
                    time.sleep(0.1)
            
            if touched:
                # Shake hand
                for _ in range(3):
                    motion.setAngles("RElbowRoll", 0.3, 0.5)
                    time.sleep(0.3)
                    motion.setAngles("RElbowRoll", 0.7, 0.5)
                    time.sleep(0.3)
                
                self.tts.say(f"It was great meeting you, {name}!")
            else:
                logger.info("No handshake (timeout)")
                self.tts.say("Maybe next time!")
            
            logger.info("Returning to rest...")
            motion.setAngles(["RShoulderPitch", "RShoulderRoll", "RElbowRoll"], 
                           [1.0, -0.1, 0.1], 0.3)
            time.sleep(1.0)
            
            self.tablet.set_action("Ready", "Handshake complete")
            
        except Exception as e:
            logger.error(f"Handshake error: {e}")
    
    def _execute_dance(self, dance_id, speech_text):
        """Execute dance."""
        self.tts.say(speech_text)
        self.tablet.set_action(dance_id.capitalize(), "Starting...")
        thread = threading.Thread(target=self._dance_thread, args=(dance_id,), daemon=True)
        thread.start()
    
    def _dance_thread(self, dance_id):
        """Dance thread."""
        try:
            if dance_id in self.dances:
                self.dances[dance_id].perform()
                self.tablet.set_action("Ready", f"{dance_id.capitalize()} done")
        except Exception as e:
            logger.error(f"Dance error: {e}")
    
    def _execute_movement(self, direction, duration):
        """Execute movement."""
        self.tts.say(f"Moving {direction}")
        base = self.controllers.get('base')
        if not base:
            return
        
        if direction == 'forward':
            base.set_continuous_velocity('x', 0.3)
        elif direction == 'back':
            base.set_continuous_velocity('x', -0.3)
        
        def stop_after():
            time.sleep(duration)
            base.stop()
        
        threading.Thread(target=stop_after, daemon=True).start()
    
    def _execute_rotation(self, direction, duration):
        """Execute rotation."""
        self.tts.say(f"Turning {direction}")
        base = self.controllers.get('base')
        if not base:
            return
        
        if direction == 'left':
            base.set_continuous_velocity('theta', 0.5)
        else:
            base.set_continuous_velocity('theta', -0.5)
        
        def stop_after():
            time.sleep(duration)
            base.stop()
        
        threading.Thread(target=stop_after, daemon=True).start()
    
    def _execute_stop(self):
        """Stop movement."""
        base = self.controllers.get('base')
        if base:
            base.stop()
        self.tts.say("Stopping")
    
    def _report_status(self):
        """Report full status."""
        try:
            status = self.pepper.get_status()
            battery = status.get('battery', 0)
            
            if battery >= 60:
                state = "great"
            elif battery >= 30:
                state = "okay"
            else:
                state = "low"
            
            self.tts.say(f"I'm doing well! My battery is at {battery} percent, which is {state}.")
        except:
            self.tts.say("I'm doing well!")
    
    def _report_battery(self):
        """Report just battery."""
        try:
            status = self.pepper.get_status()
            battery = status.get('battery', 0)
            self.tts.say(f"My battery is at {battery} percent.")
        except:
            self.tts.say("I'm not sure about my battery level.")
    
    def is_active(self):
        """Check if active."""
        return self.is_listening


def create_hybrid_voice_commander(pepper_conn, controllers, dances, tablet):
    """Factory function for hybrid voice commander."""
    return HybridVoiceCommander(pepper_conn, controllers, dances, tablet)