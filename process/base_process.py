#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.27.2021
Updated on 01.27.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
from abc import ABC, abstractmethod


class BaseProcess(ABC):

    def __init__(self, model=None, messager=None):
        self.model = model
        self.messager = messager
    
    @abstractmethod    
    def preprocess(self, image):
        return image
        
    @abstractmethod
    def infer(self, image, params, mode):
        results = self.model.ocr(image, **params)
        return image, results
        
    @abstractmethod    
    def postprocess(self, image, results):
        return image, results
        
    def sendMessage(self, msg, flag="info", display=True):
        if self.messager is None: return
        self.messager(msg, flag, display)