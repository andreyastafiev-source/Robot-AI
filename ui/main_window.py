from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout
)


from ui.camera_widget import CameraWidget

from ui.control_panel import ControlPanel

from ui.status_panel import StatusPanel



class MainWindow(QMainWindow):


    def __init__(self):

        super().__init__()



        self.setWindowTitle(
            "Robot AI Control Center"
        )


        self.resize(
            1200,
            800
        )



        root = QWidget()



        main_layout = QHBoxLayout()



        left = QVBoxLayout()



        self.camera = CameraWidget()

        self.status = StatusPanel()



        left.addWidget(
            self.camera
        )


        left.addWidget(
            self.status
        )



        self.control = ControlPanel()



        main_layout.addLayout(
            left
        )


        main_layout.addWidget(
            self.control
        )



        root.setLayout(
            main_layout
        )


        self.setCentralWidget(
            root
        )