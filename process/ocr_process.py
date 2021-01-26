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

    def __init__(self, model=None, messager=None):
        super(OcrProcess, self).__init__(model=model, messager=messager)
        
    def infer(self, image, params, mode):
        pass
        
    def postprocess(self, image, results):
        pass