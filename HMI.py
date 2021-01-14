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
import json
import time
import numpy as np

abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)

from paddleocr import PaddleOCR
from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem

import gxipy as gx
from log import getLogger
from utils import write_excel
from ConfigWidget import ConfigWidget


class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "HMI.ui"), self)
        
        # Load the configuration matrix
        config_file = os.path.join(abs_path, "config.json")
        with open (config_file, "r") as f: 
            self.config_matrix = json.load(f)
            
        self.mode = self.config_matrix["Global"]["mode"]
        self.imageLabel.setConfig(self.config_matrix, self.messager)
        self.partTable.setConfig(self.config_matrix, self.messager)
        
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
            
        # Initialize the configuration widget
        self.configWidget = ConfigWidget(self.config_matrix, self.messager)
        self.configWidget.cameraCfgSignal.connect(self.cameraConfig)
        self.configWidget.lightCfgSignal.connect(self.lightConfig)
        self.configWidget.modelCfgSignal.connect(self.modelConfig)
            
        # Initialization
        self.image = None
        self.isLive = False
        self.part_list = []
        self.scan_dict = {}
        self.initModels()
            
    def liveStream(self):
        if self.isLive: return
        
        if self.mode.lower() == "test":
            self.isLive = True
            while self.isLive:
                image_file = os.path.join(abs_path, r"data/imgs/sample.jpg")
                self.image = cv2.imread(image_file, cv2.IMREAD_COLOR)
                self.imageLabel.refresh(self.image)
                QApplication.processEvents()
        else:
            # self.startBtn.setText("连接相机")
            camera_config = self.config_matrix["Camera"]
        
            # Fetch the config parameters
            SN = camera_config['DeviceSerialNumber']
            ExposureTime = camera_config['ExposureTime']
            Gain = camera_config['Gain']
            Binning = camera_config['Binning']

            # create a device manager
            device_manager = gx.DeviceManager()
            dev_num, dev_info_list = device_manager.update_device_list()
            
            if dev_num == 0: 
                self.messager("Camera with the serial number {} does not in the list.".format(SN), flag="warning")
                return
            else:
                self.messager("Found camera {}, connecting...".format(SN), flag="info")
                
            # open the camera device by serial number
            try:
                cam = device_manager.open_device_by_sn(SN)
                self.camera = cam

                # set exposure & gain
                cam.ExposureTime.set(ExposureTime)
                cam.Gain.set(Gain)
                try: # Because some DH cameras do not support "binning"
                    cam.BinningHorizontal.set(Binning)
                    cam.BinningVertical.set(Binning)
                except Exception as expt: 
                    self.messager(expt, flag="warning")
                
                
                # set trigger mode and trigger source
                # cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
                cam.TriggerMode.set(gx.GxSwitchEntry.ON)
                cam.TriggerSource.set(gx.GxTriggerSourceEntry.SOFTWARE)
                
                # Set the status to the capturing mode
                cam.stream_on()
                self.messager("Successfully connected camera {}.".format(SN), flag="info")
                
            except Exception as expt:
                if self.camera is not None:
                    self.camera.stream_off()
                    self.camera.close_device()
                    self.messager(expt, flag="warning")
                    self.liveStream()
                else:
                    self.messager(expt, flag="error")
                return
            
            self.isLive = True
            while self.isLive: 
                try:
                    self.camera.TriggerSoftware.send_command()
                    image_raw = self.camera.data_stream[0].get_image()
                    if image_raw is None: continue
                    image = image_raw.get_numpy_array()
                    if image is None: continue
                    else: # Convert gray scale to BGR
                        c = image.shape[-1]
                        if c != 3: image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                        self.image = image
                        self.imageLabel.refresh(self.image)

                except: 
                    self.isLive = False
                    self.messager("Camera connection is interrupted, please reconnect.", flag="error")
                    return
                    
                QApplication.processEvents()
            
            # Make sure to stop the steam and close the device before exit
            cam.stream_off()
            cam.close_device()
            
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
            if self.image is None: return
            self.part_list = []
            image = self.image
            params = self.config_matrix["Model_OCR"]["infer_params"]
            results = self.model_doc.ocr(image, **params)
            
            for result in results:
                self.part_list.append(["1620M0298Z01", [0,0]])
                #self.part_list.append(result[1]) # TODO: result[1] -> [result[1][0], position]
            
            self.matchTable()

    @pyqtSlot()        
    def recDocument(self):
        self.scan_dict = {}
        #image = self.image
        image = cv2.imread(r"E:\Projects\Part_Number\dataset\20210113\test\doc.bmp", cv2.IMREAD_COLOR)
        params = self.config_matrix["Model_DOC"]["infer_params"]
        results = self.model_doc.ocr(image, **params)
        
        index = 0
        for result in results:
            number = result[1][0]
            if self.isValidNumber(number): 
                number = self.formatNumber(number)
                self.scan_dict[number] = {"position": "-", "status": "未确认", "id": index}
                index += 1
        
        self.updateTable()
        self.matchTable()

    @pyqtSlot()
    def createReport(self):
        self.messager("Creating reports ...", flag="info")
        save_dir = os.path.join(abs_path, "data/report")
        match_list = self.partTable.getCheckList()
        write_excel(match_list, save_dir)
        
    @pyqtSlot()
    def clearAll(self):
        self.partTable.clearRows()
        self.scan_dict = {}
        self.part_list = []
        
    @pyqtSlot()
    def systemConfig(self):
        self.configWidget.show()
        
    @pyqtSlot()
    def cameraConfig(self):
        if self.mode == "test": return
        self.isLive = False
        self.messager(msg="Refreshing the camera configurations, restarting...", flag="info")
        self.liveStream()
        
    @pyqtSlot()
    def lightConfig(self):
        pass
        
    @pyqtSlot()
    def modelConfig(self):
        pass
    
    @pyqtSlot(QTableWidgetItem)    
    def updateStatus(self, item):
        self.partTable.updateStatus(item)
        
    def updateTable(self):
        self.partTable.updateRows(self.scan_dict)
        
    def matchTable(self):
        self.partTable.matchRows(self.part_list, self.scan_dict)
        
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
     
    def messager(self, msg, flag="info"): 
        self.logger_flags[flag](msg)
        
    def closeEvent(self, ev):   
        reply = QMessageBox.question(
            self,
            "退出程序",
            "您确定要退出吗?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

        if reply == QMessageBox.Yes: 
            self.messager("i-shopOCR user interface has been closed.\n", flag="info")
            sys.exit()
            #ev.accept()
        else: ev.ignore()
      
        
        
