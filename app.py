"""
Robot AI Control Center v1.0

Main application.

Python 3.14
"""

from __future__ import annotations

import os
import sys
import signal
import threading
import traceback
from pathlib import Path

import customtkinter as ctk

from core.config import (
    PROJECT_NAME,
    PROJECT_VERSION,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MIN_WIDTH,
    MIN_HEIGHT,
    THEME,
    COLOR_THEME,
)

from core.logger import Logger
from core.state import AppState
from core.events import EventBus

from gui.main_window import MainWindow

from vision.camera import CameraManager
from vision.detector import Detector

from robot.connection import RobotConnection
from robot.controller import RobotController

from ai.search_engine import SearchEngine


class RobotApplication:

    def __init__(self):

        self.root = None

        self.logger = None

        self.state = None

        self.events = None

        self.camera = None

        self.detector = None

        self.robot_connection = None

        self.robot = None

        self.search_engine = None

        self.window = None

        self.running = False

        self.shutdown_event = threading.Event()

    ####################################################################
    # Initialization
    ####################################################################

    def initialize(self):

        self.initialize_gui()

        self.initialize_logger()

        self.logger.info("=======================================")
        self.logger.info(PROJECT_NAME)
        self.logger.info(PROJECT_VERSION)
        self.logger.info("=======================================")

        self.initialize_state()

        self.initialize_events()

        self.initialize_camera()

        self.initialize_detector()

        self.initialize_robot()

        self.initialize_ai()

        self.initialize_window()

        self.register_callbacks()

    ####################################################################

    def initialize_gui(self):

        ctk.set_appearance_mode(THEME)

        ctk.set_default_color_theme(COLOR_THEME)

        self.root = ctk.CTk()

        self.root.title(
            f"{PROJECT_NAME} {PROJECT_VERSION}"
        )

        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.root.minsize(
            MIN_WIDTH,
            MIN_HEIGHT
        )

    ####################################################################

    def initialize_logger(self):

        self.logger = Logger()

    ####################################################################

    def initialize_state(self):

        self.state = AppState()

    ####################################################################

    def initialize_events(self):

        self.events = EventBus()

    ####################################################################

    def initialize_camera(self):

        self.camera = CameraManager(
            logger=self.logger,
            state=self.state,
            events=self.events
        )

    ####################################################################

    def initialize_detector(self):

        self.detector = Detector(
            logger=self.logger,
            state=self.state,
            events=self.events
        )

    ####################################################################

    def initialize_robot(self):

        self.robot_connection = RobotConnection(
            logger=self.logger,
            state=self.state,
            events=self.events
        )

        self.robot = RobotController(
            logger=self.logger,
            state=self.state,
            events=self.events,
            connection=self.robot_connection
        )

    ####################################################################

    def initialize_ai(self):

        self.search_engine = SearchEngine(
            logger=self.logger,
            state=self.state,
            events=self.events,
            robot=self.robot,
            detector=self.detector
        )

    ####################################################################

    def initialize_window(self):

        self.window = MainWindow(
            root=self.root,
            logger=self.logger,
            state=self.state,
            events=self.events,
            camera=self.camera,
            detector=self.detector,
            robot=self.robot,
            ai=self.search_engine
        )

    ####################################################################

    def register_callbacks(self):

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.shutdown
        )

        signal.signal(
            signal.SIGINT,
            self.signal_handler
        )

    ####################################################################
    # Runtime
    ####################################################################

    def start_modules(self):

        self.logger.info(
            "Starting modules..."
        )

        self.camera.start()

        self.detector.start()

        self.robot_connection.start()

        self.search_engine.start()

    ####################################################################

    def stop_modules(self):

        self.logger.info(
            "Stopping modules..."
        )

        try:
            self.search_engine.stop()
        except Exception:
            self.logger.exception(traceback.format_exc())

        try:
            self.detector.stop()
        except Exception:
            self.logger.exception(traceback.format_exc())

        try:
            self.camera.stop()
        except Exception:
            self.logger.exception(traceback.format_exc())

        try:
            self.robot.stop()
        except Exception:
            self.logger.exception(traceback.format_exc())

        try:
            self.robot_connection.stop()
        except Exception:
            self.logger.exception(traceback.format_exc())
    ####################################################################
    # Main Loop
    ####################################################################

    def run(self):

        try:

            self.initialize()

            self.start_modules()

            self.running = True

            self.logger.info("Application started.")

            self.root.mainloop()

        except KeyboardInterrupt:

            self.logger.warning(
                "Keyboard interrupt received."
            )

            self.shutdown()

        except Exception:

            if self.logger is not None:
                self.logger.exception(
                    traceback.format_exc()
                )

            else:
                print(traceback.format_exc())

            self.shutdown()

    ####################################################################
    # Shutdown
    ####################################################################

    def shutdown(self):

        if self.shutdown_event.is_set():
            return

        self.shutdown_event.set()

        self.running = False

        if self.logger:
            self.logger.info(
                "Application shutdown..."
            )

        try:

            self.stop_modules()

        except Exception:

            if self.logger:
                self.logger.exception(
                    traceback.format_exc()
                )

        try:

            if self.window is not None:

                self.window.destroy()

        except Exception:

            if self.logger:
                self.logger.exception(
                    traceback.format_exc()
                )

        try:

            if self.root is not None:

                self.root.quit()

        except Exception:

            pass

        try:

            if self.root is not None:

                self.root.destroy()

        except Exception:

            pass

        if self.logger:

            self.logger.info(
                "Application stopped."
            )

        os._exit(0)

    ####################################################################
    # Signal
    ####################################################################

    def signal_handler(
        self,
        signum,
        frame
    ):

        if self.logger:

            self.logger.info(
                f"Signal received: {signum}"
            )

        self.shutdown()

    ####################################################################
    # Properties
    ####################################################################

    @property
    def version(self):

        return PROJECT_VERSION

    @property
    def name(self):

        return PROJECT_NAME

    @property
    def is_running(self):

        return self.running

    ####################################################################
    # Helpers
    ####################################################################

    def get_state(self):

        return self.state

    def get_robot(self):

        return self.robot

    def get_camera(self):

        return self.camera

    def get_detector(self):

        return self.detector

    def get_event_bus(self):

        return self.events

    def get_logger(self):

        return self.logger

    def get_ai(self):

        return self.search_engine


########################################################################
# Standalone start
########################################################################

def main():

    application = RobotApplication()

    application.run()


if __name__ == "__main__":

    main()
