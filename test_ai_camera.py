import cv2

from vision.camera import ESP32Camera
from vision.detector import AnimalDetector
from core import config


camera = ESP32Camera(
    config.CAMERA_STREAM,
    config.VIDEO_FLIP
)


detector = AnimalDetector(
    config.YOLO_MODEL,
    config.YOLO_CONFIDENCE
)


camera.connect()


while True:

    frame = camera.read()


    if frame is None:
        continue


    result = detector.detect(frame)


    output = result.plot()


    cv2.imshow(
        "Robot AI",
        output
    )


    if cv2.waitKey(1) == ord("q"):
        break


cv2.destroyAllWindows()