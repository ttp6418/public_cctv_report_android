import kivy  # ver 2.0.0
kivy.require('2.0.0')
# kivy.require('1.0.7')
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
# from kivy.lang import Builder
from kivy.uix.camera import Camera
# from kivy.uix.slider import Slider
from kivy.uix.image import Image
# from kivy.uix.video import Video
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty
# from kivy_deps import sdl2, glew
from kivy.logger import Logger
# from kivy_garden.xcamera import XCamera
# from kivy.core.image import Image as CoreImage
# from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
# from kivy.utils import platform
# from kivy.clock import mainthread
# from kivy.uix.filechooser import FileChooserController
# from kivy.uix.screenmanager import Screen, ScreenManager
# from kivy.properties import ListProperty, Property, PropertyStorage
from kivy.config import Config

# from android.permissions import Permission, check_permission
# from android.permissions import request_permissions, Permission
# from storage import SharedStorage

# import json
# import io
import glob
import cv2
# import PIL
# import ffmpeg

import time
# import jnius
# import numpy as np

import os
os.environ['KIVY_TEXT'] = 'pil'
os.environ['KIVY_IMAGE'] = 'pil,sd12'
os.environ['KIVY_CAMERA'] = 'opencv'
import platform
import sys

import socket
import threading

import requests
# from bs4 import BeautifulSoup

# fontk = 'font/Cafe24Dangdanghae.ttf'

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # 마우스 우클릭간 깨지는 문제방지
Config.set('kivy', 'exit_on_escape', '1')  # 닫기 허용
Config.set('kivy', 'desktop', '1')  # 스크롤 True
Config.set('kivy', 'log_dir', 'full path to save log report')  # 로그 경로
Config.set('kivy', 'log_enable', '1')  # 로그 허용
Config.set('kivy', 'window_icon', str(os.path.dirname(os.path.abspath(__file__))) + '/data/icon.png')
Config.set('graphics', 'borderless', '1')


def onDefine():
    global page

    page = ['log']

    global TCP_IP
    global port
    global init_connect

    TCP_IP = '127.0.0.1'
    port = 5001
    init_connect = False


def receive_all(sock, length):
    buf = b''
    try:
        step = length
        while True:
            data = sock.recv(step)
            buf = buf + data
            if len(buf) == length:
                break
            elif len(buf) < length:
                step = length - len(buf)
    except Exception as e:  # 예외처리해준거에대한 실행문
        print(e)
    return buf[:length]


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath('__file__')))

    return os.path.join(base_path, relative_path)


class KivyApp(App):
    def build(self):
        """def onPermission():
            if not is_android():
                return True
            permission = Permission.CAMERA
            return check_permission(permission)
        def onPermission_reg(permissions, result):
            onPermission()"""

        main_tap = android_tap()
        return main_tap

    def on_stop(self):
        return True


class android_tap(GridLayout):
    def __init__(self, **kwargs):
        super(android_tap, self).__init__(**kwargs)

        self.cols = 1
        self.rows = 1

        # self.row_force_default = True
        self.row_default_height = 40
        self.padding = [20, 20, 20, 20]  # left/top/right/bottom
        # self.col_force_default = True
        self.col_default_width = 40

        self.main_tap = TabbedPanel(size_hint=(1, 1))
        self.main_tap.do_default_tab = False  # 기본탭 x
        for [index, tab] in enumerate(page):
            self.tabs = TabbedPanelItem(text=page[index] + ' Page')
            if tab == page[0]:
                self.tabs.add_widget(android_log())
                self.main_tap.set_def_tab(self.tabs)
            self.main_tap.add_widget(self.tabs)
        self.add_widget(self.main_tap)


class android_log(GridLayout):
    global collectable_check

    def __init__(self, **kwargs):
        super(android_log, self).__init__(**kwargs)

        self.cols = 1
        self.rows = 3

        # self.row_force_default = True
        self.row_default_height = 40
        self.padding = [20, 20, 20, 20]  # left/top/right/bottom
        # self.col_force_default = True
        self.col_default_width = 40

        self.info = GridLayout(size_hint=(1, 0.02))  # 상단 내부 레이아웃!
        self.info.cols = 2
        self.info.rows = 1
        self.text_date = TextInput(text='Puts Date Info, ex)1990_01_01', height=50, size_hint_x=0.7, size_hint_y=1)
        self.btn_commu = Button(text='Recieve', height=50, size_hint_x=0.3, size_hint_y=1)
        self.btn_commu.bind(on_press=self.onCommu)
        self.info.add_widget(self.text_date)
        self.info.add_widget(self.btn_commu)
        self.add_widget(self.info)

        self.log = GridLayout(size_hint=(1, 0.93))
        self.log.cols = 1
        self.log.rows = 1
        self.log_text = TextInput(text='Log Info', height=410, size_hint_x=1, size_hint_y=1)
        self.log.add_widget(self.log_text)
        self.add_widget(self.log)

        self.back = GridLayout(size_hint=(1, 0.05))
        self.back.rows = 1
        self.back.cols = 1
        self.btn_back = Button(text='Exit', height=50, size_hint_x=1, size_hint_y=1)
        self.btn_back.bind(on_press=self.onExit)
        self.back.add_widget(self.btn_back)
        self.add_widget(self.back)


    def onCommu(self, instance):
        global filename

        filename = self.text_date.text
        print(filename)
        print(instance)
        recv_lock = True
        if len(filename) == 10:
            try:
                socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_client.connect((TCP_IP, port))
                socket_client.sendall(str('2999').encode())
                time.sleep(0.2)
                recv_lock = False
            except:
                print('서버와의 연결 실패')
                self._popup_alert = Popup(title="Alert Window", content=Label(text='failed connection'), size_hint=(0.8, 0.2))
                self._popup_alert.open()
            if recv_lock == False:
                print('RECV')
                recv_lock = True
                socket_client.sendall(filename.encode())
                time.sleep(0.4)
                length = int(receive_all(socket_client, 10).decode())
                time.sleep(0.2)
                data = receive_all(socket_client, length).decode()
                time.sleep(2)
                self.log_text.text = str(data)
                print(data)
                socket_client.close()
        else:
            self._popup_alert = Popup(title="Alert Window", content=Label(text='puts date info, ex)1990_10_01'), size_hint=(0.8, 0.2))
            self._popup_alert.open()


    def onExit(self, instance):
        print(instance)
        exit(1)


if __name__ == '__main__':
    onDefine()
    KivyApp().run()