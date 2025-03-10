# This Python file uses the following encoding: utf-8
# import cv2
# from Foundation import NSArray
# from AVFoundation import AVCaptureDevice

# def get_cv2_camera_list():
#     cv2_camera_list = []
#     index = 0
#     while True:
#         cap = cv2.VideoCapture(index)
#         if not cap.isOpened():
#             break
#         cap.release()
#         cv2_camera_list.append(index)
#         index += 1
#     return cv2_camera_list

# def match_cameras(avcapture_cameras, cv2_cameras):
#     matched_cameras = {}
#     for avcapture_camera in avcapture_cameras:
#         for cv2_camera in cv2_cameras:
#             # 根据需要匹配的条件进行匹配，这里假设摄像头的名称匹配
#             if avcapture_camera in cv2_camera:
#                 matched_cameras[avcapture_camera] = cv2_camera
#                 break
#     return matched_cameras

# # 获取 AVFoundation 提供的摄像头列表
# avcapture_cameras = []
# devices = AVCaptureDevice.devicesWithMediaType_("vide")
# for i in range(devices.count()):
#     device = devices.objectAtIndex_(i)
#     avcapture_cameras.append(device.localizedName().UTF8String())

# # 获取 OpenCV 提供的摄像头列表
# cv2_cameras = get_cv2_camera_list()

# # 将两个列表进行匹配
# matched_cameras = match_cameras(avcapture_cameras, cv2_cameras)

# # 打印匹配结果
# print("Matched Cameras:")
# for avcapture_camera, cv2_camera in matched_cameras.items():
#     print(f"{avcapture_camera} -> {cv2_camera}")

# def symmetric_swap(lst):
#     return [lst[0]] + list(reversed(lst[1:]))

# # 示例用法
# input_list = ['a', 'b', 'c', 'd', 'e', 'f']
# output_list = symmetric_swap(input_list)
# print(output_list)

# import cv2
# import subprocess
# import re

# result = subprocess.run(['system_profiler', 'SPCameraDataType'], capture_output=True, text=True)
# devices = re.findall(r'^(.*?):(.*)', result.stdout, re.MULTILINE)
# camera_devices = [line.strip() for _, line in devices if 'Camera' in line]
# print(camera_devices)

# # camera = cv2.VideoCapture(0)
# # while True:
# #     _status, _image = camera.read()
# #     image = _image
# #     cv2.imshow('x', image)
# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break

# import re

# # camera_list = ['UVC Camera VendorID_1452 ProductID_34068',
# #                'UVC Camera VendorID_8324 ProductID_1285',
# #                'UVC Camera VendorID_22595 ProductID_30852']

# # vendor_id_pattern = re.compile(r'VendorID_(\d+)')
# # product_id_pattern = re.compile(r'ProductID_(\d+)')

# # for camera_info in camera_list:
# #     vendor_match = vendor_id_pattern.search(camera_info)
# #     product_match = product_id_pattern.search(camera_info)

# #     if vendor_match and product_match:
# #         vendor_id = vendor_match.group(1)
# #         product_id = product_match.group(1)

# #         print(f"VendorID: {vendor_id}, ProductID: {product_id}")
# #     else:
# #         print("Pattern not found in:", camera_info)
# def get_mac_cameras():
#     try:
#         result = subprocess.run(['system_profiler', 'SPCameraDataType'], capture_output=True, text=True)
#         devices = re.findall(r'^(.*?):(.*)', result.stdout, re.MULTILINE)
#         camera_devices = [line.strip() for _, line in devices if 'Camera' in line]
#         return camera_devices
#     except Exception as e:
#         return []
    
# def get_camera_id():
#     info_dict = {}
#     _list = get_mac_cameras()
#     _length = len(_list ) - 1
#     vendor_id_pattern = re.compile(r'VendorID_(\d+)')
#     product_id_pattern = re.compile(r'ProductID_(\d+)')

