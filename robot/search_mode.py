from robot.brain import RobotBrain


class SearchMode:

    def __init__(self, frame_width):

        self.brain = RobotBrain(frame_width)


    def process(self, animal):

        action = self.brain.decide(animal)

        return action.value