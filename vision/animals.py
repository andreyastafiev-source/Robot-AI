class AnimalInfo:


    def __init__(self):

        self.found = False

        self.name = None

        self.confidence = 0

        self.center_x = 0

        self.center_y = 0



# классы животных COCO YOLO

ANIMAL_CLASSES = [

    "cat",
    "dog",
    "bird",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear"

]



def analyze(
        result,
        min_confidence=0.7
):


    animal = AnimalInfo()


    best_confidence = 0



    for box in result.boxes:


        class_id = int(
            box.cls[0]
        )


        name = result.names[class_id]


        confidence = float(
            box.conf[0]
        )



        if name in ANIMAL_CLASSES:


            if (
                confidence >= min_confidence
                and
                confidence > best_confidence
            ):


                best_confidence = confidence


                animal.found = True

                animal.name = name

                animal.confidence = confidence



                coords = box.xyxy[0]


                x1 = int(coords[0])

                y1 = int(coords[1])

                x2 = int(coords[2])

                y2 = int(coords[3])



                animal.center_x = (
                    x1 + x2
                ) // 2


                animal.center_y = (
                    y1 + y2
                ) // 2



    return animal