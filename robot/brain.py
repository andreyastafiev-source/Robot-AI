from enum import Enum


class RobotAction(Enum):

    STOP = "stop"
    FORWARD = "forward"
    LEFT = "left"
    RIGHT = "right"



class RobotBrain:

    def __init__(self, frame_width):

        self.frame_width = frame_width


    def decide(self, animal):

        if not animal.found:

            return RobotAction.FORWARD


        center = self.frame_width // 2


        # зона в центре кадра
        tolerance = 80


        if animal.center_x < center - tolerance:

            return RobotAction.LEFT


        elif animal.center_x > center + tolerance:

            return RobotAction.RIGHT


        else:

            return RobotAction.STOP