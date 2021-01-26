#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.13.2021
Updated on 01.13.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter
from utils import draw_texts


class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super(ImageLabel, self).__init__(parent)
        self.config_matrix = None
        self.pixmap = None
        self.pixmap_hold = None
        self.disp_intv = 1
        self.disp_count = 0
        
    def setConfig(self, config_matrix, messager):
        self.config_matrix = config_matrix
        self.disp_intv = self.config_matrix["Global"]["disp_intv"]
        self.messager = messager

    def refresh(self, image, mode=None, rois=None):
        if rois is not None:
            for roi in rois:
                r0, c0 ,r1, c1 = roi[0]
                pos = [(c0+c1)/2, (r0+r1)/2]
                text = str(roi[1])
                image = draw_texts(image, [text], [pos], size=5, color=(255,165,0), thickness=20)
    
        h, w, ch = image.shape
        bytesPerLine = ch*w
        convertToQtFormat = QImage(image.data.tobytes(), w, h, bytesPerLine, QImage.Format_RGB888)
            
        if mode == "hold" and self.disp_count == 0:
            self.pixmap_hold = QPixmap.fromImage(convertToQtFormat).scaled(self.size(), 
                                    Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.pixmap = self.pixmap_hold
            self.disp_count += 1
            self.update()
        elif self.disp_count > 0 and self.disp_count < self.disp_intv:
            self.pixmap = self.pixmap_hold
            self.disp_count += 1
            self.update()
        elif self.disp_count == self.disp_intv:
            self.disp_count = 0
        else:
            self.pixmap = QPixmap.fromImage(convertToQtFormat).scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.update()
            

    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.pixmap is not None: 
            off_x = (self.size().width() - self.pixmap.width()) / 2
            off_y = (self.size().height() - self.pixmap.height()) / 2
            painter.drawPixmap(off_x, off_y, self.pixmap)
        
