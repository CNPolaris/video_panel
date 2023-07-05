# -*- coding: utf-8 -*-
import sys
import tkinter

from PySide6.QtWidgets import QWidget, QApplication, QHBoxLayout, QPushButton, QVBoxLayout

from components.HKThread import HKThread


class HKVideoDemo(QWidget):
    def __init__(self):
        super().__init__()
        ############################
        # 主窗体
        ############################
        self.setWindowTitle("视频大屏Demo")
        self.main_layout = QHBoxLayout(self)
        ############################
        # 组件定义
        ############################
        self.video_widget = QWidget()
        self.main_layout.addWidget(self.video_widget)
        ############################
        # 视频地址
        ############################
        self.ip = '192.168.1.64'
        self.username = 'admin'
        self.passwd = 'ylcx888888'
        self.hk_thread = HKThread()
        self.hk_thread.init(self.ip, self.username, self.passwd, self.video_widget.winId())
        self.ptz_down_btn = QPushButton("下")
        self.main_layout.addWidget(self.ptz_down_btn)
        self.ptz_down_btn.pressed.connect(self.ptz_down)

    def showEvent(self, event) -> None:
        self.hk_thread.start()

    def ptz_down(self):
        if self.hk_thread.isRunning():
            self.hk_thread.ptz_down(0)

    def closeEvent(self, event) -> None:
        self.hk_thread.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = HKVideoDemo()
    w.show()
    sys.exit(app.exec())
