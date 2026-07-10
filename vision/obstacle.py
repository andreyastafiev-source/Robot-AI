import cv2
import numpy as np



class ObstacleDetector:


    def __init__(self):

        self.reference = None

        # по вашим измерениям:
        # свободно: 0.002-0.003
        # препятствие: 0.1-0.2

        self.threshold = 0.05



    def reset_reference(self):

        """
        Сброс эталонного кадра.
        Вызывается после поворота робота,
        чтобы новый путь стал новым эталоном.
        """

        self.reference = None



    def analyze(self, frame):


        if frame is None:

            return None



        height, width = frame.shape[:2]



        # зона перед роботом

        roi = frame[
            int(height * 0.55):height,
            :
        ]



        small = cv2.resize(
            roi,
            (160, 80)
        )



        gray = cv2.cvtColor(
            small,
            cv2.COLOR_BGR2GRAY
        )



        # первый кадр после запуска
        # считаем свободным путем

        if self.reference is None:


            self.reference = gray.copy()


            return {

                "left": 0.0,
                "center": 0.0,
                "right": 0.0,

                "left_blocked": False,
                "center_blocked": False,
                "right_blocked": False,

                "obstacle": False,

                "direction": "forward"

            }



        result = {}



        image_width = gray.shape[1]


        zones = {


            "left":
            (
                0,
                image_width // 3
            ),


            "center":
            (
                image_width // 3,
                image_width * 2 // 3
            ),


            "right":
            (
                image_width * 2 // 3,
                image_width
            )

        }



        for name, (x1, x2) in zones.items():


            current_zone = gray[:, x1:x2]


            reference_zone = self.reference[:, x1:x2]



            diff = cv2.absdiff(
                reference_zone,
                current_zone
            )



            value = np.mean(diff) / 255



            result[name] = round(
                float(value),
                3
            )



        result["left_blocked"] = (

            result["left"]
            >
            self.threshold

        )


        result["center_blocked"] = (

            result["center"]
            >
            self.threshold

        )


        result["right_blocked"] = (

            result["right"]
            >
            self.threshold

        )



        result["obstacle"] = (

            result["center_blocked"]

        )



        # выбор направления

        if result["obstacle"]:


            if result["left"] < result["right"]:

                result["direction"] = "left"


            else:

                result["direction"] = "right"



        else:


            result["direction"] = "forward"



        return result