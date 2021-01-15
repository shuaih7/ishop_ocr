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
    return style
    
    
def write_title(sheet, base_space=2, sr=0, sc=0):
    # Create the first row
    sheet.write(sr,sc,"确认人:",set_style('Times New Roman',220,True))
    sheet.write_merge(sr,sr,sc+1,sc+base_space,' ')#合并行单元格
    sheet.write(sr,sc+base_space+1,"日期:",set_style('Times New Roman',220,True))
    sheet.write_merge(sr,sr,sc+base_space+2,sc+2*base_space+1,' ')#合并行单元格
    sheet.write(sr,sc+2*base_space+2,"审核:",set_style('Times New Roman',220,True))
    sheet.write_merge(sr,sr,sc+2*base_space+3,sc+2*base_space+5,' ')#合并行单元格
    
    # Create the second row
    sr += 1
    sheet.write(sr,sc,"零件号",set_style('Times New Roman',220,True))
    sheet.write_merge(sr,sr,sc+1,sc+base_space,' ')#合并行单元格
    sheet.write(sr,sc+base_space+1,"批次号",set_style('Times New Roman',220,True))
    sheet.write_merge(sr,sr,sc+base_space+2,sc+2*base_space+1,' ')#合并行单元格
    sheet.write_merge(sr,sr,sc+2*base_space+2,sc+2*base_space+5,' ')#合并行单元格
    
    # Create the third row
    sr += 1
    sheet.write(sr,sc,"序号",set_style('Times New Roman',220,True))
    sheet.write_merge(sr,sr,sc+1,sc+2*base_space+5,'铸件号',set_style('Times New Roman',220,True))
    
    for i in range(3):
        sheet.row(i).set_style(xlwt.easyxf('font:height 540;'))
    rows, align = 3, 2*base_space+5
   
    return sheet, rows, align
    

def write_content(sheet, index=0, number=' ', sr=3, sc=0, align=10):
    sheet.write(sr,sc,str(index),set_style('Times New Roman',220))
    sheet.write_merge(sr,sr,sc+1,align,number,set_style('Times New Roman',220,False))
    sheet.row(sr).set_style(xlwt.easyxf('font:height 540;'))

    return sheet

def write_excel():
    f = xlwt.Workbook()
    
    base_space = 2
    sr, sc = 0, 0
    sheet = f.add_sheet('铸件交接单', cell_overwrite_ok=True)
    sheet, rows, align = write_title(sheet, base_space, sr, sc)
    sheet = write_content(sheet, 0, r"26199AS/N", rows, sc, align)
    sheet = write_content(sheet, 1, r"26199AS/N", rows+1, sc, align)
    
    f.save('practice.xls')


if __name__ == '__main__':
    eval("print")("Yeah!")