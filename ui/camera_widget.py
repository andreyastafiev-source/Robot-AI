from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap



class CameraWidget(QLabel):


    def __init__(self):

        super().__init__()


        self.setAlignment(
            Qt.AlignCenter
        )


        self.setText(
            "Camera offline"
        )


        self.setMinimumSize(
            800,
            450
        )



    def update_frame(
            self,
            frame
    ):


        if frame is None:

            return



        rgb = frame[:, :, ::-1]



        h, w, ch = rgb.shape


        bytes_per_line = ch * w



        image = QImage(
            rgb.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
        )



        self.setPixmap(
            QPixmap.fromImage(image)
        )