#     for index, camera_info in enumerate(_list):
#         vendor_match = vendor_id_pattern.search(camera_info)
#         product_match = product_id_pattern.search(camera_info)

#         if vendor_match and product_match:
#             vendor_id = vendor_match.group(1)
#             product_id = product_match.group(1)
#             if vendor_id == '1452':
#                 info_dict[f"CAMERA{_length}"] = {
#                     "vendor_id": vendor_id,
#                     "product_id": product_id
#                 }
#             else:
#                 info_dict[f"CAMERA{index-1}"] = {
#                     "vendor_id": vendor_id,
#                     "product_id": product_id
#                 }
#     print(info_dict)
#     return info_dict

# get_camera_id()


# from Foundation import NSArray, NSAutoreleasePool
# from AVFoundation import AVCaptureDevice

# def get_camera_unique_ids():
#     pool = NSAutoreleasePool.alloc().init()

#     devices = AVCaptureDevice.devicesWithMediaType_("vide")
#     unique_ids = [device.uniqueID() for device in devices]
#     pool.release()

#     return unique_ids

# if __name__ == "__main__":
#     camera_ids = get_camera_unique_ids()

#     print("Camera Unique IDs:")
#     for index, camera_id in enumerate(camera_ids):
#         print(f"Camera {index + 1}: {camera_id}")

# import re

# strings = [
#     "1            0x2084:0x0505  0x14141000   1.00         USB 2.0 Camera",
#     "0            0x0c45:0x6366  0x14142000   1.00         CM200"
# ]

# result = {}

# for s in strings:
#     match = re.search(r'(\d+)\s+0x(\w+):\w+\s+\w+\s+\S+\s+(.+)$', s)
#     if match:
#         index = match.group(1)
#         id_value = match.group(2)
#         key = match.group(3).strip()
#         result[key] = {'id': id_value, 'index': index}

# sorted_result = dict(sorted(result.items(), key=lambda x: int(x[1]['index'])))

# print(sorted_result)

# hex_strings = ['0x11200000c456366', 'EAB7A68FEC2B4487AADFD8AMM91C1CB782', '0x113000058437884', '0x1140000b349b182']

# # 使用 sorted 函数按照 ASCII 码值排序
# sorted_hex_strings = sorted(hex_strings, key=lambda x: [ord(c) for c in x])

# print("Sorted Result:", sorted_hex_strings)


# import sys
# import cv2
# from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSlider, QLabel, QCheckBox, QLineEdit, QGroupBox
# from PyQt5.QtGui import QIntValidator
# from PyQt5.QtCore import Qt, QTimer

# class SettingsWindow(QWidget):
#     def __init__(self, parent=None):
#         super(SettingsWindow, self).__init__(parent)

#         self.exposure_value = 24
#         self.focus_value = 24
#         self.brightness_value = 20

#         self.exposure_checkbox = QCheckBox('AUTO_EXPOSURE', self)
#         self.focus_checkbox = QCheckBox('AUTO_FOCUS', self)
#         self.led_checkbox = QCheckBox('FIXED_BRIGHTNESS', self)
#         self.exposure_checkbox.setChecked(False)
#         self.focus_checkbox.setChecked(False)
#         self.led_checkbox.setChecked(False)

#         self.save_button = QPushButton('SAVE', self)

#         self.led_pwm_slider = QSlider(Qt.Horizontal)
#         self.led_pwm_slider.setSingleStep(1)

#         self.exposure_slider = QSlider(Qt.Horizontal)
#         self.exposure_slider.setSingleStep(1)

#         self.focus_slider = QSlider(Qt.Horizontal)
#         self.focus_slider.setSingleStep(1)

#         self.exposure_label = QLabel('Exposure Value: 0')
#         self.focus_label = QLabel('Focus Value: 0')
#         self.led_pwm_label = QLabel('Brightness value: 0')

