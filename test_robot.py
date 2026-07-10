from robot.controller import RobotController
from core import config
import time


robot = RobotController(
    config.ROBOT_URL
)


print("Вперед")
robot.forward()

time.sleep(2)


print("Стоп")
robot.stop()

time.sleep(1)


print("Поворот налево")
robot.left()

time.sleep(1)


print("Стоп")
robot.stop()