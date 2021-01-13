#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.13.2021
Updated on 12.31.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
import cv2
import datetime
import json
import time
import numpy as np
import glob as gb

abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)

from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QEvent, QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QMessageBox

#from third_party import gxipy as gx
from log import getLogger
#from Workers import videoWorker


class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "HMI.ui"), self)
        
        # Load the configuration matrix
        config_file = os.path.join(abs_path, "config.json")
        with open (config_file, "r") as f: 
            self.config_matrix = json.load(f)
            
        self.mode = self.config_matrix["mode"]
        self.imageLabel.setConfig(self.config_matrix)
        
        # Config the devices
        self.camera = None
        self.lighting = None
        self.logger = getLogger(os.path.join(abs_path,"log"), log_name="logging.log")
        self.logger_flags = {
            "debug":    self.logger.debug,
            "info":     self.logger.info,
            "warning":  self.logger.warning,
            "error":    self.logger.error,
            "critical": self.logger.critical}
            
        # Initialization
        self.image = None
            
    def liveStream(self):
        if self.mode.lower() == "test":
            while True:
                image_file = os.path.join(abs_path, r"data/imgs/sample.jpg")
                self.image = cv2.imread(image_file, cv2.IMREAD_COLOR)
                self.imageLabel.refresh(self.image)
                QApplication.processEvents()
        else:
            # TODO: add camera functions here ...
            QApplication.processEvents()
        
    def message(self, msg, flag="info"): 
        self.logger_flags[flag](msg)
        
    def closeEvent(self, ev):   
        reply = QMessageBox.question(
            self,
            "退出程序",
            "您确定要退出吗?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

        if reply == QMessageBox.Yes: 
            #if self.isInferring: self.isInferring = False
            #if self.isRunning: self.isRunning = False
            self.message("ishopOCR UI 已关闭。\n", flag="info")
            sys.exit()
            #ev.accept()
        else: ev.ignore()
      
        
        
