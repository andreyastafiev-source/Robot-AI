import requests
import cv2
import numpy as np
import threading



class ESP32Camera:


    def __init__(
            self,
            stream_url,
            flip=False
    ):

        self.stream_url = stream_url

        self.flip = flip

        print("FLIP MODE:", self.flip)

        self.stream = None

        self.bytes_data = b""

        # хранит только последний актуальный кадр
        self.frame = None

        self.running = False

        self.thread = None



    def connect(self):

        print("Подключение к камере...")


        self.stream = requests.get(
            self.stream_url,
            stream=True,
            timeout=10
        )


        self.running = True


        self.thread = threading.Thread(
            target=self._capture_loop,
            daemon=True
        )


        self.thread.start()


        print("Камера подключена")



    def _capture_loop(self):

        try:

            for chunk in self.stream.iter_content(
                    chunk_size=1024
            ):


                if not self.running:
                    break


                self.bytes_data += chunk



                start = self.bytes_data.find(
                    b'\xff\xd8'
                )


                end = self.bytes_data.find(
                    b'\xff\xd9'
                )



                if start != -1 and end != -1:


                    jpg = self.bytes_data[
                        start:end + 2
                    ]


                    self.bytes_data = self.bytes_data[
                        end + 2:
                    ]



                    image = cv2.imdecode(
                        np.frombuffer(
                            jpg,
                            dtype=np.uint8
                        ),
                        cv2.IMREAD_COLOR
                    )



                    if image is not None:


                        # Исправление ориентации камеры
                        #
                        # True = переворот на 180 градусов
                        #
                        # если понадобится только зеркало:
                        # заменить -1 на 1

                        if self.flip:

                            image = cv2.flip(
                                image,
                                -1
                            )



                        # всегда хранится только последний кадр

                        self.frame = image



        except Exception as e:

            print(
                "Ошибка камеры:",
                e
            )



    def read(self):

        return self.frame



    def stop(self):

        self.running = False


        if self.stream:

            self.stream.close()