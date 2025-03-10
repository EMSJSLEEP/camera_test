#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
import uuid
import sys
import cv2
import os, time
import numpy as np
from decode import Decode
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QLineEdit
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from ui_capture import Ui_capture
from mouse_paint import MousePaint
from macos_tools import Tools
from slider import SettingsWindow
from PyQt5.QtMultimedia import QCameraInfo

camera_list = {
    'CAMERA0': 0,
    'CAMERA1': 1,
    'CAMERA2': 2,
    'CAMERA3': 3,
    'CAMERA4': 4,
    'CAMERA5': 5,
}

class ZoomWindow(QDialog):
    def __init__(self, parent=None):
        super(ZoomWindow, self).__init__(parent)
        self.setWindowTitle("Zoomed Image")
        self.setFixedSize(1000, 800)
        layout = QVBoxLayout()
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        self.cropped_image = None
        self.timer_zoom = QTimer(self)
        self.timer_zoom.timeout.connect(self.update_image)
        self.timer_zoom.start(50)

    def display_zoomed_image(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        qimg = QImage(image.data.tobytes(), width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        window_width = self.size().width()
        window_height = self.size().height()
        scaled_pixmap = pixmap.scaled(window_width, window_height, Qt.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)

    def update_image(self):
        if self.cropped_image is not None:
            self.display_zoomed_image(self.cropped_image)

    def update_cropped_image(self, cropped_image):
        self.cropped_image = cropped_image

class PC_VideoStreamApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(PC_VideoStreamApp, self).__init__()
        self.setWindowTitle("Video Stream App")
        self.resize(660, 1100)
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.ui = Ui_capture()
        self.ui.setupUi(central_widget)
        self.params_set()
        self.background()
        self.set_combox_for_camera()
        self.init_timer()

    def params_set(self):
        self.bytes_data = b''
        self.w = 640
        self.h = 480
        self.recv_pic_bytes = 1024
        self.cap_now = False
        self.decode_tool = Decode()
        self.cur_frame = None
        self.pixmap = None
        self.camera = None
        self.pre_exposure = 15
        self.pre_focus = 1
        self.pre_brightness = 1
        self.pre_status_ex = True
        self.pre_status_fo = True
        self.zoom_window = None
        self.tool_no_para = Tools()
        self.support_code = ['ECC200', 'QR', 'ZBAR']
        self.control_camera = {
            'focus_setting': [1, 100],
            'exposure_setting': [15, 200]
        }

    def background(self):
        self.ui.pushButton.clicked.connect(self.connect)
        self.ui.pushButton_2.clicked.connect(self.disconnect)
        self.ui.pushButton_3.clicked.connect(self.capture_one_pic)
        self.ui.pushButton_4.clicked.connect(self.decode_one_local_pic)
        self.ui.pushButton_5.clicked.connect(self.slid_show)
        self.ui.pushButton_6.clicked.connect(self.show_last_rect_region)
        self.ui.pushButton_7.clicked.connect(self.start_srceen)
        self.ui.pushButton.setEnabled(True)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_4.setEnabled(False)
        self.ui.pushButton_5.setEnabled(False)
        self.ui.pushButton_6.setEnabled(False)
        self.ui.pushButton_7.setEnabled(True)

    def _swap(self, lst):
        return [lst[0]] + list(reversed(lst[1:]))

    def get_frame_size(self):
        frame_format = self.ui.format_frame_box.currentText()
        width, height = map(int, frame_format.split('*'))
        return width, height
    
    def set_combox_for_camera(self):
        self.mac_camera_index = None
        self.ui.comboBox.clear()
        self.log_online("Search camera devices......\nCamera list:\n  ")
        self.video_dict = self.tool_no_para.get_camera_id()
        self.video_len = len(self.video_dict)
        for index, (key, item) in enumerate(self.video_dict.items()):
            self.ui.comboBox.addItem("")
            self.ui.comboBox.setItemText(index, key)
            if "FaceTime" in item['camera_name']:
                self.mac_camera_index = index
            self.log_online("{} : {}\n".format(key, item['camera_name']))

    def adapter_for_tool_and_avfundation(self, _num):
        #排列顺序！
        key_found = next(key for key, value in camera_list.items() if value == _num)
        select_vendor_id = hex(
            int(self.video_dict[key_found]['vendor_id']))[2:] if self.video_dict[key_found]['vendor_id'] else None
        select_position_id = self.video_dict[key_found]['position_id'][2:10]
        # print(f"--------------{select_vendor_id} {select_position_id}----------\n")
        camera_list_by_tool = self.tool_no_para.get_devices()
        # print(f"--------------{camera_list_by_tool}----------\n")
        for key, value in camera_list_by_tool.items():
            if select_vendor_id in value['vendor_id'] or select_position_id in value['position_id']:
                self.log_online(f"Match camera{select_position_id} successful\n")
                return value['index']
        self.log_online(f"Error match camera{select_position_id}\n")

    def tools_init(self, num):
        if self.video_len == 1 or num == self.mac_camera_index:
            self.ex_value_limit = [False, False]
            self.fo_value_limit = [False, False]
        else:
            tool_num = self.adapter_for_tool_and_avfundation(num)
            self.log_online(f"Convert camera num for uvc-util is {tool_num}\n")
            self.mac_tools = Tools(tool_num)
            self.ex_value_limit = [
                self.mac_tools.ex_minimum, self.mac_tools.ex_maximum
            ]
            self.fo_value_limit = [
                self.mac_tools.fo_minimum, self.mac_tools.fo_maximum
            ]
        self.log_online("Camera exposure select in [{}, {}]\n".format(
            self.ex_value_limit[0], self.ex_value_limit[1]))
        self.log_online("Camera focus select in [{}, {}]\n".format(
            self.fo_value_limit[0], self.fo_value_limit[1]))
        if self.fo_value_limit == [False, False]:
            self.fo_value_limit = False

    def connect(self):
        self.params_set()
        camera_num = camera_list[self.ui.comboBox.currentText()]
        self.log_online("Now connect Camera{}\n".format(camera_num))
        self.tools_init(camera_num)
        self.w, self.h = self.get_frame_size()
        try:
            self.camera = cv2.VideoCapture(camera_num)
            self.camera.set(6, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            self.camera.set(5, 30)  # 帧率
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)
            self.is_connect_success = True
        except:
            QMessageBox.critical(self, "Error", 'connect fail')
            self.is_connect_success = False
            return

        self.ui.label.setEnabled(True)
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton_2.setEnabled(True)
        self.ui.pushButton_3.setEnabled(True)
        self.ui.pushButton_4.setEnabled(True)
        self.ui.pushButton_5.setEnabled(True)
        self.ui.pushButton_6.setEnabled(True)
        if (self.is_connect_success):
            self.log_online("Successful enable video stream\n")
            self.timer.start()

    def disconnect(self):
        self.ui.pushButton.setEnabled(True)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_4.setEnabled(False)
        self.camera.release()
        self.timer.stop()
        self.set_combox_for_camera()
        self.log_online("disable video stream\n")

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_capture_pics)
        self.timer3 = QTimer(self)
        self.timer3.timeout.connect(self.change_region_para)
        self.timer3.start(50)

    def generate_random_filename(self):
        random_string = str(uuid.uuid4().hex)[:5]  # 生成一个8位的随机字符串
        filename = f"{random_string}.jpg"
        return filename

    def capture_one_pic(self):
        self.cap_now = True
        _path_image = self.generate_random_filename()
        # self.current_script_path = os.getcwd() + '/' + _path_image
        self.current_script_path = f"/Users/cwu/Desktop/{_path_image}"
        self.save_one_pic(self.pixmap, self.current_script_path)
        self.log_online(f"Save path is {self.current_script_path}\n")
        self.timer.stop()
        self.ui.pushButton_7.setEnabled(True)

    def start_srceen(self):
        self.set_combox_for_camera()
        if self.camera:
            self.timer.start()

    def ip_edit(self):
        self.host = self.ui.lineEdit.text()

    def port_edit(self):
        self.port = self.ui.lineEdit_2.text()

    def save_one_pic(self, pixmap, path=None):
        pixmap.save(path, "JPG", 100)
        QMessageBox.information(self, "Configure", "save success")

    def decode_one_local_pic(self):
        data = self.decode_online()
        if data != 'decode_fail':
            self.log_online("Code value is \n{}\n".format(data))
        else:
            self.log_online("Decode Fail\n")
        self.timer.start()

    def decode_online(self):
        decoded_info = None
        crop_coordinates = self.get_image_position()
        _frame = self.image[crop_coordinates[1]:crop_coordinates[1] +
                            crop_coordinates[3],
                            crop_coordinates[0]:crop_coordinates[0] +
                            crop_coordinates[2]]
        decode_type = self.ui.decode_type_box.currentText()
        self.log_online(f"now decode type is {decode_type}\n")
        gray_image = cv2.cvtColor(_frame, cv2.COLOR_BGR2GRAY)
        if decode_type == 'ECC200':
            decoded_info = self.decode_tool.decode_ecc200(gray_image)
        elif decode_type == 'DOT_ECC200':
            decoded_info = self.decode_tool.decode_dot(gray_image, 3000)
        elif decode_type == 'QR':
            decoded_info = self.decode_tool.decode_qr(gray_image)
        elif decode_type == 'AUTO':
            decoded_info = self.decode_tool.auto_decode(gray_image, 4000)
        else:
            decoded_info = self.decode_tool.simple_decode_dmtx(gray_image, 3000)
        self.change_region_para()
        return decoded_info

    def show_capture_pics(self):
        _status, _image = self.camera.read()
        if _status:
            self.image = _image
            self.cur_frame = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.resize_frame = cv2.resize(self.cur_frame, (640, 480))
            pixmap_inage = QImage(self.resize_frame, 640, 480, QImage.Format_RGB888)
            self.pixmap = QPixmap.fromImage(pixmap_inage)
            self.ui.label.setPixmap(self.pixmap)

        if self.zoom_window:
            crop_coordinates = self.get_image_position()
            cropped_image = self.cur_frame[crop_coordinates[1]:crop_coordinates[1] + crop_coordinates[3],
                                            crop_coordinates[0]:crop_coordinates[0] + crop_coordinates[2], :]
            self.zoom_window.update_cropped_image(cropped_image)

    def log_online(self, message):
        self.ui.add_text_to_plaintext(message)


    def check_camera_permission(self):
        cameras = QCameraInfo.availableCameras()
        if not cameras:
            print("No cameras available.")
            return False
        for camera in cameras:
            if not camera.isNull():
                print(f"Camera: {camera.deviceName()}")
        return True

    def show_last_rect_region(self, decode_status):
        self.ui.label.do_last_rect_region(decode_status)
        if self.zoom_window is None:
            self.zoom_window = ZoomWindow(self)
        self.zoom_window.show()

    def change_region_para(self):
        if self.ui.label.move_end == True:
            self.ui.label.move_end = False
            _posion = self.get_image_position()
            self.copy_region_2_label(_posion)
            self.log_online("Useful region has changed {}".format(_posion))

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
            end_pos = [self.w, self.h]

        x0 = int((press_pos[0] / 639.0) * (self.w -1))
        y0 = int((press_pos[1] / 479.0) * (self.h -1))
        x1 = int((end_pos[0] / 639.0) * (self.w -1))
        y1 = int((end_pos[1] / 479.0) * (self.h -1))

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
            # QMessageBox.critical(self, "Error", "please reshape")
            return [0, 0, self.w, self.h]

        return crop_coordinates

    def slid_show(self):
        self.get_camera_config_and_setting()
        self.slider.setWindowTitle('Camera Settings')
        self.slider.show()

    def get_camera_config_and_setting(self):
        self.slider = SettingsWindow()
        if self.ex_value_limit:
            self.slider.exposure_slider.setMinimum(self.ex_value_limit[0])
            self.slider.exposure_slider.setMaximum(self.ex_value_limit[1])
        else:
            self.slider.exposure_slider.setDisabled(True)
            self.slider.focus_slider.setDisabled(True)
        if self.fo_value_limit:
            self.slider.focus_slider.setMinimum(self.fo_value_limit[0])
            self.slider.focus_slider.setMaximum(self.fo_value_limit[1])
        else:
            self.slider.focus_slider.setDisabled(True)
        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.set_camera_focus_exposure)
        self.timer2.start()

    def set_camera_focus_exposure(self):
        value_ex = self.slider.exposure_value
        value_fo = self.slider.focus_value
        value_duty = self.slider.brightness_value
        status_auto_ex = self.slider.exposure_checkbox.isChecked()
        status_auto_fo = self.slider.focus_checkbox.isChecked()

        if self.ex_value_limit and self.fo_value_limit:
            if self.pre_status_ex != status_auto_ex and status_auto_ex == False:
                self.mac_tools.set_ex_auto_mode(False)
                self.pre_status_ex = status_auto_ex
            if self.pre_status_ex != status_auto_ex and status_auto_ex == True:
                self.mac_tools.set_ex_auto_mode(True)
                self.pre_status_ex = status_auto_ex

            if self.pre_status_fo != status_auto_fo and status_auto_fo == False and self.fo_value_limit:
                self.mac_tools.set_fo_auto_mode(False)
                self.pre_status_fo = status_auto_fo

            if self.pre_status_fo != status_auto_fo and status_auto_fo and self.fo_value_limit:
                self.mac_tools.set_fo_auto_mode(True)
                self.pre_status_fo = status_auto_fo

            if self.pre_exposure != value_ex and status_auto_ex == False:
                self.pre_exposure = value_ex
                self.mac_tools.configure_settings('exposure-time-abs', self.pre_exposure)

            if self.pre_focus != value_fo and status_auto_fo == False and self.fo_value_limit:
                self.pre_focus = value_fo
                self.mac_tools.configure_settings('focus-abs', self.pre_focus)
            
            if self.pre_brightness != value_duty:
                self.pre_brightness = value_duty
                self.mac_tools.configure_settings('gain', self.pre_brightness)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = PC_VideoStreamApp()
    main.show()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print("Exception:", e)
