import os
from datetime import datetime
import cv2


class PhotoManager:

    def __init__(self, folder="photos"):

        self.folder = folder

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)


    def save(self, frame, animal_name="unknown", confidence=0):

        if frame is None:
            print("Ошибка: пустой кадр")
            return None


        now = datetime.now()
        day_folder = os.path.join(self.folder, now.strftime("%Y-%m-%d"))
        os.makedirs(day_folder, exist_ok=True)
        timestamp = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]


        confidence_text = int(
            confidence * 100
        )


        filename = (
            f"{animal_name}_{confidence_text}%_{timestamp}.jpg"
        )


        path = os.path.join(
            day_folder,
            filename
        )


        result = cv2.imwrite(
            path,
            frame
        )


        if result:

            print(
                "Фото сохранено:",
                path
            )

            return path

        else:

            print(
                "Ошибка сохранения фото"
            )

            return None
