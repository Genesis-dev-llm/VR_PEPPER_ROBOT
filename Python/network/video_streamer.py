from flask import Flask, Response
from naoqi import ALProxy
import cv2
import numpy as np

class VideoStreamer:
    """
    Runs a completely separate Flask web server for video.
    This is modular because it doesn't interact with the command system at all.
    Its only job is to request frames from Pepper and stream them over HTTP.
    """
    def __init__(self, ip, port, camera_id=0, resolution=2, fps=30): # 640x480
        self.app = Flask(__name__)
        self.video_proxy = ALProxy("ALVideoDevice", ip, port)
        
        self.camera_id = camera_id 
        self.resolution = resolution # 2 = 640x480
        self.colorspace = 11 # RGB
        self.fps = fps
        self.subscriber_id = None
        self._setup_routes()

    def _setup_routes(self):
        self.app.add_url_rule('/video_feed', 'video_feed', self._video_feed_handler)

    def _subscribe_camera(self):
        self.subscriber_id = self.video_proxy.subscribeCamera(
            "vr_stream", self.camera_id, self.resolution, self.colorspace, self.fps
        )
        print(f"Subscribed to camera with ID: {self.subscriber_id}")

    def _unsubscribe_camera(self):
        if self.subscriber_id:
            self.video_proxy.unsubscribe(self.subscriber_id)
            print("Unsubscribed from camera.")

    def _generate_frames(self):
        self._subscribe_camera()
        try:
            while True:
                img_data = self.video_proxy.getImageRemote(self.subscriber_id)
                if img_data is None: continue

                width, height, image_bytes = img_data[0], img_data[1], img_data[6]
                frame = np.frombuffer(image_bytes, dtype=np.uint8).reshape((height, width, 3))
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                (flag, encoded_image) = cv2.imencode(".jpg", frame_bgr)
                if not flag: continue

                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                      bytearray(encoded_image) + b'\r\n')
        finally:
            self._unsubscribe_camera()

    def _video_feed_handler(self):
        return Response(self._generate_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    def run(self, host='0.0.0.0', port=8080):
        print(f"Starting video streaming server on http://{host}:{port}/video_feed")
        self.app.run(host=host, port=port, debug=False, threaded=True)