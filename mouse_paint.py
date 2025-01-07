from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class MousePaint(QLabel):
    flag = False

    def __init__(self, parent=None):
        super(MousePaint, self).__init__(parent)
        self.rect_visible = False
        self.press_posion = 0
        self.release_posion = 0
        self.end_posion = 0
        self.move_end = False
        self.is_show_rect = False
        self.decode_status = True
        self.last_rect_coords = QRect(0, 0, 640, 480)
        self.pre_coords = QRect(0, 0, 640, 480)

    def mousePressEvent(self, event):
        self.press_posion = event.pos()
        self.last_rect_coords.setTopLeft(self.press_posion)
        self.last_rect_coords.setWidth(0)
        self.last_rect_coords.setHeight(0)
        self.is_show_rect = False
        self.update()

    def mouseReleaseEvent(self, event):
        self.end_posion = event.pos()

        if self.press_posion != self.end_posion:
            self.move_end = True
        else:
            self.move_end = False

    def mouseMoveEvent(self, event):
        self.last_rect_coords.setWidth(event.pos().x() -
                                       self.last_rect_coords.x())
        self.last_rect_coords.setHeight(event.pos().y() -
                                        self.last_rect_coords.y())
        self.release_posion = event.pos()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(Qt.green, 2, Qt.DotLine))
        painter.drawRect(self.last_rect_coords)
        if self.is_show_rect:
            if self.decode_status == False:
                painter.setPen(QPen(Qt.red, 4, Qt.DotLine))
                painter.drawRect(self.pre_coords)
            else:
                painter.setPen(QPen(Qt.green, 2, Qt.DotLine))
                painter.drawRect(self.pre_coords)

    def do_last_rect_region(self, status=True):
        self.is_show_rect = True
        self.decode_status = status

    def region_copy(self, _posion):
        self.pre_coords = QRect(_posion[0], _posion[1], _posion[2], _posion[3])

    def reset(self):
        self.rect_visible = False
        self.press_posion = 0
        self.release_posion = 0
        self.end_posion = 0
        self.move_end = False
        self.is_show_rect = False
        self.decode_status = True
        self.last_rect_coords = QRect(0, 0, 640, 480)
        self.pre_coords = QRect(0, 0, 640, 480)
