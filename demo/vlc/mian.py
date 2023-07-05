# -*- coding: utf-8 -*-
"""
@author:CNPolaris
"""
import sys

from PySide6.QtWidgets import QWidget, QApplication, QHBoxLayout, QPushButton, QVBoxLayout
from components.VideoPanel import VideoPanel


class VideoDemo(QWidget):

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
        self.panel = VideoPanel()  # 监控面板
        self.main_layout.addWidget(self.panel)
        self.start_btn = QPushButton("开始")
        self.pause_btn = QPushButton("暂停")
        self.stop_btn = QPushButton("结束")
        self.isPlay = False  # 避免设置播放句柄失败
        self.init()
        ############################
        # 视频url
        ############################
        self.urls = ["http://vfx.mtime.cn/Video/2021/11/16/mp4/211116131456748178.mp4",
                     "http://vd3.bdstatic.com/mda-jennyc5ci1ugrxzi/mda-jennyc5ci1ugrxzi.mp4"]
        ############################
        # 事件绑定
        ############################
        self.start_btn.clicked.connect(self.on_start_btn_click)
        self.stop_btn.clicked.connect(self.on_stop_btn_click)
        self.pause_btn.clicked.connect(self.on_pause_btn_click)

    def init(self):
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.stop_btn)
        self.main_layout.addLayout(btn_layout)

    def on_start_btn_click(self):
        if not self.isPlay:
            self.panel.set_urls(self.urls)
            self.panel.open()
            self.isPlay = True

    def on_pause_btn_click(self):
        self.panel.pause()

    def on_stop_btn_click(self):
        self.panel.stop()
        self.isPlay = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = VideoDemo()
    w.show()
    sys.exit(app.exec())
