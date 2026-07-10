import cv2


from core import config


from vision.camera import ESP32Camera
from vision.detector import AnimalDetector
from vision.animals import analyze
from vision.obstacle import ObstacleDetector


from robot.controller import RobotController

from robot.mission import AnimalMission
from robot.obstacle_mission import ObstacleMission
from robot.master_mission import MasterMission


from storage.photo_manager import PhotoManager





# =========================
# Camera
# =========================

camera = ESP32Camera(
    config.CAMERA_STREAM,
    config.VIDEO_FLIP
)




# =========================
# YOLO
# =========================

detector = AnimalDetector(
    config.YOLO_MODEL,
    config.YOLO_CONFIDENCE
)




# =========================
# Robot
# =========================

robot = RobotController(
    config.ROBOT_URL
)




# =========================
# Photo
# =========================

photo = PhotoManager()




# =========================
# Missions
# =========================

animal_mission = AnimalMission(
    robot,
    photo,
    config
)



obstacle_detector = ObstacleDetector()



obstacle_mission = ObstacleMission(
    robot,
    obstacle_detector,
    config
)



mission = MasterMission(
    robot,
    animal_mission,
    obstacle_mission,
    obstacle_detector
)





# =========================
# Start
# =========================

camera.connect()


print(
    "Robot AI запущен"
)




try:


    while True:


        frame = camera.read()


        if frame is None:

            continue



        # -------------------------
        # YOLO
        # -------------------------

        result = detector.detect(
            frame
        )



        animal = analyze(
            result,
            config.ANIMAL_CONFIDENCE
        )



        # ДИАГНОСТИКА

        print(
            "ANIMAL TEST:",
            animal.found,
            animal.name,
            round(animal.confidence, 2),
            animal.center_x
        )




        # -------------------------
        # MAIN LOGIC
        # -------------------------

        mission.update(
            frame,
            animal
        )




        # отображение YOLO

        image = result.plot()



        cv2.imshow(
            "Robot AI",
            image
        )



        if cv2.waitKey(1) == ord("q"):

            robot.stop()

            break




finally:


    robot.stop()

    cv2.destroyAllWindows()