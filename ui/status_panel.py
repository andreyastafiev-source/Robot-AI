from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel
)



class StatusPanel(QWidget):


    def __init__(self):

        super().__init__()


        layout = QVBoxLayout()



        self.mode = QLabel(
            "Mode: MANUAL"
        )


        self.animal = QLabel(
            "Animal: none"
        )


        self.photos = QLabel(
            "Photos: 0"
        )


        self.status = QLabel(
            "Status: Ready"
        )



        layout.addWidget(
            self.mode
        )

        layout.addWidget(
            self.animal
        )

        layout.addWidget(
            self.photos
        )

        layout.addWidget(
            self.status
        )



        self.setLayout(
            layout
        )



    def set_status(
            self,
            text
    ):

        self.status.setText(
            "Status: " + text
        )