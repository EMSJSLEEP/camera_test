#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QLabel
from VideoStreamApp import VideoStreamApp
from PC_VideoStreamApp import PC_VideoStreamApp

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.xavier_window = None
        self.pc_window = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('界面选择器')
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout()

        # 创建下拉框
        self.comboBox = QComboBox()
        self.comboBox.addItem("Xavier")
        self.comboBox.addItem("PC")
        layout.addWidget(self.comboBox)

        # 创建按钮
        btn_open = QPushButton('Ensure', self)
        btn_open.clicked.connect(self.open_selected_interface)
        layout.addWidget(btn_open)

        self.setLayout(layout)

    def open_selected_interface(self):
        selected_interface = self.comboBox.currentText()

        if selected_interface == "Xavier":
            self.xavier_window = VideoStreamApp()
            self.xavier_window.show()
        elif selected_interface == "PC":
            self.pc_window = PC_VideoStreamApp()
            self.pc_window.show()
        self.close()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