#         self.exposure_input = QLineEdit()
#         self.focus_input = QLineEdit()
#         self.led_pwm_input = QLineEdit()

#         # Set validators to ensure only positive integers are allowed
#         validator = QIntValidator(0, 100, self)  # You can adjust the range as needed
#         self.exposure_input.setValidator(validator)
#         self.focus_input.setValidator(validator)
#         self.led_pwm_input.setValidator(validator)

#         self.exposure_slider.setDisabled(False)
#         self.focus_slider.setDisabled(False)
#         self.led_pwm_slider.setDisabled(False)

#         self.exposure_slider.valueChanged.connect(self.updateExposureLabel)
#         self.focus_slider.valueChanged.connect(self.updateFocusLabel)
#         self.led_pwm_slider.valueChanged.connect(self.updateBrightnessLabel)

#         self.exposure_checkbox.stateChanged.connect(self.updateExposureSlider)
#         self.focus_checkbox.stateChanged.connect(self.updateFocusSlider)
#         self.led_checkbox.stateChanged.connect(self.updateBrightnessSlider)

#         self.exposure_checkbox.stateChanged.connect(self.updateExposureInput)
#         self.focus_checkbox.stateChanged.connect(self.updateFocusInput)
#         self.led_checkbox.stateChanged.connect(self.updateBrightnessInput)

#         self.exposure_input.returnPressed.connect(self.updateExposureSliderFromInput)
#         self.focus_input.returnPressed.connect(self.updateFocusSliderFromInput)
#         self.led_pwm_input.returnPressed.connect(self.updateBrightnessSliderFromInput)

#         main_layout = QVBoxLayout()

#         exposure_layout = QVBoxLayout()
#         exposure_layout.addWidget(self.exposure_checkbox)
#         exposure_layout.addWidget(self.exposure_label)
#         exposure_layout.addWidget(self.exposure_slider)
#         exposure_layout.addWidget(self.exposure_input)
#         exposure_group = QGroupBox("Exposure Settings")
#         exposure_group.setLayout(exposure_layout)

#         focus_layout = QVBoxLayout()
#         focus_layout.addWidget(self.focus_checkbox)
#         focus_layout.addWidget(self.focus_label)
#         focus_layout.addWidget(self.focus_slider)
#         focus_layout.addWidget(self.focus_input)
#         focus_group = QGroupBox("Focus Settings")
#         focus_group.setLayout(focus_layout)

#         led_layout = QVBoxLayout()
#         led_layout.addWidget(self.led_checkbox)
#         led_layout.addWidget(self.led_pwm_label)
#         led_layout.addWidget(self.led_pwm_slider)
#         led_layout.addWidget(self.led_pwm_input)
#         led_group = QGroupBox("LED Settings")
#         led_group.setLayout(led_layout)

#         main_layout.addWidget(exposure_group)
#         main_layout.addWidget(focus_group)
#         main_layout.addWidget(led_group)
#         main_layout.addWidget(self.save_button)

#         self.setLayout(main_layout)

#     def updateBrightnessLabel(self, value):
#         self.led_pwm_label.setText(f'Brightness value: {value}')
#         self.brightness_value = value
#         self.led_pwm_input.setText(str(value))

#     def updateExposureLabel(self, value):
#         self.exposure_label.setText(f'Exposure: {value}')
#         self.exposure_value = value
#         self.exposure_input.setText(str(value))

#     def updateFocusLabel(self, value):
#         self.focus_label.setText(f'Focus: {value}')
#         self.focus_value = value
#         self.focus_input.setText(str(value))

#     def updateExposureSlider(self, state):
#         auto_exposure = self.exposure_checkbox.isChecked()
#         self.exposure_slider.setDisabled(auto_exposure)

#     def updateFocusSlider(self, state):
#         auto_focus = self.focus_checkbox.isChecked()
#         self.focus_slider.setDisabled(auto_focus)

