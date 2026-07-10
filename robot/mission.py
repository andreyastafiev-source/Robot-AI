import time
from enum import Enum



class MissionState(Enum):

    SEARCH = 1
    ANIMAL_FOUND = 2
    PHOTO_1 = 3
    TURN_TO_ANIMAL = 4
    PHOTO_2 = 5
    RETURN = 6
    COOLDOWN = 7




class AnimalMission:


    def __init__(
            self,
            robot,
            photo_manager,
            config
    ):

        self.robot = robot

        self.photo = photo_manager

        self.config = config


        self.state = MissionState.SEARCH


        self.confirm_count = 0


        self.last_direction = None


        self.cooldown_start = 0


        self.moving = False


        # показывает, что цикл с животным завершен

        self.finished = True




    def update(
            self,
            frame,
            animal
    ):


        # =========================
        # SEARCH
        # =========================

        if self.state == MissionState.SEARCH:


            self.finished = False



            if not self.moving:


                print(
                    "Поиск: движение вперед"
                )


                self.robot.forward()


                self.moving = True




            if animal.found:


                self.confirm_count += 1


                print(
                    "Подтверждение животного:",
                    self.confirm_count
                )



                if (
                    self.confirm_count
                    >=
                    self.config.CONFIRM_FRAMES
                ):


                    self.state = MissionState.ANIMAL_FOUND



            else:


                self.confirm_count = 0





        # =========================
        # ANIMAL FOUND
        # =========================

        elif self.state == MissionState.ANIMAL_FOUND:


            print(
                "Животное найдено:",
                animal.name,
                "confidence:",
                round(animal.confidence,2),
                "X:",
                animal.center_x
            )


            self.robot.stop()


            self.moving = False



            time.sleep(
                self.config.PHOTO_DELAY
            )


            self.state = MissionState.PHOTO_1





        # =========================
        # PHOTO 1
        # =========================

        elif self.state == MissionState.PHOTO_1:


            print(
                "Фото 1"
            )


            self.photo.save(
                frame,
                animal.name,
                animal.confidence
            )



            frame_center = 320



            if animal.center_x < frame_center - 80:


                self.last_direction = "left"



            elif animal.center_x > frame_center + 80:


                self.last_direction = "right"



            else:


                self.last_direction = None



            self.state = MissionState.TURN_TO_ANIMAL





        # =========================
        # TURN
        # =========================

        elif self.state == MissionState.TURN_TO_ANIMAL:



            if self.last_direction == "left":


                print(
                    "Поворот влево"
                )


                self.robot.left()


                time.sleep(
                    self.config.TURN_TIME
                )



            elif self.last_direction == "right":


                print(
                    "Поворот вправо"
                )


                self.robot.right()


                time.sleep(
                    self.config.TURN_TIME
                )



            self.robot.stop()



            time.sleep(
                self.config.SECOND_PHOTO_DELAY
            )



            self.state = MissionState.PHOTO_2





        # =========================
        # PHOTO 2
        # =========================

        elif self.state == MissionState.PHOTO_2:


            print(
                "Фото 2"
            )


            self.photo.save(
                frame,
                animal.name,
                animal.confidence
            )


            self.state = MissionState.RETURN





        # =========================
        # RETURN
        # =========================

        elif self.state == MissionState.RETURN:



            if self.last_direction == "left":


                print(
                    "Возврат вправо"
                )


                self.robot.right()


                time.sleep(
                    self.config.TURN_TIME
                )



            elif self.last_direction == "right":


                print(
                    "Возврат влево"
                )


                self.robot.left()


                time.sleep(
                    self.config.TURN_TIME
                )



            self.robot.stop()


            self.cooldown_start = time.time()


            self.state = MissionState.COOLDOWN





        # =========================
        # COOLDOWN
        # =========================

        elif self.state == MissionState.COOLDOWN:



            if (
                time.time()
                -
                self.cooldown_start
                >=
                self.config.IGNORE_TIME
            ):


                print(
                    "Возврат в поиск"
                )


                self.confirm_count = 0


                self.last_direction = None


                self.state = MissionState.SEARCH


                self.finished = True