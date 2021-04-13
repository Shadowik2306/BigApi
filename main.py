from PyQt5.QtWidgets import QMainWindow,QApplication
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtGui import QPixmap
import requests
import sys


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/untitled.ui', self)
        self.place.textChanged.connect(self.fine_new)

    def fine_new(self):
        if len(self.place.text()) < 4:
            return
        geo_link = 'https://geocode-maps.yandex.ru/1.x'
        params_geo = {
            'geocode': self.place.text(),
            'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
            'format': 'json'
        }
        response = requests.get(geo_link, params_geo).json()
        try:
            toponym = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
            first_cords = tuple(map(float, toponym['Point']['pos'].split()))
            static_link = 'https://static-maps.yandex.ru/1.x'
            params_static = {
                'll': ','.join(map(str, first_cords)),
                'l': 'map',
            }
            response = requests.get(static_link, params_static)
            with open('map.jpg', 'wb') as file:
                file.write(response.content)
            self.pixmap = QPixmap('map.jpg')
            self.img.setPixmap(self.pixmap)
        except Exception:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())