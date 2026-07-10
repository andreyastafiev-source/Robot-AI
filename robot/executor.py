import time


class RobotExecutor:

    def __init__(self, robot):

        self.robot = robot


    def execute(self, action):

        command = action.value

        print("Выполняю:", command)


        if command == "forward":

            self.robot.forward()
            time.sleep(0.3)
            self.robot.stop()


        elif command == "left":

            self.robot.left()
            time.sleep(0.3)
            self.robot.stop()


        elif command == "right":

            self.robot.right()
            time.sleep(0.3)
            self.robot.stop()


        elif command == "stop":

            self.robot.stop()