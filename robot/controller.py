"""Thread-safe HTTP controller that sends commands only when state changes."""
import threading
import requests

class RobotController:
    def __init__(self, robot_url, timeout=2):
        self.base_url = robot_url.rstrip("/")
        self.timeout = timeout
        self.current_command = "stop"
        self.lock = threading.RLock()

    def send_command(self, command, force=False):
        with self.lock:
            if command == self.current_command and not force:
                return True
            try:
                response = requests.get(f"{self.base_url}/{command}", timeout=self.timeout)
                response.raise_for_status()
                if response.text.strip() != "OK":
                    print("Ответ робота:", response.text)
                    return False
                if not command.startswith("light/"):
                    self.current_command = command
                print("OK:", command)
                return True
            except Exception as error:
                print("Ошибка связи с роботом:", error)
                return False

    def forward(self): return self.send_command("forward")
    def back(self): return self.send_command("back")
    def left(self): return self.send_command("left")
    def right(self): return self.send_command("right")
    def stop(self): return self.send_command("stop", force=True)
    def light_on(self): return self.send_command("light/on", force=True)
    def light_off(self): return self.send_command("light/off", force=True)
