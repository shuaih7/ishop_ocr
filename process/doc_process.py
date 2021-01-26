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
from .utils import draw_results


class DocProcess(BaseProcess):
    def __init__(self, model=None, messager=None):
        super(DocProcess, self).__init__(model=model, messager=messager)
        
    def __call__(self, image, params, mode):
        image = self.preprocess(image)
        image, results = self.infer(image, params, mode)
        image, results = self.postprocess(image, results)
        return image, results
        
    def preprocess(self, image):
        return image
        
    def infer(self, image, params, mode):
        if mode == "file":
            if not isinstance(image, str):
                raise ValueError("the input should be the image address for the file mode.")
            
            self.sendMessage("开始检测交接单 "+image+" ...")
            image = cv2.imread(image, cv2.IMREAD_COLOR)
            if image is None: 
                self.sendMessage("未读取到图片 "+image, flag="warning")
                return image, []  # Error loading the image
            
        elif mode == "live":
            self.sendMessage("交接单检测中 ...")
            
        results = self.model.ocr(image, **params)
        self.sendMessage("交接单检测完成。")
        return image, results
            
    def postprocess(self, image, results):
        results = self.filterScanDict(results)
        image = draw_results(image, results, size=2.0, color=(0,255,0), thickness=7)
        return image, results
    
    def filterScanDict(self, results):
        index = 0
        self.scan_dict = {}
        flt_results = []
        
        for result in results:
            number = result[1][0]
            if self.isValidNumber(number): 
                texts = result[1][0]
                number = self.formatNumber(number)
                self.scan_dict[number] = {"position": "-", "status": "未确认", "id": index}
                flt_results.append([result[0], [number, result[1][1]]])
                index += 1
        return flt_results
        
    def isValidNumber(self, number):
        if len(number)>=10 and "M" in number and "A" in number:
            return True
        else:
            return False
            
    def formatNumber(self, number):
        number = number.replace("O", "0")
        number = number.replace("o", "0")
        number = number.replace("I", "1")
        return number
        
                