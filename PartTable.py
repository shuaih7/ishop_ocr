#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.14.2021
Updated on 01.14.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView


class PartTable(QTableWidget):
    def __init__(self, parent=None):
        super(PartTable, self).__init__(parent)
        self.config_matrix = None
        
    def setConfig(self, config_matrix, messager):
        self.config_matrix = config_matrix
        self.messager = messager
        
        self.match_color = QColor(6, 168, 255)
        self.check_color = QColor(6, 255, 168)
        self.scrap_color = QColor(255, 60, 6)
        self.background_color = QColor(222, 222, 222)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
    def updateRows(self, info_dict):
        self.clearRows()
        self.info_dict = info_dict
        
        for row, number in enumerate(info_dict):
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem(number))
            self.setItem(row, 1, QTableWidgetItem(info_dict[number]["position"]))
            self.setItem(row, 2, QTableWidgetItem(info_dict[number]["status"]))
            
            self.item(row, 0).setToolTip(number)
            self.item(row, 0).setTextAlignment(Qt.AlignCenter)
            self.item(row, 1).setTextAlignment(Qt.AlignCenter)
            self.item(row, 2).setTextAlignment(Qt.AlignCenter)
            
    def matchRows(self, info_list, info_dict):
        for result in info_list:
            number, position = result
            
            if number in info_dict:
                row = info_dict[number]["id"]
                self.item(row, 0).setBackground(QBrush(self.match_color))
                self.item(row, 1).setBackground(QBrush(self.match_color))
                self.item(row, 1).setText(str(position))
            
    def updateStatus(self, item):
        if item.column() != 2: return
        
        row = item.row()
        number = self.item(row,0).text()
        if self.item(row, 1).text() == "-": return
        
        if item.text() == "未确认": 
            status = "完好"
            item.setText(status)
            item.setBackground(QBrush(self.check_color))
        elif item.text() == "完好":
            status = "报废"
            item.setText(status)
            item.setBackground(QBrush(self.scrap_color))
        elif item.text() == "报废":
            status = "未确认"
            item.setText(status)
            item.setBackground(QBrush(self.background_color))
        self.info_dict[number] = status
        
    def getCheckList(self):
        check_list = []
        for i in range(self.rowCount()):
            if self.item(i,1).text() != "-" and self.item(i,2).text() != "报废":
                check_list.append(self.item(i,0).text())
        
        return check_list
            
    def clearRows(self):
        for i in range(self.rowCount(),-1,-1):
            self.removeRow(i)
