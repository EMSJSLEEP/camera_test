#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
import os
import sys
import cv2
import socket
import time
import numpy as np
import datetime
from decode import Decode
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from typing import ChainMap
from PyQt5.QtWidgets import *
from ui_capture_xavier import Ui_capture
from slider import SettingsWindow
from mouse_paint import MousePaint
from pylibdmtx.pylibdmtx import decode
from PyQt5 import QtCore, QtWidgets
from rpc.proxy.proxyfactory import ProxyFactory
from mixrpc import RPCClientWrapper
from mixrpc.tinyrpc.exc import RPCError
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QLineEdit
from rpc.transports import DSProxyTransport, RPCTransportTimeout
mix_8 = True

camera_list = {
    'CAMERA1': 0,
    'CAMERA2': 1,
    'CAMERA3': 2,
    'CAMERA4': 3,
    'CAMERA5': 4
}

class ZoomWindow(QDialog):
    def __init__(self, parent=None, cropped_image=None):
        super(ZoomWindow, self).__init__(parent)
        self.setWindowTitle("Zoomed Image")
        self.setFixedSize(1000, 800)
        layout = QVBoxLayout()
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        # 将图片放大并显示
        if cropped_image is not None:
            self.display_zoomed_image(cropped_image)


    def display_zoomed_image(self, image):
        # 如果图像是 BGR 格式，需要转换为 RGB 格式
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        height, width, channel = image.shape
        bytes_per_line = 3 * width

        # 将 NumPy 数组转换为 bytes 格式
        qimg = QImage(image.data.tobytes(), width, height, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qimg)

        # 获取当前窗口的尺寸
        window_width = self.size().width()
        window_height = self.size().height()

        # 将图像按照窗口大小进行缩放
        scaled_pixmap = pixmap.scaled(window_width, window_height, Qt.KeepAspectRatio)

        self.image_label.setPixmap(scaled_pixmap)


class VideoStreamApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(VideoStreamApp, self).__init__()
        self.setWindowTitle("Video Stream App")
        self.resize(660, 1100)
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.ui = Ui_capture()
        self.ui.setupUi(central_widget)
        self.background()
        self.init_timer()
        self.init_log_file()
        
    def init_log_file(self):
        self.log_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "video_stream_log.txt")
        with open(self.log_file_path, 'a') as log_file:
            log_file.write("Video Stream Application Log\n")
            log_file.write("===========================\n\n")

    def apply_stylesheet(self):
        with open("style.qss", "r") as style_file:
            self.setStyleSheet(style_file.read())

    def params_set(self):
        self.bytes_data = b''
        self.recv_pic_bytes = 1024
        self.cap_now = False
        self.pre_status_ex = True
        self.pre_status_fo = True
        self.decode_tool = Decode()
        self.host = self.ui.lineEdit.text()
        self.port = self.ui.lineEdit_2.text()
        self.cur_frame = None
        self.pixmap = None
        self.slider = None
        self.slid_is_use = False
        self.focus_can_control_flag = False
        self.control_camera = {'focus_setting': [], 'exposure_setting': []}
    
    def connect_rpc(self):
        if mix_8 == False:
            try:
                self.client = RPCClientWrapper("tcp://{}:{}".format(self.host, self.port))
                assert self.client.server.mode() == "normal"
                self.camera = self.client.barcode
            except Exception as rpc_error:
                QMessageBox.critical(self, "Error", "Please check xavier rpc server")
                return False
        else:
            try:
                self.client = ProxyFactory.JsonZmqFactory("tcp://{}:{}".format(self.host, self.port))
                self.camera = self.client.get_proxy('barcode')
            except Exception as rpc_error:
                QMessageBox.critical(self, "Error", "Please check xavier rpc server")
                return False
        self.set_combox_for_camera()
        return True
            

    def background(self):
        self.ui.lineEdit.textChanged.connect(self.ip_edit)
        self.ui.lineEdit_2.textChanged.connect(self.port_edit)
        self.ui.pushButton.clicked.connect(self.connect)
        self.ui.pushButton_2.clicked.connect(self.disconnect)
        self.ui.pushButton_3.clicked.connect(self.capture_one_pic)
        self.ui.pushButton_4.clicked.connect(self.decode)
        self.ui.pushButton_5.clicked.connect(self.slid_show)
        self.ui.pushButton_6.clicked.connect(self.show_last_rect_region)
        self.ui.pushButton_7.clicked.connect(self.start_srceen)
        self.ui.pushButton.setEnabled(True)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_4.setEnabled(False)
        self.ui.pushButton_5.setEnabled(False)
        self.ui.pushButton_6.setEnabled(False)
        self.ui.pushButton_7.setEnabled(False)
        

    def set_combox_for_camera(self):
        self.camera_list = self.camera.get_camera_count()
        self.log_online("Search camera devices......\nCamera list:\n  ")
        for index, dev in enumerate(self.camera_list):
            self.ui.comboBox.setItemText(index, "CAMERA{}".format(index + 1))
            self.log_online("CAMERA{} : {}\n".format(index + 1, dev))

    def connect(self):
        self.params_set()
        rpc_status = self.connect_rpc()
        if rpc_status:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.camera.open()

                self.default_setting_list = self.camera.get_json()
                self.pre_focus = self.default_setting_list[0]
                self.pre_exposure = self.default_setting_list[1]
                self.pre_brightness = self.default_setting_list[2]
                self.camera_width = self.default_setting_list[3]
                self.camera_height = self.default_setting_list[4]
                if self.focus_can_control_flag == True:
                    self.camera.set_focus(self.pre_focus)
                time.sleep(1)
                self.camera.control_auto_exposure(1)
                time.sleep(0.6)
                self.ensure_camera_config()
                self.camera.set_exposure(self.pre_exposure)
                self.camera.set_pwm_duty(1, self.pre_brightness)
                self.camera.set_pwm_number(0xffffffff)
                self.camera.start_pwm()
                _port = self.camera.get_socket_port()
                self.log_online(
                    "Start to connect video stream port {}\n".format(_port))
                self.client_socket.connect((self.host, int(_port)))
                self.is_connect_success = True
                self._posion = self.camera.get_region()
                self.camera.change_region(self._posion[0], self._posion[1], self._posion[2], self._posion[3])
            except RuntimeError:
                QMessageBox.critical(self, "Error", 'connect fail')
                self.is_connect_success = False
                return
            self.ui.label.setEnabled(True)
            self.ui.pushButton.setEnabled(False)
            self.ui.pushButton_2.setEnabled(True)
            self.ui.pushButton_3.setEnabled(True)
            self.ui.pushButton_4.setEnabled(True)
            self.ui.lineEdit.setEnabled(False)
            self.ui.lineEdit_2.setEnabled(False)
            self.ui.pushButton_5.setEnabled(True)
            self.ui.pushButton_6.setEnabled(True)
            
            if (self.is_connect_success):
                self.log_online(
                    "Video stream init successful and RPC have connected\n")
            self.timer.start(33)

    def disconnect(self):
        self.client_socket.close()
        if self.slid_is_use:
            self.timer2.stop()
        if self.slider is not None:
            self.slider.close()
        self.ui.pushButton.setEnabled(True)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_4.setEnabled(False)
        self.ui.pushButton_5.setEnabled(False)
        self.ui.lineEdit.setEnabled(True)
        self.ui.lineEdit_2.setEnabled(True)
        self.log_online("Video stream disconnect and RPC have disconnected\n")
        self.timer.stop()
        # self.timer3.stop()
        
    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_capture_pics)
        self.timer3 = QTimer(self)
        self.timer3.timeout.connect(self.change_region_para)
        self.timer3.start(50)
    
    def set_camera_focus_exposure(self):
        value_ex = self.slider.exposure_value
        value_fo = self.slider.focus_value
        value_duty = self.slider.brightness_value
        status_auto_ex = self.slider.exposure_checkbox.isChecked()
        status_auto_fo = self.slider.focus_checkbox.isChecked()
        staus_auto_brightness = self.slider.led_checkbox.isChecked()
        try:
            if self.pre_status_ex != status_auto_ex and status_auto_ex == False:
                self.camera.control_auto_exposure(1)  #手动
                self.pre_status_ex = status_auto_ex
        
            if self.pre_status_ex != status_auto_ex and status_auto_ex == True:
                self.camera.control_auto_exposure(3)  #自动
                self.pre_status_ex = status_auto_ex

            if self.pre_status_fo != status_auto_fo and status_auto_fo == False and self.focus_can_control_flag:
                self.camera.control_auto_focus(0)
                self.pre_status_fo = status_auto_fo

            if self.pre_status_fo != status_auto_fo and status_auto_fo and self.focus_can_control_flag:
                self.camera.control_auto_focus(1)
                self.pre_status_fo = status_auto_fo

            if self.pre_exposure != value_ex and status_auto_ex == False:
                self.pre_exposure = value_ex
                self.camera.set_exposure(self.pre_exposure)

            if self.pre_focus != value_fo and status_auto_fo == False and self.focus_can_control_flag:
                self.pre_focus = value_fo
                self.camera.set_focus(self.pre_focus)

            if self.pre_brightness != value_duty:
                print(self.pre_brightness)
                self.pre_brightness = value_duty
                self.camera.set_pwm_duty(1, self.pre_brightness)
                self.camera.set_pwm_number(0xffffffff)
                self.camera.start_pwm()
        except RuntimeError as rpc_error:
            QMessageBox.critical(self, "Error", "in set camera, rpc return time out")

    def ensure_camera_config(self):
        try:
            self.camera_settings = self.camera.get_camera_settings()
            for item in self.camera_settings:
                if item['name'] == 'Focus (absolute)':
                    self.control_camera['focus_setting'].append(
                        item['minimum'])
                    self.control_camera['focus_setting'].append(
                        item['maximum'])
                    self.focus_can_control_flag = True
                if item['name'] == 'Exposure (Absolute)':
                    self.control_camera['exposure_setting'].append(
                        item['minimum'])
                    self.control_camera['exposure_setting'].append(
                        item['maximum'])

        except RuntimeError as rpc_error:
            QMessageBox.critical(self, "Error",
                                 "init camera, rpc return time out")
            
    def get_camera_config_and_setting(self):
        self.slider = SettingsWindow()
        self.slider.save_button.setEnabled(False)
        validator_exposure = QIntValidator(self.control_camera['exposure_setting'][0], self.control_camera['exposure_setting'][1], self)
        self.slider.exposure_input.setValidator(validator_exposure)
        self.slider.exposure_slider.setMinimum(self.control_camera['exposure_setting'][0])
        self.slider.exposure_slider.setMaximum(self.control_camera['exposure_setting'][1])
        self.slider.exposure_slider.setValue(self.pre_exposure)
        print(self.pre_exposure, self.pre_focus, self.pre_brightness)
        if self.focus_can_control_flag:
            validator_focus = QIntValidator(self.control_camera['focus_setting'][0], self.control_camera['focus_setting'][1], self)
            self.slider.focus_input.setValidator(validator_focus)
            self.slider.focus_slider.setMinimum(self.control_camera['focus_setting'][0])
            self.slider.focus_slider.setMaximum(self.control_camera['focus_setting'][1])
            self.slider.focus_slider.setValue(self.pre_focus)
        self.slider.led_pwm_slider.setValue(self.pre_brightness)
        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.set_camera_focus_exposure)
        self.timer2.start()

    def capture_one_pic(self):
        self.cap_now = True
        self.save_one_pic(self.pixmap, 'image.jpg')
        try:
            self.image_path = self.camera.transmit_img(0)
        except RuntimeError as rpc_error:
            QMessageBox.critical(self, "Error",
                                 "in save picture, rpc return time out")
            return
        # self.timer.stop()
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_7.setEnabled(True)
        self.log_online("Save {} success\n".format(self.image_path))

    def ip_edit(self):
        self.host = self.ui.lineEdit.text()

    def port_edit(self):
        self.port = self.ui.lineEdit_2.text()

    def save_one_pic(self, pixmap, path=None):
        pixmap.save(path, "JPG", 100)
        QMessageBox.information(self, "Configure", "save success")

    def decode(self):
        data = None
        data_format = [
            'EAN8', 'EAN13', 'UPCA', 'ISBN10', 'ISBN13', 'Interleaved25',
            'Code39', 'Code128', 'QrCode', 'DataMatrix'
        ]
        if self.cap_now == False:
            if mix_8 == False:
                try:
                    data = self.camera.decode_online('DataMatrix', 'SAVE_BOTH', 3, 3000, timeout_ms=9000)
                except RPCError as rpc_error:
                     QMessageBox.information(self, "Error", 'decode time out')
                     return
            else:
                try:
                    data = self.camera.decode_online('DataMatrix', 'SAVE_BOTH', 3, 3000, rpc_timeout=4)
                except RPCTransportTimeout as rpc_error:
                     QMessageBox.information(self, "Error", 'decode time out')
                     return                
            if "decode fail" not in data:
                self.log_online(f"Code value is \n{str(data)}\n")
                # self.show_last_rect_region(True)
            else:
                # self.show_last_rect_region(False)
                self.log_online("Decode Fail\n")
            self.copy_region_2_label(self._posion)
        else:
            self.cap_now = False
            try:
                data = self.camera.decode_local(self.image_path, "DataMatrix", 1, timeout_ms=4000)
                # data = self.camera.decode_local(self.image_path, "AUTO", 1, rpc_timeout=2)
            except RPCError as rpc_error:
                QMessageBox.information(self, "Error", 'decode time out')
            if "decode fail" not in data:
                self.log_online("Code value is \n{}\n".format(data))
                # self.show_last_rect_region(True)
            else:
                # self.show_last_rect_region(False)
                self.log_online("Decode Fail\n")
            self.copy_region_2_label(self._posion)

    def slid_show(self):
        self.slid_is_use = True
        self.get_camera_config_and_setting()
        self.slider.save_button.clicked.connect(self.save_camera_config)
        self.slider.save_button.setEnabled(True)
        self.slider.setWindowTitle('Camera Settings')
        self.slider.show()

    def change_region_para(self):
        if self.ui.label.move_end == True:
            self.ui.label.move_end = False
            self._posion = self.get_image_position()
            self.copy_region_2_label(self._posion)
            try:
                self.camera.change_region(self._posion[0],
                                                 self._posion[1],
                                                 self._posion[2],
                                                 self._posion[3])
            except RuntimeError as rpc_error:
                self.log_online("RPC time out while chanage\n")
            self.log_online("Useful region has changed {}".format(
                self._posion))

    def copy_region_2_label(self, posion):
        self.ui.label.region_copy(posion)

    def get_image_position(self):
        if isinstance(self.ui.label.press_posion, QPoint):
            press_pos = [
                self.ui.label.press_posion.x(),
                self.ui.label.press_posion.y()
            ]
        else:
            press_pos = [0, 0]

        if isinstance(self.ui.label.release_posion, QPoint):
            end_pos = [
                self.ui.label.release_posion.x(),
                self.ui.label.release_posion.y()
            ]
        else:
            end_pos = [self.camera_width, self.camera_height]

        x0 = int((press_pos[0] / 639.0) * (self.camera_width -1))
        y0 = int((press_pos[1] / 479.0) * (self.camera_height -1))
        x1 = int((end_pos[0] / 639.0) * (self.camera_width -1))
        y1 = int((end_pos[1] / 479.0) * (self.camera_height -1))

        width = abs(x0 - x1)
        height = abs(y0 - y1)
        if x0 - x1 > 0 and y0 - y1 > 0:
            crop_coordinates = [x1, y1, width, height]
        elif x0 - x1 < 0 and y0 - y1 > 0:
            crop_coordinates = [x0, y1, width, height]
        elif x0 - x1 > 0 and y0 - y1 < 0:
            crop_coordinates = [x1, y0, width, height]
        elif x0 - x1 < 0 and y0 - y1 < 0:
            crop_coordinates = [x0, y0, width, height]
        else:
            QMessageBox.critical(self, "Error", "please reshape")
            return [0, 0, self.camera_width, self.camera_height]

        return crop_coordinates

    def decode_online(self):
        crop_coordinates = self.get_image_position()
        _frame = self.cur_frame[crop_coordinates[1]:crop_coordinates[1] +
                                crop_coordinates[3],
                                crop_coordinates[0]:crop_coordinates[0] +
                                crop_coordinates[2], :]
        cropped_gray = np.ascontiguousarray(_frame)
        code_value = self.decode_tool.decode_online(cropped_gray)
        return code_value

    def show_last_rect_region(self, status=True):
        self.ui.label.do_last_rect_region(status)
        crop_coordinates = self.get_image_position()
        cropped_image = self.cur_frame[crop_coordinates[1]:crop_coordinates[1] +
                                       crop_coordinates[3],
                                       crop_coordinates[0]:crop_coordinates[0] +
                                       crop_coordinates[2], :]

        # 创建并显示放大窗口
        zoom_window = ZoomWindow(self, cropped_image=cropped_image)
        zoom_window.exec_()

    def log_online(self, message):
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        message = formatted_time +" \n" + message
        self.ui.add_text_to_plaintext(message)
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(message + "\n")

    def start_srceen(self):
        self.ui.pushButton_7.setEnabled(False)
        self.ui.pushButton_3.setEnabled(True)
        self.timer.start()

    def show_capture_pics(self):
        data = self.client_socket.recv(self.recv_pic_bytes)
        if not data:
            return
        self.bytes_data += data

        a = self.bytes_data.find(b'\xff\xd8')
        b = self.bytes_data.find(b'\xff\xd9', a + 2)

        while a != -1 and b != -1:
            self.recv_pic_bytes = (b + 2 - a) * 2
            image_array = np.frombuffer(self.bytes_data[a:b + 2], dtype=np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            self.cur_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.cur_frame_2  = cv2.resize(self.cur_frame, (640, 480))
            pixmap_image = QImage(self.cur_frame_2 .data, 640, 480, QImage.Format_RGB888)
            self.pixmap = QPixmap.fromImage(pixmap_image)
            self.ui.label.setAlignment(Qt.AlignCenter)
            #convert image
            #self.ui.label.setPixmap(self.pixmap.transformed(QTransform().scale(1, -1)) )
            self.ui.label.setPixmap(self.pixmap)
            self.bytes_data = self.bytes_data[b + 2:]
            a = self.bytes_data.find(b'\xff\xd8')
            b = self.bytes_data.find(b'\xff\xd9', a + 2)
    
    def save_camera_config(self):
        try:
            self.pre_exposure = self.slider.exposure_slider.value()
            self.pre_focus = self.slider.focus_slider.value()
            self.pre_brightness = self.slider.led_pwm_slider.value()
            self.camera.set_json([self.pre_focus, self.pre_exposure, self.pre_brightness])
        except Exception as rpc_error:
            QMessageBox.critical(self, "Error", "Please check xavier rpc server")
            return False
        QMessageBox.information(self, 'Configure', 'Save success')
        return "done"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = VideoStreamApp()
    main.show()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print("Exception:", e)
