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
        validator = QIntValidator(-20, 3000, self)
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
