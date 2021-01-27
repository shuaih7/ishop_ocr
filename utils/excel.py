#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.14.2021
Created on 01.14.2021

Author: haoshaui@handaotech.com
'''

import os
import xlwt
import time


#设置表格样式
def set_style(name, height, bold=False):
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = name
    
    if bold: font.bold = bold
    font.color_index = 4
    font.height = height
    al = xlwt.Alignment()
    al.horz = 0x02      # 设置水平居中
    al.vert = 0x01      # 设置垂直居中
    style.alignment = al
    style.font = font
    
    borders = xlwt.Borders()
    borders.left = 1
    borders.right = 1
    borders.top = 1
    borders.bottom = 1
    style.borders = borders
    
    return style
    
    
def write_title(sheet, base_space=2, sr=0, sc=0):
    # Create the title
    sheet.write_merge(sr,sr,sc,sc+9,"铸件交接单", set_style('Calibri',560,True))
    
    style=set_style('Calibri',360,True)
    
    # Create the first row
    sr += 1
    sheet.write(sr,sc,"确认人:",style)
    sheet.write_merge(sr,sr,sc+1,sc+base_space,' ',style)#合并行单元格
    sheet.write(sr,sc+base_space+1,"日期:",style)
    sheet.write_merge(sr,sr,sc+base_space+2,sc+2*base_space+1,' ',style)#合并行单元格
    sheet.write(sr,sc+2*base_space+2,"审核:",style)
    sheet.write_merge(sr,sr,sc+2*base_space+3,sc+2*base_space+5,' ',style)#合并行单元格
    
    # Create the second row
    sr += 1
    sheet.write(sr,sc,"零件号:",style)
    sheet.write_merge(sr,sr,sc+1,sc+base_space,' ',style)#合并行单元格
    sheet.write(sr,sc+base_space+1,"批次号:",style)
    sheet.write_merge(sr,sr,sc+base_space+2,sc+2*base_space+1,' ',style)#合并行单元格
    sheet.write_merge(sr,sr,sc+2*base_space+2,sc+2*base_space+5,' ',style)#合并行单元格
    
    # Create the third row
    sr += 1
    sheet.write(sr,sc,"序号",style)
    sheet.write_merge(sr,sr,sc+1,sc+2*base_space+5,'铸件号',style)
    
    sheet.row(0).set_style(xlwt.easyxf('font:height 594;'))
    for i in range(1,4):
        sheet.row(i).set_style(xlwt.easyxf('font:height 382;'))
    rows, align = 4, 2*base_space+5
   
    return sheet, rows, align
    

def write_content(sheet, index=0, number=' ', sr=3, sc=0, align=10):
    sheet.write(sr,sc,str(index),set_style('Calibri',360))
    sheet.write_merge(sr,sr,sc+1,align,number,set_style('Calibri',360,False))
    sheet.row(sr).set_style(xlwt.easyxf('font:height 382;'))

    return sheet

def write_excel(match_list, save_dir):
    f = xlwt.Workbook()
    
    base_space = 2
    sr, sc = 0, 0
    sheet = f.add_sheet('铸件交接单', cell_overwrite_ok=True)
    sheet, rows, align = write_title(sheet, base_space, sr, sc)
    
    for i, number in enumerate(match_list):
        sheet = write_content(sheet, i, number, rows+i, sc, align)
    
    timestr = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) 
    save_name = os.path.join(save_dir, timestr + ".xls")
    f.save(save_name)


if __name__ == '__main__':
    write_excel()