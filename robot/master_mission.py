from enum import Enum



class MasterState(Enum):

    SEARCH = 1
    ANIMAL = 2
    OBSTACLE = 3




class MasterMission:


    def __init__(
            self,
            robot,
            animal_mission,
            obstacle_mission,
            obstacle_detector
    ):


        self.robot = robot

        self.animal_mission = animal_mission

        self.obstacle_mission = obstacle_mission

        self.obstacle_detector = obstacle_detector


        self.state = MasterState.SEARCH


        self.animal_active = False



    def update(
            self,
            frame,
            animal
    ):



        # ======================
        # Уже фотографируем животное
        # ======================

        if self.animal_active:


            self.animal_mission.update(
                frame,
                animal
            )


            if self.animal_mission.finished:


                print(
                    "Животное обработано"
                )


                self.animal_active = False


            return




        # ======================
        # Новое животное
        # ======================

        if animal.found:


            print(
                "Запуск AnimalMission"
            )


            self.animal_active = True


            self.robot.stop()


            self.animal_mission.update(
                frame,
                animal
            )


            return




        # ======================
        # Препятствия
        # ======================

        obstacle = self.obstacle_detector.analyze(
            frame
        )



        if obstacle["obstacle"]:


            self.obstacle_mission.update(
                frame
            )


            return




        # ======================
        # Свободный путь
        # ======================

        self.robot.forward()