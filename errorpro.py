"""
ErrorPro V6.
PySide6 GUI main function.
"""

import sys
from PySide6 import QtWidgets

import gui_main_window


def main():
    """@brief start GUI"""
    app = QtWidgets.QApplication(sys.argv)
    main_window = gui_main_window.MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
