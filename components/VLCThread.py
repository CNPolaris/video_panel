# -*- coding: utf-8 -*-
"""
@author:CNPolaris
"""
import os
import platform

from PySide6.QtCore import QThread

# 将VLC插件加入到系统环境中
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__))).split('utils')[0]
vlc_path = BASE_DIR + 'plugins' + os.sep + 'vlc' + os.sep + '64'
os.environ["PATH"] = vlc_path
import vlc


class VLCThread(QThread):
    def __init__(self) -> None:
        super().__init__()
        self.stopped = False
        self.isPlay = False

        self.url = None

        self.vlcInst = None
        self.vlcMedia = None

        self.isInit = False
        if not self.isInit:
            self.isInit = True

    def run(self) -> None:
        while not self.stopped:
            self.msleep(1)
        # 线程结束后释放资源
        self.free()
        self.stopped = False
        self.isPlay = False

    def set_url(self, url):
        self.url = url

    def set_option(self, option):
        vlc.libvlc_media_add_option(self.vlcMedia, option)

    def init(self, wm_id):
        self.vlcInst = vlc.Instance("--network-caching=300 --codec=mediacodec,iomx,all --file-caching=500")
        if self.vlcInst is None:
            return False
        self.vlcMedia = self.vlcInst.media_player_new(self.url)

        # 设置播放句柄
        self.set_window(wm_id)
        # 设置libvlc忽略鼠标和键盘事件
        vlc.libvlc_video_set_mouse_input(self.vlcMedia, False)
        vlc.libvlc_video_set_key_input(self.vlcMedia, False)
        # 开始播放
        self.vlcMedia.play()
        # 静音
        self.set_volume(0)
        return True

    def set_window(self, wm_id):
        """设置窗口句柄"""
        if platform.system() == "Linux":  # for Linux using the X Server
            self.vlcMedia.set_xwindow(int(wm_id))
        elif platform.system() == "Windows":  # for Windows
            self.vlcMedia.set_hwnd(int(wm_id))
        elif platform.system() == "Darwin":  # for MacOS
            self.vlcMedia.set_nsobject(int(wm_id))

    def play(self, wm_id):
        """设置播放句柄并开始播放"""
        self.isPlay = True
        self.init(wm_id)

    def pause(self):
        """暂停播放"""
        if self.vlcMedia is not None:
            self.vlcMedia.pause()

    def next(self):
        if self.vlcMedia is not None:
            self.vlcMedia.pause()

    def free(self):
        """释放资源"""
        if self.vlcInst is not None:
            self.vlcInst.release()
            self.vlcInst = None

        if self.vlcMedia is not None:
            self.vlcMedia.release()
            self.vlcMedia = None

    def stop(self):
        """停止播放"""
        self.stopped = True

    def set_volume(self, volume:int):
        """设置音量（0~100）"""
        if volume < 0:
            volume = 0
        elif volume > 100:
            volume = 100
        self.vlcMedia.audio_set_volume(volume)

    def get_volume(self):
        """获取当前音量（0~100）"""
        return self.vlcMedia.audio_get_volume()

    def set_ratio(self, ratio):
        """设置宽高比率（如"16:9","4:3"）"""
        self.vlcMedia.video_set_scale(0)  # 必须设置为0，否则无法修改屏幕宽高
        self.vlcMedia.video_set_aspect_ratio(ratio)

    def set_rate(self, rate):
        """设置播放速率（如：1.2，表示加速1.2倍播放）"""
        return self.vlcMedia.set_rate(rate)

    def get_rate(self):
        """获取当前文件播放速率"""
        return self.vlcMedia.get_rate()

    def set_position(self, float_val):
        """拖动当前进度，传入0.0~1.0之间的浮点数(需要注意，只有当前多媒体格式或流媒体协议支持才会生效)"""
        return self.vlcMedia.set_position(float_val)

    def get_position(self):
        """当前播放进度情况。返回0.0~1.0之间的浮点数"""
        return self.vlcMedia.get_position()

    def get_state(self):
        """返回当前状态 不要在播放或暂停等操作后立即查询 稍微延时1s"""
        state = self.vlcMedia.get_state()
        if state == vlc.State.Playing:
            return 1
        elif state == vlc.State.Paused:
            return 0
        else:
            return -1

    def get_time(self):
        """已播放时间，返回毫秒值"""
        return self.vlcMedia.get_time()

    def set_time(self, m_time):
        """拖动指定的毫秒值处播放。成功返回0，失败返回-1 (需要注意，只有当前多媒体格式或流媒体协议支持才会生效)"""
        return self.vlcMedia.set_time(m_time)

    def get_length(self):
        """音视频总长度，返回毫秒值"""
        return self.vlcMedia.get_length()
