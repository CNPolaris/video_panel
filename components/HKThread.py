# -*- coding: utf-8 -*-
import os
import platform

from PySide6.QtCore import QThread
from components.HCNetSDK import *
from components.PlayCtrl import *

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("video")

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__))).split('utils')[0]
sdk_path = BASE_DIR + os.sep + 'plugins' + os.sep + 'hk' + os.sep + 'sdk' + os.sep


class HKThread(QThread):

    def __init__(self):
        super().__init__()
        self.dev_ip = create_string_buffer(b'192.168.1.64')
        self.dev_port = 8000
        self.username = create_string_buffer(b'admin')
        self.password = create_string_buffer(b'admin123')

        self.windows_flag = True
        self.funcRealDataCallBack_V30 = None
        self.Objdll = None  # 网络库
        self.PlayCtrl_Port = c_long(-1)  # 播放句柄
        self.Playctrldll = None  # 播放库
        self.FuncDecCB = None  # 播放库解码回调函数，需要定义为全局的
        self.lRealPlayHandle = None

        self.dev_info = None
        self.user_id = None

        self.stopped = False
        self.winId = None

    def init(self, ip, username, passwd, winId):
        self.dev_ip = create_string_buffer(bytes(ip, encoding='utf8'))
        self.username = create_string_buffer(bytes(username, encoding='utf8'))
        self.password = create_string_buffer(bytes(passwd, encoding='utf8'))
        self.winId = winId

        self.GetPlatform()
        self.loadDll()
        self.SetSDKInitCfg()
        self.Objdll.NET_DVR_Init()
        if not self.Playctrldll.PlayM4_GetPort(byref(self.PlayCtrl_Port)):
            print(u'获取播放库句柄失败')



    # 获取当前系统环境
    def GetPlatform(self):
        sysstr = platform.system()
        print('' + sysstr)
        if sysstr != "Windows":
            self.windows_flag = False

    def loadDll(self):
        # 加载库,先加载依赖库
        if self.windows_flag:
            os.chdir(sdk_path + 'win')
            self.Objdll = ctypes.CDLL(r'./HCNetSDK.dll')  # 加载网络库
            self.Playctrldll = ctypes.CDLL(r'./PlayCtrl.dll')  # 加载播放库
        else:
            os.chdir(sdk_path + 'linux')
            self.Objdll = cdll.LoadLibrary(r'./libhcnetsdk.so')
            self.Playctrldll = cdll.LoadLibrary(r'./libPlayCtrl.so')

    # 设置SDK初始化依赖库路径
    def SetSDKInitCfg(self):
        # 设置HCNetSDKCom组件库和SSL库加载路径
        # print(os.getcwd())
        if self.windows_flag:
            strPath = os.getcwd().encode('gbk')
            sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath
            self.Objdll.NET_DVR_SetSDKInitCfg(2, byref(sdk_ComPath))
            self.Objdll.NET_DVR_SetSDKInitCfg(3, create_string_buffer(strPath + b'\libcrypto-1_1-x64.dll'))
            self.Objdll.NET_DVR_SetSDKInitCfg(4, create_string_buffer(strPath + b'\libssl-1_1-x64.dll'))
        else:
            strPath = os.getcwd().encode('utf-8')
            sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath
            self.Objdll.NET_DVR_SetSDKInitCfg(2, byref(sdk_ComPath))
            self.Objdll.NET_DVR_SetSDKInitCfg(3, create_string_buffer(strPath + b'/libcrypto.so.1.1'))
            self.Objdll.NET_DVR_SetSDKInitCfg(4, create_string_buffer(strPath + b'/libssl.so.1.1'))

    def LoginDev(self):
        self.dev_info = NET_DVR_DEVICEINFO_V30()
        self.user_id = self.Objdll.NET_DVR_Login_V30(self.dev_ip, self.dev_port, self.username, self.password,
                                                     byref(self.dev_info))
        return self.user_id, self.dev_info

    def DecCBFun(self, nPort, pBuf, nSize, pFrameInfo, nUser, nReserved2):
        # 解码回调函数
        if pFrameInfo.contents.nType == 3:
            # 解码返回视频YUV数据，将YUV数据转成cv
            nWidth = pFrameInfo.contents.nWidth
            nHeight = pFrameInfo.contents.nHeight
            dwFrameNum = pFrameInfo.contents.dwFrameNum
            nStamp = pFrameInfo.contents.nStamp

    def RealDataCallBack_V30(self, lPlayHandle, dwDataType, pBuffer, dwBufSize, pUser):
        # 码流回调
        if dwDataType == NET_DVR_SYSHEAD:
            # 设置流播放模式
            self.Playctrldll.PlayM4_SetStreamOpenMode(self.PlayCtrl_Port, 0)
            # 打开码流，送入40字节系统头数据
            if self.Playctrldll.PlayM4_OpenStream(self.PlayCtrl_Port, pBuffer, dwBufSize, 1024 * 1024):
                # 设置解码回调，可以返回解码后YUV视频数据
                self.FuncDecCB = DECCBFUNWIN(self.DecCBFun)
                self.Playctrldll.PlayM4_SetDecCallBackExMend(self.PlayCtrl_Port, self.FuncDecCB, None, 0, None)

            if self.Playctrldll.PlayM4_Play(self.PlayCtrl_Port, self.winId):
                print(u'调用播放库成功')
            else:
                print(u'调用播放库失败')

        elif dwDataType == NET_DVR_STREAMDATA:
            self.Playctrldll.PlayM4_InputData(self.PlayCtrl_Port, pBuffer, dwBufSize)
        else:
            print(u'其他数据, 长度', dwBufSize)

    def OpenPreview(self, call_back_fun):
        preview_info = NET_DVR_PREVIEWINFO()
        preview_info.hPlayWnd = 0
        preview_info.lChannel = 1  # 通道号
        preview_info.dwStreamType = 0  # 主码流
        preview_info.dwLinkMode = 0  # TCP
        preview_info.bBlocked = 1  # 阻塞取流

        lRealPlayHandle = self.Objdll.NET_DVR_RealPlay_V40(self.user_id, byref(preview_info), call_back_fun, None)
        return lRealPlayHandle

    def free(self):
        self.Objdll.NET_DVR_StopRealPlay(self.lRealPlayHandle)
        if self.PlayCtrl_Port.value > -1:
            self.Playctrldll.PlayM4_Stop(self.PlayCtrl_Port)
            self.Playctrldll.PlayM4_CloseStream(self.PlayCtrl_Port)
            self.Playctrldll.PlayM4_FreePort(self.PlayCtrl_Port)
            self.PlayCtrl_Port = c_long(-1)
        self.Objdll.NET_DVR_Logout(self.user_id)
        self.Objdll.NET_DVR_Cleanup()

        self.winId = None
        self.dev_ip = None
        self.username = None
        self.password = None
        self.stopped = False

    def run(self) -> None:

        (lUserId, device_info) = self.LoginDev()
        if lUserId < 0:
            err = self.Objdll.NET_DVR_GetLastError()
            print('Login device fail, error code is: %d' % self.Objdll.NET_DVR_GetLastError())
            # 释放资源
            self.Objdll.NET_DVR_Cleanup()
            exit()
        self.funcRealDataCallBack_V30 = REALDATACALLBACK(self.RealDataCallBack_V30)
        self.lRealPlayHandle = self.OpenPreview(self.funcRealDataCallBack_V30)

        if self.lRealPlayHandle < 0:
            print('Open preview fail, error code is: %d' % self.Objdll.NET_DVR_GetLastError())
            # 登出设备
            self.Objdll.NET_DVR_Logout(lUserId)
            # 释放资源
            self.Objdll.NET_DVR_Cleanup()
            exit()

        while not self.stopped:
            self.msleep(1)

        self.free()
        self.stopped = True

    def stop(self):
        self.stopped = True

    def zoom_in(self, signal):
        """焦距变大(倍率变大)
        0:有效 1:无效
        """
        lRet = self.Objdll.NET_DVR_PTZControl(self.lRealPlayHandle, ZOOM_IN, signal)
        if lRet == 0:
            print('Start ptz control fail, error code is: %d' % self.Objdll.NET_DVR_GetLastError())
        else:
            print('Start ptz control success')

    def zoom_out(self, signal):
        """焦距变小(倍率变小)
        0:有效 1:无效
        """
        lRet = self.Objdll.NET_DVR_PTZControl(self.lRealPlayHandle, ZOOM_OUT, signal)
        if lRet == 0:
            print('Start ptz control fail, error code is: %d' % self.Objdll.NET_DVR_GetLastError())
        else:
            print('Start ptz control success')

    def ptz_up(self, signal):
        """云台上仰 0:有效 1:无效"""
        lRet = self.Objdll.NET_DVR_PTZControl(self.lRealPlayHandle, TILT_UP, signal)
        if lRet == 0:
            print('Start ptz control fail, error code is: %d' % self.Objdll.NET_DVR_GetLastError())
        else:
            print('Start ptz control success')

    def ptz_down(self, signal):
        """云台下俯 0:有效 1:无效"""
        lRet = self.Objdll.NET_DVR_PTZControl(self.lRealPlayHandle, TILT_DOWN, signal)
        if lRet == 0:
            print('Start ptz control fail, error code is: %d' % self.Objdll.NET_DVR_GetLastError())
        else:
            print('Start ptz control success')

    def ptz_left(self, signal):
        """云台左转 0:有效 1:无效"""
        lRet = self.Objdll.NET_DVR_PTZControl(self.lRealPlayHandle, PAN_LEFT, signal)
        if lRet == 0:
            print('Start ptz control fail, error code is: %d' % self.Objdll.NET_DVR_GetLastError())
        else:
            print('Start ptz control success')

    def ptz_right(self, signal):
        """云台右转 0:有效 1:无效"""
        lRet = self.Objdll.NET_DVR_PTZControl(self.lRealPlayHandle, PAN_RIGHT, signal)
        if lRet == 0:
            print('Start ptz control fail, error code is: %d' % self.Objdll.NET_DVR_GetLastError())
        else:
            print('Start ptz control success')

    def wiper_power(self, signal):
        """接通雨刷开关 0:有效 1:无效"""
        lRet = self.Objdll.NET_DVR_PTZControl(self.lRealPlayHandle, WIPER_PWRON, signal)
        if lRet == 0:
            print('Start ptz control fail, error code is: %d' % self.Objdll.NET_DVR_GetLastError())
        else:
            print('Start ptz control success')

    def light_power(self, signal):
        """接通灯光电源 0:有效 1:无效"""
        lRet = self.Objdll.NET_DVR_PTZControl(self.lRealPlayHandle, LIGHT_PWRON, signal)
        if lRet == 0:
            print('Start ptz control fail, error code is: %d' % self.Objdll.NET_DVR_GetLastError())
        else:
            print('Start ptz control success')
