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


def draw_polylines(image, polylines, texts=None, isClosed=True, size=0.6, color=(0,255,0), thickness=3):
    font = cv2.FONT_HERSHEY_SIMPLEX
    polylines = np.array(polylines, dtype=np.int32)#.reshape((-1,1,2))
    
    for i, line in enumerate(polylines):
        pt = (int(line[0][0]), int(line[0][1]))
        line = line.reshape((-1,1,2))
        image = cv2.polylines(image, [line], isClosed=isClosed, color=color, thickness=thickness)
        if texts is not None:
            image = cv2.putText(image, texts[i], pt, fontFace=font, 
                fontScale=size, color=color, thickness=max(1,thickness-1))
    return image 


def draw_results(image, 
                 results, 
                 isClosed=True, 
                 size=0.6, 
                 color=(0,255,0), 
                 thickness=3):
    if image is None: return image
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    for result in results:
        line = np.array(result[0], dtype=np.int32)
        pt = (int(line[0][0]), int(line[0][1]))
        line = line.reshape((-1,1,2))
        image = cv2.polylines(image, [line], isClosed=isClosed, color=color, thickness=thickness)
        image = cv2.putText(image, result[1][0], pt, fontFace=font, 
            fontScale=size, color=color, thickness=max(1,thickness-1))
    return image 
    
    
def rotate_image(image, angle):
    """
    :param image: 原图像
    :param angle: 旋转角度
    :return: 旋转后的图像
    """
    if angle not in [0, 90, -90, 180, -180]:
        raise ValueError("Angle value only support 0, 90, -90, 180, and -180.")
    
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    img = cv2.warpAffine(image, M, (nW, nH))
    # perform the actual rotation and return the image
    return img
    
    
def rotate_points(points, shape, angle):
    """ Assume that the points are clock-wisely arranged
    
    """
    if angle not in [0, 90, -90, 180, -180]:
        raise ValueError("Angle value only support 0, 90, -90, 180, and -180.")
    if angle == 0: return points
     
    img_h, img_w = shape
    points_rotated, temp_pts = [], []
    
    if angle == 180 or angle == -180:
        for pt in points:
            rot_pt = [img_w-pt[0], img_h-pt[1]]
            temp_pts.append(rot_pt)
        points_rotated = [temp_pts[2], temp_pts[3], temp_pts[0], temp_pts[1]]
    elif angle == 90:
        for pt in points:
            rot_pt = [img_h-pt[1], pt[0]]
            temp_pts.append(rot_pt)
        points_rotated = [temp_pts[3], temp_pts[0], temp_pts[1], temp_pts[2]]
    elif angle == -90:
        for pt in points:
            rot_pt = [pt[1], img_w-pt[0]]
            temp_pts.append(rot_pt)
        points_rotated = [temp_pts[1], temp_pts[2], temp_pts[3], temp_pts[0]]
    
    return points_rotated