import cv2
import time


from core import config

from vision.camera import ESP32Camera
from vision.detector import AnimalDetector
from vision.animals import analyze

from storage.photo_manager import PhotoManager


camera = ESP32Camera(
    config.CAMERA_STREAM,
    config.VIDEO_FLIP
)


detector = AnimalDetector(
    config.YOLO_MODEL,
    config.YOLO_CONFIDENCE
)


photo = PhotoManager()


camera.connect()


print("Поиск животных запущен")


saved = False


while True:


    frame = camera.read()


    if frame is None:
        continue



    result = detector.detect(frame)



    animal = analyze(result)



    image = result.plot()



    if animal.found:


        print(
            "Найдено:",
            animal.name,
            "вероятность:",
            round(animal.confidence, 2),
            "X:",
            animal.center_x
        )


        if not saved:


            photo.save(
                frame,
                animal.name,
                animal.confidence
            )


            saved = True



    else:

        saved = False



    cv2.imshow(
        "Animal Photo Test",
        image
    )



    if cv2.waitKey(1) == ord("q"):
        break



cv2.destroyAllWindows()