from robot.search_mode import SearchMode
from vision.animals import AnimalInfo


mode = SearchMode(640)


animal = AnimalInfo()


print("Нет животного:")
print(
    mode.process(animal)
)


print()


print("Животное слева:")

animal.found = True
animal.center_x = 100

print(
    mode.process(animal)
)


print()


print("Животное справа:")

animal.center_x = 550

print(
    mode.process(animal)
)


print()


print("Животное по центру:")

animal.center_x = 320

print(
    mode.process(animal)
)