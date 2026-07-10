from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QRadioButton
)

from PySide6.QtCore import Signal



class ControlPanel(QWidget):


    command = Signal(str)

    mode_changed = Signal(str)



    def __init__(self):

        super().__init__()


        layout = QVBoxLayout()



        self.title = QLabel(
            "Control"
        )


        layout.addWidget(
            self.title
        )



        self.forward_btn = QPushButton(
            "↑ Forward"
        )


        self.left_btn = QPushButton(
            "← Left"
        )


        self.stop_btn = QPushButton(
            "■ STOP"
        )


        self.right_btn = QPushButton(
            "Right →"
        )


        self.back_btn = QPushButton(
            "↓ Back"
        )



        layout.addWidget(
            self.forward_btn
        )

        layout.addWidget(
            self.left_btn
        )

        layout.addWidget(
            self.stop_btn
        )

        layout.addWidget(
            self.right_btn
        )

        layout.addWidget(
            self.back_btn
        )



        layout.addWidget(
            QLabel("Mode")
        )



        self.manual = QRadioButton(
            "Manual"
        )


        self.auto = QRadioButton(
            "Auto"
        )


        self.manual.setChecked(
            True
        )


        layout.addWidget(
            self.manual
        )


        layout.addWidget(
            self.auto
        )



        self.setLayout(
            layout
        )



        self.forward_btn.clicked.connect(
            lambda: self.command.emit("forward")
        )


        self.left_btn.clicked.connect(
            lambda: self.command.emit("left")
        )


        self.right_btn.clicked.connect(
            lambda: self.command.emit("right")
        )


        self.back_btn.clicked.connect(
            lambda: self.command.emit("back")
        )


        self.stop_btn.clicked.connect(
            lambda: self.command.emit("stop")
        )



        self.manual.clicked.connect(
            lambda:
            self.mode_changed.emit("MANUAL")
        )


        self.auto.clicked.connect(
            lambda:
            self.mode_changed.emit("AUTO")
        )