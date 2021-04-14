from PyQt5.QtWidgets import QMainWindow,QApplication
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtGui import QPixmap
import keyboard
from PyQt5.QtCore import Qt
import requests
import sys


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/untitled.ui', self)
        self.z = 7
        self.search.clicked.connect(self.fine_new)

    def fine_new(self):
        if len(self.place.text()) < 4:
            return
        geo_link = 'https://geocode-maps.yandex.ru/1.x'
        params_geo = {
            'geocode': self.place.text(),
            'apikey': '33c50873-3bf9-406f-8799-464a3980ef2d',
            'format': 'json',
        }
        response = requests.get(geo_link, params_geo).json()
        try:
            toponym = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
            self.first_cords = tuple(map(float, toponym['Point']['pos'].split()))
            static_link = 'https://static-maps.yandex.ru/1.x'
            params_static = {
                'll': ','.join(map(str, self.first_cords)),
                'l': 'map',
                'z': self.z
            }
            response = requests.get(static_link, params_static)
            with open('map.jpg', 'wb') as file:
                file.write(response.content)
            self.pixmap = QPixmap('map.jpg')
            self.img.setPixmap(self.pixmap)
            self.img.setFocus()
        except Exception:
            pass

    def onlyStatic(self):
        try:
            static_link = 'https://static-maps.yandex.ru/1.x'
            params_static = {
                'll': ','.join(map(str, self.first_cords)),
                'l': 'map',
                'z': self.z
            }
            response = requests.get(static_link, params_static)
            with open('map.jpg', 'wb') as file:
                file.write(response.content)
            self.pixmap = QPixmap('map.jpg')
            self.img.setPixmap(self.pixmap)
            self.img.setFocus()
        except Exception:
            pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.z += 1
        if event.key() == Qt.Key_PageDown:
            self.z -= 1
        if event.key() == Qt.Key_Up:
            self.first_cords = (self.first_cords[0], self.first_cords[1] + 1/self.z)
        if event.key() == Qt.Key_Down:
            self.first_cords = (self.first_cords[0], self.first_cords[1] - 1/self.z)
        if event.key() == Qt.Key_Left:
            self.first_cords = (self.first_cords[0] - 1/self.z, self.first_cords[1])
        if event.key() == Qt.Key_Right:
            self.first_cords = (self.first_cords[0] + 1/self.z, self.first_cords[1])
        self.onlyStatic()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())