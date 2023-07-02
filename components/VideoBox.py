# -*- coding: utf-8 -*-
"""
@author:CNPolaris
"""

from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Signal, QObject


class VideoBox(QObject):
    videoMaxSignal = Signal(bool)

    def __init__(self, parent=None) -> None:
        super().__init__()

        self.gridLayout = None  # 通道布局

        self.videoCount = 64  # 视频通道数量

        self.menuFlag = "画面"  # 主菜单标识
        self.actionFlag = "通道"  # 子菜单标识
        self.videoType = "1_4"  # 当前画面类型
        self.types = {}  # 布局方案集合
        self.widgets = []
        self.init_types()  # 初始化布局方案

    def init_types(self):
        self.types[4] = ["1_4", "5_8", "9_12", "13_16", "17_20", "21_24", "25_28", "29_32", "33_36"]
        self.types[6] = ["1_6", "7_12", "13_18", "19_24", "25_30", "31_36"]
        self.types[8] = ["1_8", "9_16", "17_24", "25_32", "33_40", "41_48", "49_57", "57_64"]
        self.types[9] = ["1_9", "9_17", "18_26", "27_35", "36_42", "43_50", "51_59"]
        self.types[13] = ["1_13", "14_26", "27_39", "40_52", "52_64"]
        self.types[16] = ["1_16", "17_32", "33_48", "49_64"]
        self.types[25] = ["1_25"]
        self.types[36] = ["1_36"]
        self.types[64] = ["1_64"]

    def add_menu(self, menu, type: int):
        # 父菜单文字
        name = f"切换到{type}{self.menuFlag}"
        # 列表中取出该布局大类下的小类集合
        flags = self.types[type]
        # 超过一个子元素则添加子菜单
        menuSub = QMenu()
        if len(flags) > 1:
            menuSub = menu.addMenu(name)
        else:
            menuSub = menu

        for flag in flags:
            lis = flag.split("_")
            start = lis[0]
            end = lis[1]
            # 对应菜单文本
            text = f"{self.actionFlag}{start}-{self.actionFlag}{end}"
            if len(flags) == 1:
                text = name
            # 添加菜单动作
            action = menuSub.addAction(text)
            action.setProperty("index", start)
            action.setProperty("type", type)
            action.setProperty("flag", flag)
            action.triggered.connect(self.show_video)

    def setVideoType(self, videoType):
        self.videoType = videoType

    def setLayout(self, gridLayout):
        self.gridLayout = gridLayout

    def setWidgets(self, widgets):
        self.widgets = widgets
        self.videoCount = len(widgets)

    def setMenuFlag(self, menuFlag):
        self.menuFlag = menuFlag

    def setActionFlag(self, actionFlag):
        self.actionFlag = actionFlag

    def setTypes(self, types: list):
        self.types = types

    def init_menu(self, menu, enable: list):
        # 通过菜单是否可见设置每个菜单可见与否
        if len(enable) < 9:
            return

        if enable[0]:
            self.add_menu(menu, 4)

        if enable[1]:
            self.add_menu(menu, 6)

        if enable[2]:
            self.add_menu(menu, 8)

        if enable[3]:
            self.add_menu(menu, 9)

        if enable[4]:
            self.add_menu(menu, 13)

        if enable[5]:
            self.add_menu(menu, 16)

        if enable[6]:
            self.add_menu(menu, 25)

        if enable[7]:
            self.add_menu(menu, 36)

        if enable[8]:
            self.add_menu(menu, 64)

    def show_video_(self, type: int, index: int):
        if type == 1:
            self.change_video_1(index)
        elif type == 4:
            self.change_video_4(index)
        elif type == 6:
            self.change_video_6(index)
        elif type == 8:
            self.change_video_8(index)
        elif type == 9:
            self.change_video_9(index)
        elif type == 13:
            self.change_video_13(index)
        elif type == 16:
            self.change_video_16(index)
        elif type == 25:
            self.change_video_25(index)
        elif type == 36:
            self.change_video_36(index)
        elif type == 64:
            self.change_video_64(index)

        self.videoMaxSignal.emit(False)

    def show_video(self):
        # 识别具体是哪个动作菜单触发的
        action = self.sender()
        # 从弱属性取出值
        index = int(action.property("index")) - 1
        type = int(action.property("type"))
        videoType = action.property("flag")
        # 只有当画面布局类型改变了才需要切换
        if self.videoType != videoType:
            self.videoType = videoType
            self.show_video_(type, index)

    def show_video_all(self):
        type = 1
        if self.videoType.startswith("0_"):
            index = int(self.videoType.split("_")[-1]) - 1
            self.change_video_1(index)
            self.videoMaxSignal.emit(True)
        else:
            index = int(self.videoType.split("_")[0]) - 1
            for key in self.types:
                flags = self.types[key]
                if self.videoType in flags:
                    type = key
                    self.show_video_(type, index)
                    break

    def hide_video_all(self):
        for i in range(self.videoCount):
            self.gridLayout.removeWidget(self.widgets[i])
            self.widgets[i].setVisible(False)

    def change_video_normal(self, index: int, flag: int):
        self.hide_video_all()

        size = 0
        row = 0
        column = 0

        for i in range(self.videoCount):
            if i >= index:
                self.gridLayout.addWidget(self.widgets[i], row, column)
                self.widgets[i].setVisible(True)

                size += 1
                column += 1
                if column == flag:
                    row += 1
                    column = 0
            if size == flag * flag:
                break

    def change_video_custom(self, index: int, type: int):
        indexs = [i for i in range(index, index + type)]

        if type == 6:
            self.change_video_6_s(indexs)
        elif type == 8:
            self.change_video_8_s(indexs)
        elif type == 13:
            self.change_video_13_s(indexs)

    def change_video_1(self, index):
        self.hide_video_all()
        self.widgets[index].setVisible(True)
        self.gridLayout.addWidget(self.widgets[index], 0, 0)

    def change_video_4(self, index: int):
        self.change_video_normal(index, 2)

    def change_video_6(self, index: int):
        self.change_video_custom(index, 6)

    def change_video_8(self, index: int):
        self.change_video_custom(index, 8)

    def change_video_9(self, index: int):
        self.change_video_normal(index, 3)

    def change_video_13(self, index: int):
        self.change_video_custom(index, 13)

    def change_video_16(self, index: int):
        self.change_video_normal(index, 4)

    def change_video_25(self, index: int):
        self.change_video_normal(index, 5)

    def change_video_36(self, index: int):
        self.change_video_normal(index, 6)

    def change_video_64(self, index: int):
        self.change_video_normal(index, 8)

    def change_video_6_s(self, indexs: list):
        if len(indexs) < 6:
            return
        self.hide_video_all()
        self.gridLayout.addWidget(self.widgets[indexs[0]], 0, 0, 2, 2)
        self.gridLayout.addWidget(self.widgets[indexs[1]], 0, 2, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[2]], 1, 2, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[3]], 2, 2, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[4]], 2, 1, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[5]], 2, 0, 1, 1)
        for i in range(len(indexs)):
            self.widgets[i].setVisible(True)

    def change_video_8_s(self, indexs: list):
        if len(indexs) < 8:
            return
        self.hide_video_all()

        self.gridLayout.addWidget(self.widgets[indexs[0]], 0, 0, 3, 3)
        self.gridLayout.addWidget(self.widgets[indexs[1]], 0, 3, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[2]], 1, 3, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[3]], 2, 3, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[4]], 3, 3, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[5]], 3, 2, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[6]], 3, 1, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[7]], 3, 0, 1, 1)
        # 设置通道控件可见
        for i in indexs:
            self.widgets[i].setVisible(True)

    def change_video_13_s(self, indexs: list):
        if len(indexs) < 13:
            return
        self.hide_video_all()

        self.gridLayout.addWidget(self.widgets[indexs[0]], 0, 0, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[1]], 0, 1, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[2]], 0, 2, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[3]], 0, 3, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[4]], 1, 0, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[5]], 2, 0, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[6]], 1, 1, 2, 2)
        self.gridLayout.addWidget(self.widgets[indexs[7]], 1, 3, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[8]], 2, 3, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[9]], 3, 0, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[10]], 3, 1, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[11]], 3, 2, 1, 1)
        self.gridLayout.addWidget(self.widgets[indexs[12]], 3, 3, 1, 1)
        # 设置通道控件可见
        for i in indexs:
            self.widgets[i].setVisible(True)
