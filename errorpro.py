"""
ErrorPro V6.
PySide GUI main function.
"""

import sys
from PySide import QtGui

import gui_main_window

def main():
    """@brief start GUI"""
    app = QtGui.QApplication(sys.argv)
    main_window = gui_main_window.MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
