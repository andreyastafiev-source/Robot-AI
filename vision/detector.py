from ultralytics import YOLO


class AnimalDetector:

    def __init__(self, model_path, confidence=0.6):

        print("Загрузка YOLO модели...")

        self.model = YOLO(model_path)

        self.confidence = confidence

        print("YOLO готова")


    def detect(self, frame):

        results = self.model(
            frame,
            conf=self.confidence,
            verbose=False
        )

        return results[0]