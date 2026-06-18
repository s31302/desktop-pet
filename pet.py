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
        # 1. Sprawdź, czy to lewy przycisk myszy
        if event.button() == Qt.MouseButton.LeftButton:
            # 2. Zmień obrazek na "głaskany"
            self.addPixmap(QPixmap("img/happy_cat.png"))
            self.oldPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        # 3. Wróć do zwykłego obrazka po puszczeniu
        self.addPixmap(QPixmap("img/cat.png"))

    def mouseMoveEvent(self, event):
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

    def addPixmap(self, pixmap: QPixmap):
        if pixmap.isNull():
            print("ERROR: Nie znaleziono obrazka!")
        else:
            self.label.setPixmap(pixmap)
            self.label.setScaledContents(True)
            self.label.resize(200, 200)


app = QApplication(sys.argv)
pet = DesktopPet()
pet.show()
sys.exit(app.exec())