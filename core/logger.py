"""
Robot AI Control Center v1.0

core/logger.py

Единый логгер проекта.
Python 3.14
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

from config import (
    LOG_FILE,
    LOG_LEVEL,
)


class Logger:

    def __init__(self):

        self._logger = logging.getLogger("RobotAI")

        if self._logger.handlers:
            return

        self._logger.setLevel(
            getattr(logging, LOG_LEVEL.upper())
        )

        self._logger.propagate = False

        self._create_log_directory()

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=LOG_FILE,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )

        file_handler.setFormatter(formatter)

        self._logger.addHandler(console)
        self._logger.addHandler(file_handler)

    ####################################################################
    # Internal
    ####################################################################

    @staticmethod
    def _create_log_directory():

        Path(LOG_FILE).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    ####################################################################
    # Standard logging methods
    ####################################################################

    def debug(self, message):

        self._logger.debug(str(message))

    def info(self, message):

        self._logger.info(str(message))

    def warning(self, message):

        self._logger.warning(str(message))

    def error(self, message):

        self._logger.error(str(message))

    def critical(self, message):

        self._logger.critical(str(message))

    def exception(self, message):

        self._logger.exception(str(message))

    ####################################################################
    # Robot specific
    ####################################################################

    def robot(self, message):

        self.info(f"[ROBOT] {message}")

    def camera(self, message):

        self.info(f"[CAMERA] {message}")

    def detector(self, message):

        self.info(f"[YOLO] {message}")

    def ai(self, message):

        self.info(f"[AI] {message}")

    def gui(self, message):

        self.info(f"[GUI] {message}")

    def network(self, message):

        self.info(f"[NETWORK] {message}")

    ####################################################################
    # Section
    ####################################################################

    def section(self, title):

        line = "=" * 70

        self.info(line)
        self.info(title)
        self.info(line)

    ####################################################################
    # Blank line
    ####################################################################

    def blank(self):

        self.info("")

    ####################################################################
    # Shutdown
    ####################################################################

    def shutdown(self):

        logging.shutdown()

    ####################################################################
    # Access
    ####################################################################

    @property
    def logger(self):

        return self._logger