import cv2

from vision.camera import ESP32Camera
from core import config


camera = ESP32Camera(
    config.CAMERA_STREAM,
    config.VIDEO_FLIP
)


camera.connect()


while True:

    frame = camera.read()


    if frame is None:
        continue


    cv2.imshow(
        "ESP32 Camera",
        frame
    )


    if cv2.waitKey(1) == ord("q"):
        break


cv2.destroyAllWindows()