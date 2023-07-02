# -*- coding: utf-8 -*-
"""
@author:CNPolaris
"""
from PySide6.QtWidgets import QWidget, QGridLayout, QMenu, QSizePolicy, QLabel
from PySide6.QtCore import Qt, QEvent, QSize, Signal
from PySide6.QtGui import QAction, QCursor

from .VLCThread import VLCThread
from .VideoBox import VideoBox


class VideoPanel(QWidget):
    fullScreenSignal = Signal(bool)

    def __init__(self, parent=None) -> None:
        super(VideoPanel, self).__init__(parent)
        self.resize(546, 329)

        self.videoMax = False
        self.videoCount = 64
        self.videoType = "1_4"

        self.videoMenu = QMenu(self)
        self.actionFull = QAction("切换全屏模式", self.videoMenu)

        self.gridLayout = QGridLayout(self)
        self.widgets = []
        self.videoBox = VideoBox(self)

        self.fullScreenSignal.connect(self.fullScreen)

        self.initControl()
        self.initForm()
        self.initMenu()

        self.urls = []  # 播放链接
        self.players = {}  # 播放线程

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.Type.MouseButtonDblClick:
            widget = watched
            if not self.videoMax:
                self.videoMax = True
                self.videoBox.hide_video_all()
                self.gridLayout.addWidget(widget, 0, 0)
                widget.setVisible(True)
            else:
                self.videoMax = False
                self.videoBox.show_video_all()
            widget.setFocus()
        elif event.type() == QEvent.Type.MouseButtonPress:
            mouseEvent = event
            if mouseEvent.button() == Qt.MouseButton.RightButton:
                self.videoMenu.exec(QCursor.pos())
        return super().eventFilter(watched, event)

    def sizeHint(self) -> QSize:
        return QSize(800, 600)

    def minimumSizeHint(self) -> QSize:
        return QSize(546, 329)

    def initControl(self):
        self.gridLayout.setSpacing(1)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.gridLayout)

    def initForm(self):
        qss = "QFrame{border:2px solid #000000;} QLabel{font:75 25px;color:#F0F0F0;border:2px solid " \
              "#AAAAAA;background:#303030;} QLabel:focus{border:2px solid #00BB9E;background:#555555;}"
        self.setStyleSheet(qss)
        for i in range(self.videoCount):
            widget_label = QLabel()
            widget_label.setObjectName(f"video{i + 1}")
            widget_label.installEventFilter(self)
            widget_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            widget_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            widget_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            widget_label.setText(f"通道{i + 1}")
            self.widgets.append(widget_label)

    def initMenu(self):
        self.actionFull.triggered.connect(self.full)
        self.videoMenu.addAction(self.actionFull)
        self.videoMenu.addSeparator()

        # 实例化通道布局类
        enable = [True, True, True, True, True, True, True, True, True]
        self.videoBox.init_menu(self.videoMenu, enable)
        self.videoBox.setVideoType(self.videoType)
        self.videoBox.setLayout(self.gridLayout)
        self.videoBox.setWidgets(self.widgets)
        self.videoBox.show_video_all()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:  # Esc快捷键退出全屏
            if self.actionFull.text() == "切换正常模式":
                self.fullScreenSignal.emit(False)
        return super().keyPressEvent(event)

    def full(self):
        if self.actionFull.text() == "切换全屏模式":
            self.actionFull.setText("切换正常模式")
            self.fullScreenSignal.emit(True)
        else:
            self.actionFull.setText("切换全屏模式")
            self.fullScreenSignal.emit(False)

    def fullScreen(self, full_flag):
        if full_flag:
            self.showFullScreen()
        else:
            self.showNormal()

    def set_urls(self, urls):
        self.urls = urls

    def open(self):
        for i in range(len(self.urls)):
            vlc = VLCThread()
            vlc.set_url(self.urls[i])
            vlc.play(self.widgets[i].winId())
            vlc.start()
            self.players[i] = vlc

    def pause(self):
        for i in range(len(self.urls)):
            self.players[i].pause()

    def stop(self):
        for i in range(len(self.urls)):
            if self.players[i].isRunning():
                self.players[i].stop()
                self.players[i].quit()
                self.players[i].wait(3000)

    def closeEvent(self, event) -> None:
        self.stop()
