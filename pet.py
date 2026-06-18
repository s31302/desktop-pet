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
        self.set_image("cat.png")

    def mousePressEvent(self, event):
        # 1. Sprawdź, czy to lewy przycisk myszy
        if event.button() == Qt.MouseButton.LeftButton:
            # 2. Zmień obrazek na "głaskany"
            self.set_image("happy_cat.png")
            self.oldPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        # 3. Wróć do zwykłego obrazka po puszczeniu
        self.set_image("cat.png")

    def mouseMoveEvent(self, event):
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

    def set_image(self, filename):
        path = f"img/{filename}"
        pixmap = QPixmap(path)

        if pixmap.isNull():
            print("ERROR: Nie znaleziono: {path}!")
        else:
            self.label.setPixmap(pixmap)
            self.label.setScaledContents(True)
            self.label.resize(200, 200)


app = QApplication(sys.argv)
pet = DesktopPet()
pet.show()
sys.exit(app.exec())