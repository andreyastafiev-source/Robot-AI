import cv2

from core import config

from vision.camera import ESP32Camera
from vision.detector import AnimalDetector
from vision.animals import analyze

from robot.brain import RobotBrain


camera = ESP32Camera(
    config.CAMERA_STREAM,
    config.VIDEO_FLIP
)


detector = AnimalDetector(
    config.YOLO_MODEL,
    config.YOLO_CONFIDENCE
)


brain = RobotBrain(640)


camera.connect()


while True:

    frame = camera.read()


    if frame is None:
        continue


    result = detector.detect(frame)


    animal = analyze(result)


    action = brain.decide(animal)


    print(
        animal.name,
        "=>",
        action.value
    )


    image = result.plot()


    cv2.imshow(
        "Animal Control Test",
        image
    )


    if cv2.waitKey(1) == ord("q"):
        break


cv2.destroyAllWindows()