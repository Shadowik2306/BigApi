from PyQt5.QtWidgets import QMainWindow,QApplication
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtGui import QPixmap
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
        self.l = 'map'
        self.change = [0, 0]
        self.point = False
        self.view.clicked.connect(self.change_view)
        self.search.clicked.connect(self.fine_new)
        self.delPointBut.clicked.connect(self.delPoint)

    def fine_new(self):
        self.point = True
        self.change = [0, 0]
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
            self.addressLabel.setText(toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted'])
            self.first_cords = tuple(map(float, toponym['Point']['pos'].split()))
            self.onlyStatic()
            self.img.setFocus()
        except Exception:
            pass

    def onlyStatic(self):
        try:
            static_link = 'https://static-maps.yandex.ru/1.x'
            params_static = {
                'll': ','.join(map(str, (self.first_cords[0] + self.change[0],
                                         self.first_cords[1] + self.change[1]))),
                'l': self.l,
                'z': self.z
            }
            if self.point:
                params_static['pt'] = f'{self.first_cords[0]},{self.first_cords[1]},pm2rdm'
            response = requests.get(static_link, params_static)
            with open('map.jpg', 'wb') as file:
                file.write(response.content)
            self.pixmap = QPixmap('map.jpg')
            self.img.setPixmap(self.pixmap)
        except Exception:
            pass

    def change_view(self):
        lst = ['map', 'sat', 'sat,skl']
        self.l = lst[(lst.index(self.l) + 1) % 3]
        self.onlyStatic()

    def delPoint(self):
        self.point = False
        self.addressLabel.setText('')
        self.onlyStatic()
        self.img.setFocus()

    def keyPressEvent(self, event):
        k = (17 - self.z) * 10 ** -2
        if event.key() == Qt.Key_PageUp:
            self.z += 1
        if event.key() == Qt.Key_PageDown:
            self.z -= 1
        if event.key() == Qt.Key_Up:
            self.change[1] += k
        if event.key() == Qt.Key_Down:
            self.change[1] -= k
        if event.key() == Qt.Key_Left:
            self.change[0] -= k
        if event.key() == Qt.Key_Right:
            self.change[0] += k
        self.onlyStatic()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())