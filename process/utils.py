#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.27.2021
Created on 01.27.2021

Author: haoshaui@handaotech.com
'''

import os
import cv2
import sys
import numpy as np


def draw_results(image, results, isClosed=True, size=0.6, color=(0,255,0), thickness=3):
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    for result in results:
        line = np.array(result[0], dtype=np.int32)
        pt = (int(line[0][0]), int(line[0][1]))
        line = line.reshape((-1,1,2))
        image = cv2.polylines(image, [line], isClosed=isClosed, color=color, thickness=thickness)
        image = cv2.putText(image, result[1][0], pt, fontFace=font, 
            fontScale=size, color=color, thickness=max(1,thickness-1))
    return image 