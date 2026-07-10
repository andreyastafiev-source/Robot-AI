"""
Robot AI Control Center v1.0

core/state.py

Глобальное состояние приложения.

Python 3.14
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Any


@dataclass(slots=True)
class DetectionResult:

    class_name: str = ""
    confidence: float = 0.0

    center_x: int = 0
    center_y: int = 0

    width: int = 0
    height: int = 0

    bbox: tuple[int, int, int, int] | None = None


@dataclass(slots=True)
class CameraState:

    connected: bool = False
    streaming: bool = False

    fps: float = 0.0

    frame_width: int = 0
    frame_height: int = 0

    last_frame: Any = None


@dataclass(slots=True)
class RobotState:

    connected: bool = False

    moving: bool = False

    direction: str = "STOP"

    speed: int = 180

    battery: float = 0.0

    last_command: str = ""


@dataclass(slots=True)
class AIState:

    enabled: bool = False

    searching: bool = False

    tracking: bool = False

    target_found: bool = False

    target_name: str = ""

    confidence: float = 0.0

    last_detection: DetectionResult | None = None


class AppState:
    """
    Единое состояние приложения.

    Любой модуль работает только через этот объект.
    """

    def __init__(self):

        self._lock = Lock()

        self.camera = CameraState()

        self.robot = RobotState()

        self.ai = AIState()

    ####################################################################
    # Camera
    ####################################################################

    def set_frame(
        self,
        frame,
        width: int,
        height: int,
        fps: float,
    ):

        with self._lock:

            self.camera.last_frame = frame

            self.camera.frame_width = width
            self.camera.frame_height = height

            self.camera.fps = fps

    ####################################################################

    def set_camera_connected(
        self,
        value: bool,
    ):

        with self._lock:

            self.camera.connected = value

    ####################################################################

    def set_streaming(
        self,
        value: bool,
    ):

        with self._lock:

            self.camera.streaming = value

    ####################################################################
    # Robot
    ####################################################################

    def set_robot_connected(
        self,
        value: bool,
    ):

        with self._lock:

            self.robot.connected = value

    ####################################################################

    def set_robot_direction(
        self,
        direction: str,
    ):

        with self._lock:

            self.robot.direction = direction

            self.robot.moving = direction != "STOP"

    ####################################################################

    def set_speed(
        self,
        speed: int,
    ):

        with self._lock:

            self.robot.speed = speed

    ####################################################################

    def set_last_command(
        self,
        command: str,
    ):

        with self._lock:

            self.robot.last_command = command

    ####################################################################

    def set_battery(
        self,
        value: float,
    ):

        with self._lock:

            self.robot.battery = value

    ####################################################################
    # AI
    ####################################################################

    def enable_ai(
        self,
        value: bool,
    ):

        with self._lock:

            self.ai.enabled = value

    ####################################################################

    def set_searching(
        self,
        value: bool,
    ):

        with self._lock:

            self.ai.searching = value

    ####################################################################

    def set_tracking(
        self,
        value: bool,
    ):

        with self._lock:

            self.ai.tracking = value

    ####################################################################

    def clear_target(self):

        with self._lock:

            self.ai.target_found = False

            self.ai.target_name = ""

            self.ai.confidence = 0.0

            self.ai.last_detection = None

    ####################################################################

    def set_target(
        self,
        result: DetectionResult,
    ):

        with self._lock:

            self.ai.target_found = True

            self.ai.target_name = result.class_name

            self.ai.confidence = result.confidence

            self.ai.last_detection = result

    ####################################################################
    # Snapshot
    ####################################################################

    def snapshot(self) -> dict:

        with self._lock:

            return {

                "camera_connected":
                    self.camera.connected,

                "streaming":
                    self.camera.streaming,

                "fps":
                    self.camera.fps,

                "robot_connected":
                    self.robot.connected,

                "robot_direction":
                    self.robot.direction,

                "robot_speed":
                    self.robot.speed,

                "battery":
                    self.robot.battery,

                "last_command":
                    self.robot.last_command,

                "ai_enabled":
                    self.ai.enabled,

                "searching":
                    self.ai.searching,

                "tracking":
                    self.ai.tracking,

                "target_found":
                    self.ai.target_found,

                "target_name":
                    self.ai.target_name,

                "confidence":
                    self.ai.confidence,
            }

    ####################################################################
    # Reset
    ####################################################################

    def reset(self):

        with self._lock:

            self.camera = CameraState()

            self.robot = RobotState()

            self.ai = AIState()