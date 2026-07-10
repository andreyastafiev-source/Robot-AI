"""
Robot AI Control Center

Entry point.

"""

import sys
import subprocess
import importlib


REQUIRED = [
    "customtkinter",
    "cv2",
    "numpy",
    "PIL",
    "ultralytics",
    "requests",
    "serial",
    "psutil",
    "yaml",
]


def check_packages():

    missing = []

    for package in REQUIRED:

        try:
            importlib.import_module(package)

        except ImportError:
            missing.append(package)

    return missing


def install():

    print()
    print("Installing dependencies...")
    print()

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt"
        ]
    )


def main():

    missing = check_packages()

    if missing:

        print("Missing packages:")
        for item in missing:
            print(" -", item)

        install()

    from app import RobotApplication

    app = RobotApplication()

    app.run()


if __name__ == "__main__":

    main()