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
from .enhancement import SNPatch
from .base_process import BaseProcess
from .utils import draw_polylines, draw_results, rotate_image, rotate_points


class OcrProcess(BaseProcess):
    offset = (0, 0)  #(r,c)
    width = 905
    height = 683
    row_nbr, col_nbr = 5, 5

    def __init__(self, model=None, messager=None, app=None):
        super(OcrProcess, self).__init__(model=model, messager=messager)
        self.use_patch = True
        self.angle = 90
        self.patcher = SNPatch()
        self.rois = self.patcher.rois
        self.app = app
        
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
            
            self.sendMessage("开始检测零件号 "+image+" ...")
            image = cv2.imread(image, cv2.IMREAD_COLOR)
            if image is None: 
                self.sendMessage("未读取到图片 "+image, flag="warning")
                return image, []  # Error loading the image
            
        elif mode == "live":
            self.sendMessage("交接单检测中 ...")
            
        if self.use_patch:
            if self.angle not in [0, 90, -90, 180, -180]:
                raise ValueError("Rotate angle only support 0, 90, -90, 180.")
            
            results = []
            offy, offx = self.offset
            img_patches = self.patcher(image)
            
            for i, img in enumerate(img_patches):
                cur_result = []
                img = rotate_image(img, self.angle)
                img_shape = img.shape[:2]
                loc_result = self.model.ocr(img, **params)

                for label in loc_result:
                    points = rotate_points(label[0], img_shape, -1*self.angle)
                    text = label[1][0].upper()
                    confidence = label[1][1]

                    r0, c0, r1, c1 = self.rois[i][0]
                    for point in points:
                        point[0] += c0
                        point[1] += r0
                    cur_result.append([points, [text, confidence], self.rois[i][1], True])
                
                results += self.merge_results(cur_result)
                # results += cur_result

                if self.app is not None: 
                    ratio = (i+1) / len(img_patches)
                    self.sendMessage("零件号检测进度: "+str(ratio*100)+"%")
                    self.app.processEvents()
        else:
            results = self.model.ocr(image, **params)
            
        self.sendMessage("零件号检测完成。")
        return image, results
            
    def postprocess(self, image, results):
        image = self.extractDraw(image, results)
        return image, results
        
    def extractDraw(self, image, results):
        self.part_list = []
        if not self.use_patch:
            return draw_results(image, results, size=2.0, color=(0,255,0), thickness=7)
        
        for result in results:
            self.part_list.append([result[1][0], str(result[2])])
            points = np.array(result[0],dtype=np.float32)
            texts = result[1][0]
            
            if result[-1]: color = (0,255,0)
            else: color = (255,0,0) 
            image = draw_polylines(image, [points], [texts], size=2.0, color=color, thickness=7)
            
        return image
        
    def merge_results(self, results, conf_thresh=0.8, dir="hor"):
        if len(results) < 2: return results
        
        confidences = []
        for result in results:
            confidences.append(result[1][1])
            
        xs, ys = [], []
        for result in results:
            for pt in result[0]:
                xs.append(pt[0])
                ys.append(pt[1])

        xmin = min(xs)
        ymin = min(ys)
        xmax = max(xs)
        ymax = max(ys)
        roi = [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]
    
        if len(results) != 2 or min(confidences) < conf_thresh:
            return [[roi, ["---", 0.0], results[0][2], False]]
        
        if dir == "hor":
            if results[0][0][0] < results[1][0][0]:
                text = results[0][1][0] + results[1][1][0]
            else:
                text = results[1][1][0] + results[0][1][0]
                
        elif dir == "ver":
            if results[0][0][1] < results[1][0][1]:
                text = results[0][1][0] + results[1][1][0]
            else:
                text = results[1][1][0] + results[0][1][0]
        
        conf = (results[0][1][1] + results[1][1][1]) / 2
        merge_result = [[roi, [text, conf], results[0][2], True]]
        
        return merge_result
        