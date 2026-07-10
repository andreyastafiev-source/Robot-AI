import time

from enum import Enum



class ObstacleState(Enum):

    FORWARD = 1
    STOP = 2
    TURN = 3
    BACK = 4
    WAIT = 5
    CHECK = 6




class ObstacleMission:


    def __init__(
            self,
            robot,
            obstacle_detector,
            config
    ):


        self.robot = robot

        self.detector = obstacle_detector

        self.config = config


        self.state = ObstacleState.FORWARD


        self.turn_direction = "left"


        self.timer = 0


        # время движения назад

        self.back_time = 0.6


        # время поворота

        self.turn_time = config.TURN_TIME




    def all_blocked(self, result):

        return (

            result["left"] < 0.03
            and
            result["center"] < 0.03
            and
            result["right"] < 0.03

        )




    def choose_direction(self, result):


        # выбираем более свободную сторону

        if result["left"] < result["right"]:

            return "left"

        else:

            return "right"





    def update(self, frame):


        result = self.detector.analyze(frame)


        if result is None:

            return




        # ==========================
        # Движение вперед
        # ==========================

        if self.state == ObstacleState.FORWARD:


            if result["obstacle"]:


                print(
                    "Препятствие"
                )


                self.robot.stop()



                # полная блокировка

                if self.all_blocked(result):


                    print(
                        "Зажат. Назад."
                    )


                    self.timer = time.time()


                    self.state = ObstacleState.BACK



                else:


                    self.turn_direction = (
                        self.choose_direction(result)
                    )


                    self.timer = time.time()


                    self.state = ObstacleState.TURN



            else:


                self.robot.forward()



        # ==========================
        # Отъезд назад
        # ==========================

        elif self.state == ObstacleState.BACK:


            self.robot.back()



            if (
                time.time()
                -
                self.timer
                >
                self.back_time
            ):


                self.robot.stop()


                print(
                    "Назад выполнено"
                )


                # меняем направление

                if self.turn_direction == "left":

                    self.turn_direction = "right"

                else:

                    self.turn_direction = "left"



                self.timer = time.time()


                self.state = ObstacleState.TURN




        # ==========================
        # Поворот
        # ==========================

        elif self.state == ObstacleState.TURN:


            if self.turn_direction == "left":


                print(
                    "Поворот LEFT"
                )


                self.robot.left()



            else:


                print(
                    "Поворот RIGHT"
                )


                self.robot.right()




            if (
                time.time()
                -
                self.timer
                >
                self.turn_time
            ):


                self.robot.stop()


                print(
                    "Поворот закончен"
                )


                self.timer = time.time()


                self.state = ObstacleState.WAIT





        # ==========================
        # Ждем стабилизацию камеры
        # ==========================

        elif self.state == ObstacleState.WAIT:


            if (
                time.time()
                -
                self.timer
                >
                0.5
            ):


                self.detector.reset_reference()


                self.state = ObstacleState.CHECK





        # ==========================
        # Проверка нового пути
        # ==========================

        elif self.state == ObstacleState.CHECK:


            result = self.detector.analyze(frame)



            if not result["obstacle"]:


                print(
                    "Путь свободен"
                )


                self.state = ObstacleState.FORWARD



            else:


                print(
                    "Еще закрыто"
                )


                self.turn_direction = (
                    self.choose_direction(result)
                )


                self.timer = time.time()


                self.state = ObstacleState.TURN