from robot.brain import RobotBrain


class AnimalSearchMode:

    def __init__(self, frame_width):

        self.brain = RobotBrain(frame_width)


    def get_action(self, animal):

        return self.brain.decide(animal)