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
    scanSignal = pyqtSignal()
    ocrSignal = pyqtSignal()
    reportSignal = pyqtSignal()
    clearSignal = pyqtSignal()
    configSignal = pyqtSignal()
    generalSaveSignal = pyqtSignal()
    cameraSaveSignal = pyqtSignal()
    lightSaveSignal = pyqtSignal()
    docModelSignal = pyqtSignal()
    ocrModelSignal = pyqtSignal()
    modelSaveSignal = pyqtSignal()
    exitSignal = pyqtSignal()
    
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

    def mouseReleaseEvent(self, event):
        if self.objectName() in self.mainBtnList:
            self.setStyleSheet(self.main_style+self.color)
        elif self.objectName() in self.cfgBtnList:
            self.setStyleSheet(self.cfg_style+self.color)
        
        if self.objectName() == "scanBtn":
            self.scanSignal.emit()
        elif self.objectName() == "ocrBtn":
            self.ocrSignal.emit()
        elif self.objectName() == "reportBtn":
            self.reportSignal.emit()
        elif self.objectName() == "clearBtn":
            self.clearSignal.emit()
        elif self.objectName() == "configBtn":
            self.configSignal.emit()
            
        elif self.objectName() == "generalSaveBtn":
            self.generalSaveSignal.emit()
        elif self.objectName() == "cameraSaveBtn":
            self.cameraSaveSignal.emit()
        elif self.objectName() == "lightSaveBtn":
            self.lightSaveSignal.emit()
        elif self.objectName() == "docModelBtn":
            self.docModelSignal.emit()
        elif self.objectName() == "ocrModelBtn":
            self.ocrModelSignal.emit()
        elif self.objectName() == "modelSaveBtn":
            self.modelSaveSignal.emit()
        elif "Exit" in self.objectName():
            self.exitSignal.emit()
        

            