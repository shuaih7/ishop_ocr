#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.27.2021
Updated on 01.27.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
import cv2
import numpy as np
from .base_process import BaseProcess


class OcrProcess(BaseProcess):
    offset = (0, 0)  #(r,c)
    width = 905
    height = 683
    row_nbr, col_nbr = 5, 5

    def __init__(self, model=None, messager=None):
        super(OcrProcess, self).__init__(model=model, messager=messager)
        self.use_patch = True
        self.angle = 90
        self.image_patches = []
        self.image_filtered = None
        self.roi = []  # list of r0,c0,r1,c1
        self.set_roi()
        
    # todo, multiprocessing
    def __call__(self, image, params, mode, app=None):
        return self.infer(image, params, mode, app)
        
    def preprocess(self, image):
        return self.image_patches(image)
        
    def infer(self, image, params, mode, app=None):
        pass
        
    def postprocess(self, image, results):
        pass
        
    # todo, roi setting for config files
    def set_roi(self):
        ''''''
        index = 0
        self.roi = []  # list of r0,c0,r1,c1
        for r in range(self.row_nbr):
            for c in range(self.col_nbr):
                r0, r1 = self.offset[0] + self.height * r, self.offset[0] + self.height * (r + 1)
                c0, c1 = self.offset[1] + self.width * c, self.offset[1] + self.width * (c + 1)
                self.roi.append([(r0,c0,r1,c1), index + 1])
                #print("r0,c0,r1,c1: ",r0, c0, r1, c1)
                index += 1
        return self.roi

    def get_patches(self,img_filtered):
        image_patches = []
        for i,roi in enumerate(self.roi):
            r0,c0,r1,c1 = roi[0]
            img_patch= img_filtered[r0:r1, c0:c1]
            image_patches.append(img_patch)
        return image_patches