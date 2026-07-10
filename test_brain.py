from robot.brain import RobotBrain
from vision.animals import AnimalInfo


brain = RobotBrain(640)


# нет животного

animal = AnimalInfo()

print(
    brain.decide(animal)
)


# животное слева

animal.found = True
animal.center_x = 100

print(
    brain.decide(animal)
)


# животное справа

animal.center_x = 550

print(
    brain.decide(animal)
)


# животное по центру

animal.center_x = 320

print(
    brain.decide(animal)
)