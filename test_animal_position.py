import cv2

from vision.camera import ESP32Camera
from vision.detector import AnimalDetector
from vision.animals import analyze
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


    animal = analyze(result)


    if animal.found:

        print(
            animal.name,
            round(animal.confidence,2),
            animal.center_x,
            animal.center_y
        )


    image = result.plot()


    cv2.imshow(
        "Animal Position",
        image
    )


    if cv2.waitKey(1)==ord("q"):
        break