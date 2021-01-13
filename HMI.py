#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.13.2021
Updated on 01.14.2021

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

from paddleocr import PaddleOCR
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
            
        self.mode = self.config_matrix["Global"]["mode"]
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
        self.part_list = []
        self.scan_dict = {}
        self.initModels()
            
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
            
    def initModels(self):
        params_doc = self.config_matrix["Model_DOC"]
        params_doc["build_params"]["use_gpu"] = self.config_matrix["Global"]["use_gpu"]
        params_ocr = self.config_matrix["Model_OCR"]
        params_ocr["build_params"]["use_gpu"] = self.config_matrix["Global"]["use_gpu"]
        
        self.model_doc = PaddleOCR(**params_doc["build_params"])
        self.model_ocr = PaddleOCR(**params_ocr["build_params"])
    
    @pyqtSlot()    
    def recParts(self):
        if len(self.scan_dict) == 0:
            QMessageBox.warning(self,"警告", "请先扫描交接单！", QMessageBox.Yes)
        else:
            self.part_list = []
            image = self.image
            params = self.config_matrix["Model_OCR"]["infer_params"]
            results = self.model_doc.ocr(image, **params)
            
            for result in results:
                self.part_list.append(result[1][0])
            
            self.updateTable()

    @pyqtSlot()        
    def recDocument(self):
        self.scan_dict = {}
        #image = self.image
        image = cv2.imread(r"E:\Projects\Part_Number\dataset\20210113\test\doc.bmp", cv2.IMREAD_COLOR)
        params = self.config_matrix["Model_DOC"]["infer_params"]
        results = self.model_doc.ocr(image, **params)
        
        for result in results:
            number = result[1][0]
            if self.isValidNumber(number): 
                 self.scan_dict[number] = {"position": None, "status": None}
        
        self.updateTable()

    @pyqtSlot()
    def createReport(self):
        pass
        
    @pyqtSlot()
    def clearAll(self):
        self.scan_dict = {}
        self.part_list = []
        
    def updateTable(self):
        pass
        
    def isValidNumber(self, number):
        if len(number)>=10 and number[4]=="M":
            return True
        else:
            return False
            
    def formatNumber(self, number):
        number = number.replace("O", "0")
        number = number.replace("o", "0")
        number = number.replace("I", "1")
        if number[-3] == "2": number = number[:-4]+"Z"+number[-2:]
        return number
     
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
            self.message("i-shopOCR user interface has been closed。\n", flag="info")
            sys.exit()
            #ev.accept()
        else: ev.ignore()
      
        
        
