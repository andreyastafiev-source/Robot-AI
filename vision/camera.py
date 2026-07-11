"""Low-latency MJPEG reader that retains only the latest decoded frame."""
import threading
import time
import cv2
import numpy as np
import requests

class ESP32Camera:
    def __init__(self, stream_url, flip=False, max_buffer=2097152, reconnect_delay=2.0):
        self.stream_url, self.flip = stream_url, flip
        self.max_buffer, self.reconnect_delay = max_buffer, reconnect_delay
        self.stream = self.frame = self.thread = None
        self.frame_id, self.running, self.last_error = 0, False, None
        self.frame_lock = threading.Lock()
        print("FLIP MODE:", self.flip)

    def connect(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        print("Камера: запущен фоновый захват")

    def _capture_loop(self):
        while self.running:
            try:
                self.stream = requests.get(self.stream_url, stream=True, timeout=(5, 10))
                self.stream.raise_for_status()
                buffer = bytearray(); self.last_error = None
                for chunk in self.stream.iter_content(chunk_size=8192):
                    if not self.running: break
                    if not chunk: continue
                    buffer.extend(chunk)
                    if len(buffer) > self.max_buffer:
                        start = buffer.rfind(b"\xff\xd8")
                        buffer = buffer[start:] if start >= 0 else bytearray()
                    while True:
                        start = buffer.find(b"\xff\xd8")
                        end = buffer.find(b"\xff\xd9", start + 2) if start >= 0 else -1
                        if start < 0 or end < 0:
                            if start > 0: del buffer[:start]
                            break
                        jpg = bytes(buffer[start:end + 2]); del buffer[:end + 2]
                        image = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)
                        if image is None: continue
                        if self.flip: image = cv2.flip(image, -1)
                        with self.frame_lock:
                            self.frame, self.frame_id = image, self.frame_id + 1
            except Exception as error:
                self.last_error = str(error); print("Ошибка камеры:", error)
            finally:
                if self.stream: self.stream.close()
                self.stream = None
            if self.running: time.sleep(self.reconnect_delay)

    def read_latest(self):
        with self.frame_lock:
            return self.frame_id, None if self.frame is None else self.frame.copy()

    def read(self): return self.read_latest()[1]

    def stop(self):
        self.running = False
        if self.stream: self.stream.close()
        if self.thread and self.thread.is_alive(): self.thread.join(timeout=2)
