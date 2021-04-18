from PyQt5.QtWidgets import QMainWindow,QApplication
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests
import sys
import math


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def lonlat_distance(a, b):

    degree_to_meters_factor = 111 * 1000 # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/untitled.ui', self)
        self.z = 7
        self.l = 'map'
        self.index = ''
        self.change = [0, 0]
        self.point = False
        self.view.clicked.connect(self.change_view)
        self.search.clicked.connect(self.fine_new)
        self.delPointBut.clicked.connect(self.delPoint)
        self.indexCheckBox.stateChanged.connect(self.indexCheckBoxChange)

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
            self.address = toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
            try:
                self.index += " " + \
                        toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
            except Exception:
                self.index = ''
            if self.indexCheckBox.isChecked():
                self.addressLabel.setText(self.address + self.index)
            else:
                self.addressLabel.setText(self.address)
            self.first_cords = tuple(map(float, toponym['Point']['pos'].split()))
            self.onlyStatic()
            self.img.setFocus()
        except Exception:
            pass

    def indexCheckBoxChange(self):
        if self.indexCheckBox.isChecked():
            self.addressLabel.setText(self.address + self.index)
        else:
            self.addressLabel.setText(self.address)

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

    def mousePressEvent(self, event):
        center = (320, 266)
        if event.x() in range(18, 621):
            if event.y() in range(40, 495):
                print(f"Координаты: {event.x() - center[0]}, {event.y() - center[1]}")
                k1 = (17 - (event.x() - center[0])) * 10 ** -2
                k2 = (17 - (event.y() - center[1])) * 10 ** -2
                self.first_cords = (self.first_cords[0] - k1, self.first_cords[1] + k2)
                self.change = [0, 0]
                geo_link = 'https://geocode-maps.yandex.ru/1.x'
                params_geo = {
                    'geocode': ','.join(map(str, self.first_cords)),
                    'apikey': '33c50873-3bf9-406f-8799-464a3980ef2d',
                    'format': 'json',
                }
                response = requests.get(geo_link, params_geo).json()
                try:
                    toponym = response['response']['GeoObjectCollection']['featureMember'][0][
                        'GeoObject']
                    self.address = toponym['metaDataProperty']['GeocoderMetaData']['Address'][
                        'formatted']
                    try:
                        self.index += " " + \
                                        toponym['metaDataProperty']['GeocoderMetaData']['Address'][
                                              'postal_code']
                    except Exception:
                        self.index = ''
                    if self.indexCheckBox.isChecked():
                        self.addressLabel.setText(self.address + self.index)
                    else:
                        self.addressLabel.setText(self.address)
                except Exception:
                    pass
                self.onlyStatic()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())