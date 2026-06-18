import sys
import os
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QIcon


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        # 1. Ustawienia okna
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.oldPos = None
        self.setGeometry(100, 100, 128, 128)

        # 2. Wygląd i grafika
        self.label = QLabel(self)
        self.label.setFixedSize(128, 128)
        self.label.setScaledContents(True)

        # BEZPIECZNA ŚCIEŻKA:
        base_dir = os.path.dirname(sys.argv[0])
        img_path = os.path.join(base_dir, "img", "ExportedLayers.png")
        self.sprite_sheet = QPixmap(img_path)
        self.frame_size = 256

        # 3. Definicja sekwencji
        self.seq_idle = [0, 1, 2, 1]  # Rząd 0: machanie ogonkiem
        self.seq_walk = [0, 1, 2, 1, 2, 1, 2, 0]  # Rząd 1: chodzenie

        # 4. Inicjalizacja Maszyny Stanów (FSM)
        self.state = "idle"  # Aktualny stan: idle, idle_animate, walking
        self.animation_seq = [0]  # Domyślnie stoi (klatka 0)
        self.frame_idx = 0  # Numer klatki w sekwencji
        self.current_row = 0  # 0=przód, 1=bok
        self.direction = "left"  # Kierunek ruchu

        # 5. Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(200)

        self.show()
        # Wymuś ustawienie na pasku zadań od razu po pokazaniu
        self.update_position_on_taskbar()

        # Stworzenie ikony w zasobniku obok zegarka
        self.tray_icon = QSystemTrayIcon(self)

        # Jako ikonkę w zasobniku wykorzystamy pierwszą klatkę Twojego kota
        first_frame = self.sprite_sheet.copy(0, 0, self.frame_size, self.frame_size)
        self.tray_icon.setIcon(QIcon(first_frame))

        # Stworzenie menu pod prawym przyciskiem myszy
        tray_menu = QMenu()

        # 1. NOWA AKCJA: Pokaż / Ukryj
        self.toggle_action = QAction("Ukryj zwierzaka", self)
        self.toggle_action.triggered.connect(self.toggle_pet)  # Podpięcie funkcji
        tray_menu.addAction(self.toggle_action)

        # Dodanie akcji "Wyjście"
        exit_action = QAction("Wyłącz zwierzaka", self)
        exit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(exit_action)

        # Przypisanie menu do ikonki i pokazanie jej
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def animate(self):
        # Sprawdzanie, czy sekwencja się skończyła
        if self.frame_idx >= len(self.animation_seq):
            if self.state == "walking":
                # Zmiana kierunku po dojściu do końca sekwencji chodu
                if self.direction == "left":
                    self.direction = "right"
                    self.frame_idx = 0  # Idzie z powrotem
                else:
                    self.direction = "left"
                    self.state = "idle"
                    self.current_row = 0
                    self.animation_seq = [0]  # Koniec chodzenia, wraca do siedzenia
            elif self.state == "idle_animate":
                self.state = "idle"
                self.animation_seq = [0]

            # Zerujemy indeks, jeśli zmieniliśmy sekwencję
            if self.frame_idx >= len(self.animation_seq):
                self.frame_idx = 0

        # Wybór odpowiedniej kolumny z sekwencji
        current_col = self.animation_seq[self.frame_idx]
        self.frame_idx += 1

        # Wycinanie grafiki
        x = current_col * self.frame_size
        y = self.current_row * self.frame_size
        frame = self.sprite_sheet.copy(x, y, self.frame_size, self.frame_size)

        # Odbicie lustrzane, jeśli idzie w prawo
        if self.direction == "right":
            frame = frame.transformed(QTransform().scale(-1, 1))

        self.label.setPixmap(frame)

        # Fizyczny ruch po ekranie (tylko X)
        if self.state == "walking":
            if self.direction == "left":
                self.move(self.x() - 10, self.y())
            else:
                self.move(self.x() + 10, self.y())

        # ZAWSZE wymuszaj trzymanie się paska zadań (grawitacja)
        self.update_position_on_taskbar()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

            if self.state == "idle":
                self.state = "idle_animate"
                self.animation_seq = self.seq_idle
                self.current_row = 0
                self.frame_idx = 0

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.state = "walking"
            self.animation_seq = self.seq_walk
            self.current_row = 1
            self.frame_idx = 0
            self.direction = "left"

    def mouseMoveEvent(self, event):
        if self.oldPos is not None:
            delta = event.globalPosition().toPoint() - self.oldPos

            # Przesuwamy TYLKO oś X (lewo-prawo). Oś Y jest ignorowana przy przeciąganiu.
            new_x = self.x() + delta.x()
            self.move(new_x, self.y())

            self.oldPos = event.globalPosition().toPoint()

    def update_position_on_taskbar(self):
        # availableGeometry() zwraca obszar ekranu BEZ paska zadań.
        # bottom() to dolna krawędź tego obszaru (czyli idealnie na styku z paskiem).
        screen_bottom = QApplication.primaryScreen().availableGeometry().bottom()
        y_offset = 38


        # Odejmujemy wysokość zwierzaka, żeby jego dół dotykał paska (+1 dla idealnego wyrównania)
        y_position = screen_bottom - self.height() + y_offset

        self.move(self.x(), y_position)

    def toggle_pet(self):
        if self.isVisible():
            self.hide()  # Ukrywamy okno
            self.toggle_action.setText("Pokaż zwierzaka")  # Zmieniamy tekst w menu
        else:
            self.show()  # Pokazujemy okno
            self.update_position_on_taskbar()  # Upewniamy się, że stoi na pasku
            self.toggle_action.setText("Ukryj zwierzaka")  # Zmieniamy tekst z powrotem


app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
pet = DesktopPet()
pet.show()
sys.exit(app.exec())