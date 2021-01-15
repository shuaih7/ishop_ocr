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
from PyQt5.QtWidgets import QTabWidget, QMessageBox, QFileDialog

abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)


class ConfigWidget(QTabWidget):
    generalCfgSignal = pyqtSignal()
    cameraCfgSignal = pyqtSignal()
    lightCfgSignal = pyqtSignal()
    modelCfgSignal = pyqtSignal()
    
    def __init__(self, config_matrix, messager):
        super(ConfigWidget, self).__init__()
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "ConfigWidget.ui"), self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.config_matrix = config_matrix
        self.messager = messager
        
    @pyqtSlot()    
    def generalConfig(self):
        if self.liveModeBtn.isChecked():
            self.config_matrix["Global"]["mode"] = "live"
        else:
            self.config_matrix["Global"]["mode"] = "file"
        self.config_matrix["Global"]["file_folder"] = self.folderLine.text()
        
        self.generalCfgSignal.emit()
        self.saveConfig()
        self.exitConfig()
        
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
        isValidPath = True
        
        model_doc_dir = self.docModelLine.text()
        rec_prefix = os.path.join("rec", self.config_matrix["Model_DOC"]["build_params"]["lang"])
        if not self.checkModelPath(model_doc_dir, rec_prefix):
            QMessageBox.warning(self,"路径错误", "请检查件号识别模型路径！", QMessageBox.Yes)
            isValidPath = False
        
        model_ocr_dir = self.ocrModelLine.text()
        rec_prefix = os.path.join("rec", self.config_matrix["Model_OCR"]["build_params"]["lang"])
        if not self.checkModelPath(model_ocr_dir, rec_prefix):
            QMessageBox.warning(self,"路径错误", "请检查交接单检测模型路径！", QMessageBox.Yes)
            isValidPath = False
        
        if isValidPath:
            self.config_matrix["Model_DOC"]["build_params"]["model_dir"] = model_doc_dir
            self.config_matrix["Model_OCR"]["build_params"]["model_dir"] = model_ocr_dir
            self.config_matrix["Global"]["use_gpu"] = self.gpuBtn.isChecked()
            self.config_matrix["Global"]["gpu_mem"] = int(self.gpuMemLine.text())
            self.modelCfgSignal.emit()
            self.saveConfig()
            self.exitConfig()
            
    @pyqtSlot()
    def setDocModelDir(self):
        model_doc_dir = QFileDialog.getExistingDirectory()
        self.docModelLine.setText(model_doc_dir)
        
    @pyqtSlot()
    def setOcrModelDir(self):
        model_ocr_dir = QFileDialog.getExistingDirectory()
        self.ocrModelLine.setText(model_ocr_dir)
        
    @pyqtSlot()
    def setFileFolder(self):
        folder_dir = QFileDialog.getExistingDirectory()
        self.folderLine.setText(folder_dir)
            
    def checkModelPath(self, path, rec_prefix=None):
        if not os.path.exists(path): return False
        
        cls_path = os.path.join(path, "cls")
        det_path = os.path.join(path, "det")
        
        if rec_prefix is None:
            rec_path = os.path.join(path, "rec")
        else:
            rec_path = os.path.join(path, rec_prefix)
        
        if os.path.exists(cls_path) and os.path.exists(det_path) and os.path.exists(rec_path):
            return True
        else:
            return False
            
    def showConfig(self):
        # Load the general configurations
        if self.config_matrix["Global"]["mode"] == "live":
            self.liveModeBtn.setChecked(True)
        elif self.config_matrix["Global"]["mode"] == "file":
            self.fileModeBtn.setChecked(True)
    
        # Load the current camera configurations
        self.snLine.setText(str(self.config_matrix["Camera"]["DeviceSerialNumber"]))
        #self.exposeLine.setValidator(QIntValidator(0,1000000))
        self.exposeLine.setText(str(self.config_matrix["Camera"]["ExposureTime"]))
        #self.gainLine.setValidator(QIntValidator(0,1000))
        self.gainLine.setText(str(self.config_matrix["Camera"]["Gain"]))
        #self.binningLine.setValidator(QIntValidator(1,4))
        self.binningLine.setText(str(self.config_matrix["Camera"]["Binning"]))
    
        # Load the model configurations
        self.gpuBtn.setChecked(self.config_matrix["Global"]["use_gpu"])
        self.gpuMemLine.setText(str(self.config_matrix["Global"]["gpu_mem"]))
        self.docModelLine.setText(self.config_matrix["Model_DOC"]["build_params"]["model_dir"])
        self.ocrModelLine.setText(self.config_matrix["Model_OCR"]["build_params"]["model_dir"])
        self.show()

    @pyqtSlot()
    def exitConfig(self):
        self.close()
    
    def saveConfig(self):
        json_file = os.path.join(abs_path, "config.json")
        with open(json_file, "w", encoding="utf-8") as f:
            cfg_obj = json.dumps(self.config_matrix, indent=4)
            f.write(cfg_obj)
            f.close()
            
    