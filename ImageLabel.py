#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.13.2021
Updated on 01.26.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QPen, QFont


class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super(ImageLabel, self).__init__(parent)
        self.config_matrix = None
        self.image_shape = None
        self.qimage = None
        self.pixmap = None
        self.pixmap_hold = None
        self.disp_intv = 1
        self.disp_count = 0
        self.rois = None
        self.mode = None
        
    def setConfig(self, config_matrix, messager):
        self.config_matrix = config_matrix
        self.disp_intv = self.config_matrix["Global"]["disp_intv"]
        self.messager = messager
       
    def refresh(self, image, mode=None):
        self.mode = mode
        h, w, ch = image.shape
        self.image_shape = (h, w)
        bytesPerLine = ch*w
        convertToQtFormat = QImage(image.data.tobytes(), w, h, bytesPerLine, QImage.Format_RGB888)
        self.qimage = convertToQtFormat
            
        if mode is not None and self.disp_count == 0:
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
            self.pixmap = QPixmap.fromImage(convertToQtFormat).scaled(self.size(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.update()
            
    def resizeEvent(self, event):
        if self.pixmap is not None:
            self.pixmap = QPixmap.fromImage(self.qimage).scaled(self.size(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.update()

    def paintEvent(self, event):
        if self.pixmap is not None: 
            # Setup the scales
            h, w = self.image_shape
            scalex = self.pixmap.width() / w
            scaley = self.pixmap.height() / h
                
            # Setup the painter
            painter = QPainter(self)
            
            # Setup the pen
            pen = QPen()
            pen.setColor(QColor(255,165,0))
            pen.setWidth(int(23*scalex))
            pen.setStyle(Qt.SolidLine)
            painter.setPen(pen)
            
            # Setup the font
            font = QFont()
            font.setPixelSize(int(150*scalex))
            font.setFamily("Microsoft YaHei")
            painter.setFont(font)
                
            offx = (self.size().width() - self.pixmap.width()) / 2
            offy = (self.size().height() - self.pixmap.height()) / 2
            painter.drawPixmap(offx, offy, self.pixmap)
            
            if self.mode == "ocr":
                if self.rois is None: return
                for roi in self.rois:
                    r0, c0 ,r1, c1 = roi[0]
                    x, y = int(((c0+c1)/2+150)*scalex+offx), int(((r0+r1)/2)*scaley+offy)
                    painter.drawText(x, y, str(roi[1]))
        
