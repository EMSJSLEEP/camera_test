from PyQt5 import QtCore, QtWidgets
from mouse_paint import MousePaint

format_size = ["640 * 480", "1280 * 720", "1920 * 1080", "3840 * 2160"]
decode_type = ["ECC200", "DOT_ECC200", "QR"]
camera_list = ['CAMERA0', 'CAMERA1', 'CAMERA2', 'CAMERA3', 'CAMERA4', 'CAMERA5']

class Ui_capture(object):
    def setupUi(self, capture):
        capture.setObjectName("capture")
        capture.resize(660, 900)
        capture.setMaximumSize(QtCore.QSize(16777215, 16777215))

        # 主布局
        self.main_layout = QtWidgets.QVBoxLayout(capture)

        # 视频显示区域
        self.label = MousePaint(capture)
        self.label.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.label.setObjectName("label")
        self.label.setFixedSize(640, 480)  # 固定尺寸为 640×480
        
        # 将视频显示框居中放置
        self.main_layout.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)  # 居中对齐

        # 控件的水平布局
        self.h_layout = QtWidgets.QHBoxLayout()
    
        # 创建一个 QWidget 作为容器
        self.control_widget = QtWidgets.QWidget()
        self.control_widget.setObjectName("control_widget")

        # 设置容器样式（背景颜色和轮廓）
        self.control_widget.setStyleSheet("""
            QWidget#control_widget {
                background-color: #e0e0f8; /* 浅蓝色背景 */
                border: 2px solid #7070a0; /* 深蓝色边框 */
                border-radius: 8px; /* 圆角 */
                padding: 10px; /* 内边距 */
            }
        """)

        # 创建一个垂直布局用于放置控件
        self.control_layout = QtWidgets.QVBoxLayout(self.control_widget)

        # IP 和端口 输入框布局
        self.ip_port_layout = QtWidgets.QHBoxLayout()
        
        self.label_2 = QtWidgets.QLabel(capture)
        self.label_2.setText("IP")
        self.lineEdit = QtWidgets.QLineEdit(capture)
        self.lineEdit.setText("169.254.1.32")
        
        self.label_3 = QtWidgets.QLabel(capture)
        self.label_3.setText("PORT")
        self.lineEdit_2 = QtWidgets.QLineEdit(capture)
        self.lineEdit_2.setText("7801")
        
        self.ip_port_layout.addWidget(self.label_2)
        self.ip_port_layout.addWidget(self.lineEdit)
        self.ip_port_layout.addWidget(self.label_3)
        self.ip_port_layout.addWidget(self.lineEdit_2)
        
        # 将 IP 和端口部分添加到控件的布局
        self.control_layout.addLayout(self.ip_port_layout)

        # 创建一个新的水平布局，将 ComboBox、Connect 和 Disconnect 按钮放在同一行
        self.combo_connect_layout = QtWidgets.QHBoxLayout()

        # Camera选择
        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.setObjectName("comboBox")
        for item in camera_list:
            self.comboBox.addItem(item)

        # Connect按钮
        self.pushButton = QtWidgets.QPushButton("Connect")

        # Disconnect按钮
        self.pushButton_2 = QtWidgets.QPushButton("Disconnect")
        
        # 将 ComboBox、Connect 按钮和 Disconnect 按钮添加到水平布局
        self.combo_connect_layout.addWidget(self.comboBox)
        self.combo_connect_layout.addWidget(self.pushButton)
        self.combo_connect_layout.addWidget(self.pushButton_2)

        # 将这个水平布局添加到控件的布局
        self.control_layout.addLayout(self.combo_connect_layout)

        # 将这个组合控件添加到主布局
        self.main_layout.addWidget(self.control_widget)

        # 其他控件
        self.pushButton_4 = QtWidgets.QPushButton("Decode")
        self.main_layout.addWidget(self.pushButton_4)

        self.pushButton_3 = QtWidgets.QPushButton("Stop and Capture")
        self.main_layout.addWidget(self.pushButton_3)

        self.pushButton_7 = QtWidgets.QPushButton("Start")
        self.main_layout.addWidget(self.pushButton_7)
        
        self.pushButton_5 = QtWidgets.QPushButton("Setting")
        self.main_layout.addWidget(self.pushButton_5)

        self.pushButton_6 = QtWidgets.QPushButton("Show Region")
        self.main_layout.addWidget(self.pushButton_6)
    
        self.plainTextEdit = QtWidgets.QPlainTextEdit()
        self.main_layout.addWidget(self.plainTextEdit)

        # 重新翻译文本
        self.retranslateUi(capture)

        QtCore.QMetaObject.connectSlotsByName(capture)

    def scroll_plain_text_edit(self):
        self.plainTextEdit.verticalScrollBar().setValue(self.plainTextEdit.verticalScrollBar().maximum())

    def retranslateUi(self, capture):
        _translate = QtCore.QCoreApplication.translate
        capture.setWindowTitle(_translate("capture", "Capture"))

    def add_text_to_plaintext(self, text):
        # 向 QPlainTextEdit 添加文本，并滚动到文本框底部
        self.plainTextEdit.appendPlainText(text)
        self.scroll_plain_text_edit()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    capture = QtWidgets.QWidget()
    ui = Ui_capture()
    ui.setupUi(capture)
    capture.show()
    sys.exit(app.exec_())
