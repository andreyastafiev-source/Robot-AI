import cv2

from core import config

from vision.camera import ESP32Camera
from vision.detector import AnimalDetector
from vision.animals import analyze

from robot.controller import RobotController
from robot.brain import RobotBrain
from robot.executor import RobotExecutor


camera = ESP32Camera(
    config.CAMERA_STREAM,
    config.VIDEO_FLIP
)


detector = AnimalDetector(
    config.YOLO_MODEL,
    config.YOLO_CONFIDENCE
)


robot = RobotController(
    config.ROBOT_URL
)


executor = RobotExecutor(robot)


brain = RobotBrain(640)


camera.connect()


print("Система запущена")


while True:

    frame = camera.read()

    if frame is None:
        continue


    result = detector.detect(frame)


    animal = analyze(result)


    action = brain.decide(animal)


    print(
        "Команда:",
        action.value
    )


    # ВАЖНО:
    # пока отключаем автоматическое движение
    # executor.execute(action)


    image = result.plot()


    cv2.imshow(
        "Robot AI Test",
        image
    )


    if cv2.waitKey(1) == ord("q"):
        break


cv2.destroyAllWindows()