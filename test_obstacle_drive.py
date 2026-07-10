from core import config

from vision.camera import ESP32Camera
from vision.obstacle import ObstacleDetector

from robot.controller import RobotController
from robot.obstacle_mission import ObstacleMission



camera = ESP32Camera(
    config.CAMERA_STREAM,
    config.VIDEO_FLIP
)



robot = RobotController(
    config.ROBOT_URL
)



detector = ObstacleDetector()



mission = ObstacleMission(
    robot,
    detector,
    config
)



camera.connect()


print(
    "Тест обхода препятствий"
)



while True:


    frame = camera.read()


    if frame is None:

        continue



    mission.update(frame)