#     def updateBrightnessSlider(self, state):
#         auto_led = self.led_checkbox.isChecked()
#         self.led_pwm_slider.setDisabled(auto_led)

#     def updateExposureInput(self, state):
#         auto_exposure = self.exposure_checkbox.isChecked()
#         self.exposure_input.setDisabled(auto_exposure)

#     def updateFocusInput(self, state):
#         auto_focus = self.focus_checkbox.isChecked()
#         self.focus_input.setDisabled(auto_focus)

#     def updateBrightnessInput(self, state):
#         auto_led = self.led_checkbox.isChecked()
#         self.led_pwm_input.setDisabled(auto_led)

#     def updateExposureSliderFromInput(self):
#         value = int(self.exposure_input.text())
#         self.exposure_slider.setValue(value)

#     def updateFocusSliderFromInput(self):
#         value = int(self.focus_input.text())
#         self.focus_slider.setValue(value)

#     def updateBrightnessSliderFromInput(self):
#         value = int(self.led_pwm_input.text())
#         self.led_pwm_slider.setValue(value)

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     mainWin = SettingsWindow()
#     mainWin.show()
#     sys.exit(app.exec_())
#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSlider, QLabel, QCheckBox, QLineEdit, QGroupBox
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt, QTimer

class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.setFixedSize(400, 600)
        self.exposure_value = 24
        self.focus_value = 24
        self.brightness_value = 20

        self.exposure_checkbox = QCheckBox('AUTO_EXPOSURE', self)
        self.focus_checkbox = QCheckBox('AUTO_FOCUS', self)
        self.led_checkbox = QCheckBox('FIXED_BRIGHTNESS', self)
        self.exposure_checkbox.setChecked(False)
        self.focus_checkbox.setChecked(False)
        self.led_checkbox.setChecked(False)

        self.save_button = QPushButton('SAVE', self)

        self.led_pwm_slider = QSlider(Qt.Horizontal)
        self.led_pwm_slider.setSingleStep(1)

        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setSingleStep(1)

        self.focus_slider = QSlider(Qt.Horizontal)
        self.focus_slider.setSingleStep(1)

        self.exposure_label = QLabel('Exposure Value: 0')
        self.focus_label = QLabel('Focus Value: 0')
        self.led_pwm_label = QLabel('Brightness value: 0')

        self.exposure_input = QLineEdit()
        self.focus_input = QLineEdit()
        self.led_pwm_input = QLineEdit()

        # Set validators to ensure only positive integers are allowed
        validator = QIntValidator(0, 100, self)
        self.exposure_input.setValidator(validator)
        self.focus_input.setValidator(validator)
        self.led_pwm_input.setValidator(validator)

        self.exposure_slider.setDisabled(False)
        self.focus_slider.setDisabled(False)
        self.led_pwm_slider.setDisabled(False)

        self.exposure_slider.valueChanged.connect(self.updateExposureLabel)
        self.focus_slider.valueChanged.connect(self.updateFocusLabel)
        self.led_pwm_slider.valueChanged.connect(self.updateBrightnessLabel)

        self.exposure_checkbox.stateChanged.connect(self.updateExposureSlider)
        self.focus_checkbox.stateChanged.connect(self.updateFocusSlider)
        self.led_checkbox.stateChanged.connect(self.updateBrightnessSlider)

        self.exposure_checkbox.stateChanged.connect(self.updateExposureInput)
        self.focus_checkbox.stateChanged.connect(self.updateFocusInput)
        self.led_checkbox.stateChanged.connect(self.updateBrightnessInput)

        self.exposure_input.returnPressed.connect(self.updateExposureSliderFromInput)
        self.focus_input.returnPressed.connect(self.updateFocusSliderFromInput)
        self.led_pwm_input.returnPressed.connect(self.updateBrightnessSliderFromInput)

        main_layout = QVBoxLayout()

        exposure_layout = QVBoxLayout()
        exposure_layout.addWidget(self.exposure_checkbox)
        exposure_layout.addWidget(self.exposure_label)
        exposure_layout.addWidget(self.exposure_slider)
        exposure_layout.addWidget(self.exposure_input)
        exposure_group = QGroupBox("Exposure Settings")
        exposure_group.setLayout(exposure_layout)

        focus_layout = QVBoxLayout()
        focus_layout.addWidget(self.focus_checkbox)
        focus_layout.addWidget(self.focus_label)
        focus_layout.addWidget(self.focus_slider)
        focus_layout.addWidget(self.focus_input)
        focus_group = QGroupBox("Focus Settings")
        focus_group.setLayout(focus_layout)

        led_layout = QVBoxLayout()
        led_layout.addWidget(self.led_checkbox)
        led_layout.addWidget(self.led_pwm_label)
        led_layout.addWidget(self.led_pwm_slider)
        led_layout.addWidget(self.led_pwm_input)
        led_group = QGroupBox("LED Settings")
        led_group.setLayout(led_layout)

        main_layout.addWidget(exposure_group)
        main_layout.addWidget(focus_group)
        main_layout.addWidget(led_group)
        main_layout.addWidget(self.save_button)

        self.setLayout(main_layout)

        # 设置样式表
        self.setStyleSheet("""
            QWidget {
                font-size: 16px;
            }
            QGroupBox {
                border: 2px solid gray;
                border-radius: 5px;
                margin-top: 1em;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QCheckBox {
                spacing: 5px;
                padding: 5px;
            }
            QPushButton {
                border: 2px solid #8f8f91;
                border-radius: 10px;
                background-color: #f0f0f0;
                min-width: 80px;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QSlider {
                min-height: 20px;
                max-height: 20px;
            }
            QLineEdit {
                border: 1px solid gray;
                border-radius: 5px;
                padding: 2px;
            }
            QLabel {
                padding: 5px;
            }
        """)

    def updateBrightnessLabel(self, value):
        self.led_pwm_label.setText(f'Brightness value: {value}')
        self.brightness_value = value
        self.led_pwm_input.setText(str(value))

    def updateExposureLabel(self, value):
        self.exposure_label.setText(f'Exposure: {value}')
        self.exposure_value = value
        self.exposure_input.setText(str(value))

    def updateFocusLabel(self, value):
        self.focus_label.setText(f'Focus: {value}')
        self.focus_value = value
        self.focus_input.setText(str(value))

    def updateExposureSlider(self, state):
        auto_exposure = self.exposure_checkbox.isChecked()
        self.exposure_slider.setDisabled(auto_exposure)

    def updateFocusSlider(self, state):
        auto_focus = self.focus_checkbox.isChecked()
        self.focus_slider.setDisabled(auto_focus)

    def updateBrightnessSlider(self, state):
        auto_led = self.led_checkbox.isChecked()
        self.led_pwm_slider.setDisabled(auto_led)

    def updateExposureInput(self, state):
        auto_exposure = self.exposure_checkbox.isChecked()
        self.exposure_input.setDisabled(auto_exposure)

    def updateFocusInput(self, state):
        auto_focus = self.focus_checkbox.isChecked()
        self.focus_input.setDisabled(auto_focus)

    def updateBrightnessInput(self, state):
        auto_led = self.led_checkbox.isChecked()
        self.led_pwm_input.setDisabled(auto_led)

    def updateExposureSliderFromInput(self):
        value = int(self.exposure_input.text())
        self.exposure_slider.setValue(value)

    def updateFocusSliderFromInput(self):
        value = int(self.focus_input.text())
        self.focus_slider.setValue(value)

    def updateBrightnessSliderFromInput(self):
        value = int(self.led_pwm_input.text())
        self.led_pwm_slider.setValue(value)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = SettingsWindow()
    mainWin.show()
    sys.exit(app.exec_())

