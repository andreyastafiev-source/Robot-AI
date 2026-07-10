import cv2


from core import config

from vision.camera import ESP32Camera
from vision.obstacle import ObstacleDetector



camera = ESP32Camera(
    config.CAMERA_STREAM,
    config.VIDEO_FLIP
)


detector = ObstacleDetector()



camera.connect()


print(
    "Тест препятствий"
)



while True:


    frame = camera.read()


    if frame is None:

        continue



    result = detector.analyze(
        frame
    )



    if result["obstacle"]:

        text = (
            "ПРЕПЯТСТВИЕ "
            +
            str(
                round(
                    result["value"],
                    3
                )
            )
        )


    else:

        text = (
            "СВОБОДНО "
            +
            str(
                round(
                    result["value"],
                    3
                )
            )
        )



    cv2.putText(
        frame,
        text,
        (20,40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )



    cv2.imshow(
        "Obstacle",
        frame
    )



    if cv2.waitKey(1) == ord("q"):

        break



cv2.destroyAllWindows()