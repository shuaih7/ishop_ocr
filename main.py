#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.13.2021
Updated on 01.13.2021

Author: haoshaui@handaotech.com
'''

import sys
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)

from HMI import MainWindow


def main():
    Window = MainWindow()
    #Window.show()
    Window.showMaximized()
    Window.liveStream()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
