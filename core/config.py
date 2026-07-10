"""
Robot AI Control Center v1.0

Global configuration.

Author: OpenAI
"""

from pathlib import Path

# ---------------------------------------------------------------------
# PROJECT
# ---------------------------------------------------------------------

PROJECT_NAME = "Robot AI Control Center"
PROJECT_VERSION = "1.0.0"

ROOT = Path(__file__).resolve().parent

ASSETS_DIR = ROOT / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
MODELS_DIR = ROOT / "models"
LOG_DIR = ROOT / "logs"
TEMP_DIR = ROOT / "temp"

LOG_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------

YOLO_MODEL = MODELS_DIR / "yolo11n.pt"

CONFIDENCE = 0.45

TARGET_CLASSES = [
    "cat",
    "dog",
    "bird",
    "horse",
    "cow",
    "sheep",
    "bear",
    "zebra"
]

SEARCH_TIMEOUT = 3

# ---------------------------------------------------------------------
# CAMERA
# ---------------------------------------------------------------------

DEFAULT_CAMERA_URL = "http://192.168.0.18:81/stream"

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# ---------------------------------------------------------------------
# ROBOT
# ---------------------------------------------------------------------

DEFAULT_ROBOT_IP = "192.168.0.18"

COMMAND_TIMEOUT = 2

MOVE_SPEED = 180

TURN_SPEED = 180

FORWARD_TIME = 0.35

TURN_TIME = 0.40

BACKWARD_TIME = 0.30

# ---------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 900

MIN_WIDTH = 1280
MIN_HEIGHT = 720

REFRESH_MS = 30

THEME = "dark"

COLOR_THEME = "blue"

# ---------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------

LOG_LEVEL = "INFO"

LOG_FILE = LOG_DIR / "robot.log"

# ---------------------------------------------------------------------
# SEARCH
# ---------------------------------------------------------------------

AUTO_STOP_ON_TARGET = True

SEARCH_ROTATION_TIME = 0.8

SEARCH_PAUSE = 0.2

# ---------------------------------------------------------------------
# SAFETY
# ---------------------------------------------------------------------

WATCHDOG_TIMEOUT = 5

EMERGENCY_STOP = True

