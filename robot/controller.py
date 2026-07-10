import requests


class RobotController:

    def __init__(self, robot_url):
        self.base_url = robot_url


    def send_command(self, command):

        try:

            url = f"{self.base_url}/{command}"

            response = requests.get(
                url,
                timeout=2
            )

            if response.text == "OK":
                print(f"OK: {command}")
            else:
                print(
                    f"Ответ робота: {response.text}"
                )


        except Exception as e:

            print(
                f"Ошибка связи с роботом: {e}"
            )


    def forward(self):
        self.send_command("forward")


    def back(self):
        self.send_command("back")


    def left(self):
        self.send_command("left")


    def right(self):
        self.send_command("right")


    def stop(self):
        self.send_command("stop")