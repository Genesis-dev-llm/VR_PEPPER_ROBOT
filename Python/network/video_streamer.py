from flask import Flask, Response
from flask_cors import CORS
import qi
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class VideoStreamer:
    """
    Runs a Flask web server for video streaming from Pepper's camera.
    Now uses qi framework instead of naoqi.
    """
    def __init__(self, ip, port, camera_id=0, resolution=2, fps=30):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for Unity to access the stream
        
        self.ip = ip
        self.port = port
        self.camera_id = camera_id
        self.resolution = resolution  # 2 = 640x480
        self.colorspace = 11  # RGB
        self.fps = fps
        self.subscriber_id = None
        self.video_proxy = None
        self.session = None
        
        self._connect()
        self._setup_routes()

    def _connect(self):
        """Connect to Pepper and get video service using qi framework."""
        try:
            logger.info(f"Connecting to Pepper camera at {self.ip}:{self.port}...")
            self.session = qi.Session()
            self.session.connect(f"tcp://{self.ip}:{self.port}")
            self.video_proxy = self.session.service("ALVideoDevice")
            logger.info("✓ Video service connected successfully")
        except qi.Exception as e:
            logger.error(f"Failed to connect to video service: {e}")
            raise

    def _setup_routes(self):
        """Setup Flask routes for video streaming."""
        self.app.add_url_rule('/video_feed', 'video_feed', self._video_feed_handler)
        self.app.add_url_rule('/health', 'health', self._health_check)

    def _health_check(self):
        """Simple health check endpoint."""
        return {"status": "ok", "camera_id": self.camera_id}

    def _subscribe_camera(self):
        """Subscribe to Pepper's camera feed."""
        try:
            self.subscriber_id = self.video_proxy.subscribeCamera(
                "vr_stream", self.camera_id, self.resolution, self.colorspace, self.fps
            )
            logger.info(f"✓ Subscribed to camera with ID: {self.subscriber_id}")
        except Exception as e:
            logger.error(f"Failed to subscribe to camera: {e}")
            raise

    def _unsubscribe_camera(self):
        """Unsubscribe from camera feed."""
        if self.subscriber_id:
            try:
                self.video_proxy.unsubscribe(self.subscriber_id)
                logger.info("✓ Unsubscribed from camera")
            except Exception as e:
                logger.warning(f"Error unsubscribing from camera: {e}")

    def _generate_frames(self):
        """Generator function that yields video frames."""
        self._subscribe_camera()
        try:
            while True:
                try:
                    img_data = self.video_proxy.getImageRemote(self.subscriber_id)
                    if img_data is None:
                        logger.warning("Received None from camera")
                        continue

                    width, height, image_bytes = img_data[0], img_data[1], img_data[6]
                    
                    # Convert raw bytes to numpy array
                    frame = np.frombuffer(image_bytes, dtype=np.uint8).reshape((height, width, 3))
                    
                    # Convert RGB to BGR for OpenCV
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    # Encode frame as JPEG
                    (flag, encoded_image) = cv2.imencode(".jpg", frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    if not flag:
                        logger.warning("Failed to encode frame")
                        continue

                    # Yield frame in multipart format for streaming
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + 
                           bytearray(encoded_image) + b'\r\n')
                           
                except Exception as e:
                    logger.error(f"Error generating frame: {e}")
                    break
                    
        finally:
            self._unsubscribe_camera()

    def _video_feed_handler(self):
        """Flask route handler for video feed."""
        return Response(
            self._generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )

    def run(self, host='0.0.0.0', port=8080):
        """Start the Flask video streaming server."""
        logger.info(f"Starting video streaming server on http://{host}:{port}/video_feed")
        logger.info(f"Health check available at http://{host}:{port}/health")
        try:
            self.app.run(host=host, port=port, debug=False, threaded=True)
        except KeyboardInterrupt:
            logger.info("Video server stopped by user")
        finally:
            if self.session:
                self.session.close()