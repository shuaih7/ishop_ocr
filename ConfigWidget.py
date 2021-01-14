#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 01.14.2021
Updated on 01.14.2021

Author: haoshuai@handaotech.com
"""

import os, sys, json
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QTabWidget, QFileDialog

abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)


class ConfigWidget(QTabWidget):
    cameraCfgSignal = pyqtSignal()
    lightCfgSignal = pyqtSignal()
    modelCfgSignal = pyqtSignal()
    
    def __init__(self, config_matrix, messager):
        super(ConfigWidget, self).__init__()
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "ConfigWidget.ui"), self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.config_matrix = config_matrix
        self.messager = messager
        
        # Load the current camera configurations
        self.snLine.setText(str(config_matrix["Camera"]["DeviceSerialNumber"]))
        #self.exposeLine.setValidator(QIntValidator(0,1000000))
        self.exposeLine.setText(str(config_matrix["Camera"]["ExposureTime"]))
        #self.gainLine.setValidator(QIntValidator(0,1000))
        self.gainLine.setText(str(config_matrix["Camera"]["Gain"]))
        #self.binningLine.setValidator(QIntValidator(1,4))
        self.binningLine.setText(str(config_matrix["Camera"]["Binning"]))
        
        # Load the current lighting configurations
        # ......
        
    @pyqtSlot()    
    def cameraConfig(self):
        # Save the camera configurations
        self.config_matrix["Camera"]["DeviceSerialNumber"] = self.snLine.text()
        self.config_matrix["Camera"]["ExposureTime"] = int(self.exposeLine.text())
        self.config_matrix["Camera"]["Gain"] = int(self.gainLine.text())
        self.config_matrix["Camera"]["Binning"] = int(self.binningLine.text())
        
        self.cameraCfgSignal.emit()
        self.saveConfig()
        self.exitConfig()
    
    @pyqtSlot()    
    def lightConfig(self):    
        # Save the lighting configurations
        # ......
        self.lightCfgSignal.emit()
        self.saveConfig()
        self.exitConfig()
    
    @pyqtSlot()    
    def modelConfig(self):  
        # Save the model configurations
        # ......
        self.modelCfgSignal.emit()
        self.saveConfig()
        self.exitConfig()

    @pyqtSlot()
    def exitConfig(self):
        self.close()
    
    def saveConfig(self):
        json_file = os.path.join(abs_path, "config.json")
        with open(json_file, "w", encoding="utf-8") as f:
            cfg_obj = json.dumps(self.config_matrix, indent=4)
            f.write(cfg_obj)
            f.close()
            
    