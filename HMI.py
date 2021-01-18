#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.13.2021
Updated on 01.17.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
import cv2
import json
import time
import glob as gb
import numpy as np

abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)

from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem

import gxipy as gx
from paddleocr.paddleocr import PaddleOCR
from log import getLogger
from utils import draw_polylines, write_excel, SNPatch
from ConfigWidget import ConfigWidget
from PushButton import PushButton


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
        self.configWidget.generalCfgSignal.connect(self.generalConfig)
        self.configWidget.cameraCfgSignal.connect(self.cameraConfig)
        self.configWidget.lightCfgSignal.connect(self.lightConfig)
        self.configWidget.modelCfgSignal.connect(self.modelConfig)
            
        # Initialization
        self.image = None
        self.camera = None
        self.isLive = False
        self.patch = SNPatch()
        self.doc_folder = self.config_matrix["Global"]["doc_folder"]
        self.ocr_folder = self.config_matrix["Global"]["ocr_folder"]
        self.supported_images = [".bmp", ".png", ".jpg", ".tif"]
        
        self.part_list = []
        self.scan_dict = {}
        self.initModels()
        
    def initCanvas(self):
        if self.mode == "live":
            self.liveStream()
        if not self.isLive:
            self.image = cv2.imread(os.path.join(abs_path, os.path.join(r"data\imgs","preface.jpg")))
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.imageLabel.refresh(self.image)
            
    def liveStream(self):
        if self.isLive or self.mode == "file": return
        elif self.mode == "live":
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
            
    def closeLiveStream(self):
        if self.camera is not None:
            try: self.camera.close_device()
            except Exception as expt: pass
            self.image = cv2.imread(os.path.join(abs_path, os.path.join(r"data\imgs","preface.jpg")))
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.imageLabel.refresh(self.image)
            
    def initModels(self):
        params_doc = self.config_matrix["Model_DOC"]
        params_doc["build_params"]["use_gpu"] = self.config_matrix["Global"]["use_gpu"]
        params_doc["build_params"]["gpu_mem"] = self.config_matrix["Global"]["gpu_mem"]
        params_ocr = self.config_matrix["Model_OCR"]
        params_ocr["build_params"]["use_gpu"] = self.config_matrix["Global"]["use_gpu"]
        params_ocr["build_params"]["gpu_mem"] = self.config_matrix["Global"]["gpu_mem"]
        
        self.model_doc = PaddleOCR(**self.extendModelParams(params_doc["build_params"]))
        self.model_ocr = PaddleOCR(**self.extendModelParams(params_ocr["build_params"]))
    
    @pyqtSlot()    
    def recParts(self):
        if len(self.scan_dict) == 0:
            QMessageBox.warning(self,"警告", "请先扫描交接单！", QMessageBox.Yes)
        else:
            self.part_list = []
            params = self.config_matrix["Model_OCR"]["infer_params"]
            
            if self.mode == "file":
                img_list = self.imageLoader(self.ocr_folder)
                
                for img_file in img_list:
                    image = cv2.imread(img_file, cv2.IMREAD_COLOR)
                    if image is None: 
                        continue
                    else:
                        results = self.model_ocr.ocr(image, **params)
                        
                    for result in results:
                        self.part_list.append([result[1][0], "(0,0)"])
                        points = np.array(result[0],dtype=np.float32)
                        texts = result[1][0]
                        image = draw_polylines(image, [points], [texts], size=0.5, color=(0,255,0))
                                 
                    _, filename = os.path.split(img_file)
                    save_path = os.path.join(abs_path, os.path.join("data/result/ocr", filename))
                    #cv2.imwrite(save_path, image)
                    
                    self.imageLabel.refresh(image)
                    QApplication.processEvents()    
                    self.matchTable()
                    
            elif self.mode == "live":
                if self.image is None: return
                if self.camera is None or not self.isLive: return
                image = self.image
                results = self.model_ocr.ocr(image, **params)
                
                for result in results:
                    self.part_list.append([result[1][0], "(0,0)"]) # TODO: result[1] -> [result[1][0], position]
                    points = np.array(result[0],dtype=np.float32)
                    texts = result[1][0]
                    image = draw_polylines(image, [points], [texts], size=0.5, color=(0,255,0))
                 
                self.imageLabel.refresh(image, mode="hold")
                QApplication.processEvents()   
                self.matchTable()

    @pyqtSlot()        
    def recDocument(self):
        self.scan_dict = {}
        params = self.config_matrix["Model_DOC"]["infer_params"]
        
        if self.mode == "file":
            img_list = self.imageLoader(self.doc_folder)
            
            for img_file in img_list:
                image = cv2.imread(img_file, cv2.IMREAD_COLOR)
                if image is None: 
                    continue
                else:
                    results = self.model_doc.ocr(image, **params)
                
                index = 0
                for result in results:
                    number = result[1][0]
                    if self.isValidNumber(number): 
                        points = np.array(result[0],dtype=np.float32)
                        texts = result[1][0]
                        image = draw_polylines(image, [points], [texts], size=0.5, color=(0,255,0))
                        number = self.formatNumber(number)
                        self.scan_dict[number] = {"position": "-", "status": "未确认", "id": index}
                        index += 1
                
                _, filename = os.path.split(img_file)
                save_path = os.path.join(abs_path, os.path.join("data/result/doc", filename))
                #cv2.imwrite(save_path, image)
                        
                self.imageLabel.refresh(image)
                self.updateTable()
                self.matchTable()
        
        elif self.mode == "live":
            if self.image is None: return
            if self.camera is None or not self.isLive: return
            
            image = self.image
            results = self.model_doc.ocr(image, **params)
            index = 0
            for result in results:
                number = result[1][0]
                if self.isValidNumber(number): 
                    points = np.array(result[0],dtype=np.float32)
                    texts = result[1][0]
                    image = draw_polylines(image, [points], [texts], size=0.5, color=(0,255,0))
                    number = self.formatNumber(number)
                    self.scan_dict[number] = {"position": "-", "status": "未确认", "id": index}
                    index += 1
                    
            self.imageLabel.refresh(image, mode="hold")
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
        self.configWidget.showConfig()
        
    @pyqtSlot()
    def generalConfig(self):
        self.mode = self.config_matrix["Global"]["mode"]
        if self.mode == "file":
            self.closeLiveStream()
        elif self.mode == "live" and not self.isLive:
            self.liveStream()
            
        self.doc_folder = self.config_matrix["Global"]["doc_folder"]
        self.ocr_folder = self.config_matrix["Global"]["ocr_folder"]
            
    @pyqtSlot()
    def cameraConfig(self):
        if self.mode == "file": return
        self.isLive = False
        self.messager(msg="Refreshing the camera configurations, restarting...", flag="info")
        self.liveStream()
        
    @pyqtSlot()
    def lightConfig(self):
        pass
        
    @pyqtSlot()
    def modelConfig(self):
        self.initModels()
    
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
        
    def extendModelParams(self, params):
        model_dir = params['model_dir']
        
        if model_dir is None: 
            params['cls_model_dir'] = None
            params['det_model_dir'] = None
            params['rec_model_dir'] = None
        else:
            params['cls_model_dir'] = os.path.join(model_dir, "cls")
            params['det_model_dir'] = os.path.join(model_dir, "det")
            params['rec_model_dir'] = os.path.join(model_dir, os.path.join("rec", params["lang"]))
        
        return params
        
    def imageLoader(self, folder):
        img_list = []
        for suffix in self.supported_images:
            img_list += gb.glob(folder + r"/*"+suffix)
        return sorted(img_list, key=os.path.getmtime)
     
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
      
        
        
