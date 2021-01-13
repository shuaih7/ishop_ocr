#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.13.2021
Updated on 01.13.2021

Author: haoshaui@handaotech.com
'''


import os
import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal


class videoWorker(QThread):
    """Get each frame from the camera and update the imageLabel widget

    Attributes:
        config_matrix: configuration matrix
        messager: self-defined logger
    
    """
    imgSignal = pyqtSignal(np.ndarray)

    def __init__(self, config_matrix, messager, parent=None):
        super(revWorker, self).__init__(parent)
        self.config_matrix = config_matrix
        self.messager = messager

    def run(self):
        if self.config_matrix["mode"] == "test":
            abs_path = os.path.abspath(os.path.dirname(__file__))
            image_file = os.path.join(abs_path, r"data/imgs/sample.jpg")
            image = cv2.imread(image_file, cv2.IMREAD_COLOR)
            self.imgSignal.emit(image)
        else: pass