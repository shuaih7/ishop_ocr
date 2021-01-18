#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.17.2021
Updated on 01.17.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton


class PushButton(QPushButton):
    
    def __init__(self, parent=None):
        super(PushButton, self).__init__(parent)
        self.main_style = "font-size: 22px;height: 36px;width: 100px; border:2px groove gray; border-radius:15px;padding:2px 4px;"
        self.cfg_style = "font-size: 20px;height: 30px;width: 80px; border:2px groove gray;border-radius:10px;padding:2px 4px;"
        self.color = "background-color:rgb(180,180,180)"
        self.press_color = "background-color: rgb(140,140,140)"
        
        self.mainBtnList = ["scanBtn", "ocrBtn", "reportBtn", "clearBtn", "configBtn"]
        self.cfgBtnList = ["folderBtn", "docModelBtn", "ocrModelBtn",
                           "generalSaveBtn", "generalExitBtn",
                           "cameraSaveBtn", "cameraExitBtn",
                           "lightSaveBtn", "lightExitBtn",
                           "modelSaveBtn", "modelExitBtn"]

    def mousePressEvent(self, event):
        if self.objectName() in self.mainBtnList:
            self.setStyleSheet(self.main_style+self.press_color)
        elif self.objectName() in self.cfgBtnList:
            self.setStyleSheet(self.cfg_style+self.press_color)
        super(PushButton, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.objectName() in self.mainBtnList:
            self.setStyleSheet(self.main_style+self.color)
        elif self.objectName() in self.cfgBtnList:
            self.setStyleSheet(self.cfg_style+self.color)
        super(PushButton, self).mouseReleaseEvent(event)
        

            