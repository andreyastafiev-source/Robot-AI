import time
import cv2

from core import config
from vision.camera import ESP32Camera
from vision.detector import AnimalDetector


camera = ESP32Camera(
    config.CAMERA_STREAM,
    config.VIDEO_FLIP
)


detector = AnimalDetector(
    config.YOLO_MODEL,
    config.YOLO_CONFIDENCE
)


camera.connect()


count = 0
start = time.time()


while count < 30:

    frame = camera.read()

    if frame is None:
        continue


    t1 = time.time()

    result = detector.detect(frame)

    t2 = time.time()


    print(
        "YOLO:",
        round(t2-t1,3),
        "сек",
        "Размер:",
        frame.shape
    )


    count += 1


print(
    "FPS:",
    round(
        count/(time.time()-start),
        2
    )
)