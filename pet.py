import sys

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import Qt

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 200, 200)

        self.label = QLabel(self)
        pixmap = QPixmap("img/cat.png")
        if pixmap.isNull():
            print("ERROR: Nie znaleziono obrazka!")
        else:
            self.label.setPixmap(pixmap)
            self.label.setScaledContents(True)
            self.label.resize(200, 200)

    def mousePressEvent(self, event):
        # Pozwala przeciągać okno za pomocą myszki
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

app = QApplication(sys.argv)
pet = DesktopPet()
pet.show()
sys.exit(app.exec())