"""
ErrorPro V6.
PySide GUI main window class.
"""

import collections
import traceback

from PySide import QtGui
from PySide import QtCore

import epl_model
import epl_logger
import epl_prism
import epl_checker
import epl_xml

import gui_model_view

class MainWindow(QtGui.QMainWindow):
    """@brief Main window class"""

    def __init__(self):
        """@brief constructor"""
        # initialization of QtGui.QMainWindow
        super(MainWindow, self).__init__()

        # Layout:
        # ----------------------------------
        # |        QWidget: widget         |
        # | ------------------------------ |
        # | |                            | |
        # | |   ModelView: model_view    | |
        # | |                            | |
        # | |                            | |
        # | ---------------v-------------- |
        # | |   QTextEdit: history_te    | |
        # | |                            | |
        # | ------------------------------ |
        # | |   QLineEdit: command_le    | |
        # | ------------------------------ |
        # ----------------------------------

        # Widgets:
        # history_te - command history, logger output
        self.history_te = QtGui.QTextEdit()
        self.history_te.setReadOnly(True)
        self.palette = QtGui.QPalette() # for hisotory_te and command_le
        self.palette.setColor(QtGui.QPalette.Base, QtGui.QColor(50, 50, 50))
        self.palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
        self.palette_highlight = QtGui.QPalette() # for command_le to show that input is required
        self.palette_highlight.setColor(QtGui.QPalette.Base, QtGui.QColor(0, 0, 0))
        self.palette_highlight.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
        self.history_te.setPalette(self.palette)
        # command_le - command line
        self.command_le = QtGui.QLineEdit()
        self.command_le.setPalette(self.palette)
        self.command_le.setText("model.")
        # for press enter and press up down events
        self.command_le.returnPressed.connect(self.execute_command)
        self.command_le.installEventFilter(self)

        # Model-related variables:
        # epl logger
        self.logger = epl_logger.Logger(out_widget=self.history_te)
        # current model
        self.model = epl_model.Model(self.logger)
        # XML related functions
        self.xml = epl_xml.XML()
        # PRISM related functions
        self.prism = epl_prism.PRISM()
        # checking functions
        self.checker = epl_checker.Checker()
        # top-level model
        self.top_model = self.model
        # command history
        self.command_history = collections.deque(maxlen=100)
        # current command history id to iterate over the history
        self.command_history_id = 0

        # Model view:
        self.model_view = gui_model_view.ModelView(self)
        #self.model_view QtGui.QGraphicsView()

        # Layout
        self.setWindowTitle("OpenErrorPro")
        widget = QtGui.QWidget()
        self.setCentralWidget(widget)
        splitter = QtGui.QSplitter()
        splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.addWidget(self.model_view)
        splitter.addWidget(self.history_te)
        splitter.setSizes([500, 100])
        layout = QtGui.QVBoxLayout()
        layout.addWidget(splitter)
        layout.addWidget(self.command_le)
        widget.setLayout(layout)
        self.setWindowIcon(QtGui.QIcon('errorpro.ico'))

    def eventFilter(self, widget, event):
        """@brief command line navigation over command history"""
        if (event.type() == QtCore.QEvent.KeyPress and \
            widget is self.command_le):
            key = event.key()
            if key == QtCore.Qt.Key_Down and \
                self.command_history_id < len(self.command_history) - 1:
                self.command_history_id += 1
                cmd = self.command_history[self.command_history_id]
                self.command_le.setText(cmd)
                self.command_le.setCursorPosition(len(cmd))
                return True
            else:
                if key == QtCore.Qt.Key_Up and \
                    self.command_history_id > 0:
                    self.command_history_id -= 1
                    cmd = self.command_history[self.command_history_id]
                    self.command_le.setText(cmd)
                    self.command_le.setCursorPosition(len(cmd))
                    return True
        return QtGui.QWidget.eventFilter(self, widget, event)

    def execute_command(self):
        """@brief command line press enter"""
        self.command_history.append(self.command_le.text())
        self.history_te.append("> " + self.command_le.text())
        try:
            res = eval(self.command_le.text(), \
                {'model': self.model, \
                 'top_model': self.top_model, \
                 'view_stack': self.model_view.view_stack, \
                 'prism': self.prism, \
                 'xml': self.xml, \
                 'self': self, \
                 'model_layout': self.model_view.model_layout, \
                 'checker': self.checker, \
                 'logger': self.logger, \
                 'drawing': self.model_view.drawing})
            self.history_te.append(str(res))
        except BaseException as exception:
            self.history_te.append(traceback.format_exc())
        self.command_history_id = len(self.command_history)
        self.command_le.clear()
        self.model_view.draw_model()
        self.command_le.setPalette(self.palette)
