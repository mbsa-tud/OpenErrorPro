"""
ErrorPro V6.
PySide GUI pix item class.
"""

import math

from PySide import QtGui
from PySide import QtCore

class PixItem(QtGui.QGraphicsPixmapItem):
    """@brief Pix item class for interection with model components"""

    def __init__(self, pixmap, main_window):
        """@brief constructor"""
        super(PixItem, self).__init__(pixmap)
        self.main_window = main_window
        self.model_view = main_window.model_view
        self.from_node = None
        self.to_node = None

    def __over_element(self, pos):
        """@brief checks is mouse over an element"""
        for el_name in  self.main_window.model_view.model_layout['elements'].keys():
            if pos.x() >= self.main_window.model_view.model_layout['elements'][el_name][0] and \
                pos.x() <= self.main_window.model_view.model_layout['elements'][el_name][2] and \
                pos.y() >= self.main_window.model_view.model_layout['elements'][el_name][1] and \
                pos.y() <= self.main_window.model_view.model_layout['elements'][el_name][3]:
                return el_name
        return None

    def __over_data(self, pos):
        """@brief checks is mouse over a data"""
        for d_name in  self.main_window.model_view.model_layout['data'].keys():
            if pos.x() >= self.main_window.model_view.model_layout['data'][d_name][0] and \
                pos.x() <= self.main_window.model_view.model_layout['data'][d_name][2] and \
                pos.y() >= self.main_window.model_view.model_layout['data'][d_name][1] and \
                pos.y() <= self.main_window.model_view.model_layout['data'][d_name][3]:
                return d_name
        return None

    def __over_failure(self, pos):
        """@brief checks is mouse over a failure"""
        for f_name in  self.main_window.model_view.model_layout['failures'].keys():
            if pos.x() >= self.main_window.model_view.model_layout['failures'][f_name][0] and \
                pos.x() <= self.main_window.model_view.model_layout['failures'][f_name][2] and \
                pos.y() >= self.main_window.model_view.model_layout['failures'][f_name][1] and \
                pos.y() <= self.main_window.model_view.model_layout['failures'][f_name][3]:
                return f_name
        return None

    def contextMenuEvent(self, event):
        """@brief context menu event"""
        el_name = self.__over_element(event.pos())
        if el_name:
            self.model_view.selected_node = ['element', el_name]
            menu = QtGui.QMenu(self.model_view)
            element = self.main_window.model.elements[el_name]
            if ((len(element['cf_outputs']) > 1) or \
                (element['cf_prism_commands'])) or \
                ((not element['sub_model'] and element['df_outputs']) or \
                (element['ep_prism_commands'])):
                menu.addAction(self.model_view.actions["element_properties"])
            if self.main_window.model.initial_element != el_name:
                menu.addAction(self.model_view.actions["make_initial"])
            menu.addAction(self.model_view.actions["update_time"])
            menu.addAction(self.model_view.actions["update_repetitions"])
            if not element['sub_model']:
                menu.addAction(self.model_view.actions["create_sub_model"])
            remove_menu = QtGui.QMenu("&Remove")
            remove_menu.addAction(self.model_view.actions["remove_element"])
            if element['cf_outputs']:
                remove_menu.addAction(self.model_view.actions["remove_control_flow"])
            if element['df_outputs']:
                remove_menu.addAction(self.model_view.actions["remove_data_flow"])
            if element['sub_model']:
                remove_menu.addAction(self.model_view.actions["remove_sub_model"])
            menu.addMenu(remove_menu)
            menu.exec_(QtGui.QCursor.pos())
            event.accept()
            return
        d_name = self.__over_data(event.pos())
        if d_name:
            self.model_view.selected_node = ['data', d_name]
            menu = QtGui.QMenu(self.model_view)
            menu.addAction(self.model_view.actions["update_values"])
            remove_menu = QtGui.QMenu("&Remove")
            remove_menu.addAction(self.model_view.actions["remove_data"])
            if self.main_window.model.data[d_name]['df_outputs']:
                remove_menu.addAction(self.model_view.actions["remove_data_flow"])
            menu.addMenu(remove_menu)
            menu.exec_(QtGui.QCursor.pos())
            event.accept()
            return
        f_name = self.__over_failure(event.pos())
        if f_name:
            self.model_view.selected_node = ['failure', f_name]
            menu = QtGui.QMenu(self.model_view)
            compute_menu = QtGui.QMenu("&Compute")
            compute_menu.addAction(self.model_view.actions["compute_P_single"])
            compute_menu.addAction(self.model_view.actions["compute_MTTF"])
            compute_menu.addSeparator()
            compute_menu.addAction(self.model_view.actions["compute_P"])
            compute_menu.addAction(self.model_view.actions["compute_downtime"])
            compute_menu.addAction(self.model_view.actions["compute_N_failures"])
            menu.addMenu(compute_menu)
            menu.addAction(self.model_view.actions["update_failure"])
            menu.addAction(self.model_view.actions["remove_failure"])
            menu.exec_(QtGui.QCursor.pos())
            event.accept()
            return
        event.ignore()

    def mouseDoubleClickEvent(self, event):
        """@brief mouse double click event"""
        el_name = self.__over_element(event.pos())
        if el_name:
            if self.main_window.model.elements[el_name]['sub_model']:
                self.model_view.view_stack.append(el_name)
                self.main_window.model = self.main_window.model.elements[el_name]['sub_model']
                self.model_view.draw_model()
        else:
            self.model_view.draw_model()

    def mousePressEvent(self, event):
        """@brief mouse press event"""
        self.main_window.command_le.setPalette(self.main_window.palette)
        el_name = self.__over_element(event.pos())
        if not el_name:
            d_name = self.__over_data(event.pos())
            if not d_name:
                f_name = self.__over_failure(event.pos())
                if not f_name:
                    return
        if el_name:
            self.main_window.command_le.setText("model.elements['" + el_name + "']")
            pos = self.main_window.model_view.model_layout['elements'][el_name]
            self.from_node = ['element', el_name, pos]
        elif d_name:
            self.main_window.command_le.setText("model.data['" + d_name + "']")
            pos = self.main_window.model_view.model_layout['data'][d_name]
            self.from_node = ['data', d_name, pos]
        elif f_name:
            self.main_window.command_le.setText("model.failure['" + f_name + "']")
            #pos = self.main_window.model_view.model_layout['data'][d_name]
            #self.from_node = ['data', d_name, pos]

    @staticmethod
    def __draw_arrow(painter, pen, point_x1, point_y1, point_x2, point_y2):
        """@brief drawing arrow heads, thanks to https://stackoverflow.com/a/3011123/9320993"""
        painter.setPen(pen)
        painter.drawLine(point_x2, point_y2, point_x1, point_y1)
        length = 7
        delta_x = point_x2 - point_x1
        delta_y = point_y2 - point_y1
        theta = math.atan2(delta_y, delta_x)
        rad = math.radians(35)
        xh1 = point_x2 - length * math.cos(theta + rad)
        yh1 = point_y2 - length * math.sin(theta + rad)
        phi2 = math.radians(-35)
        xh2 = point_x2 - length * math.cos(theta + phi2)
        yh2 = point_y2 - length * math.sin(theta + phi2)
        painter.drawLine(point_x2, point_y2, xh1, yh1)
        painter.drawLine(point_x2, point_y2, xh2, yh2)

    def mouseMoveEvent(self, event):
        """@brief mouse move event"""
        if self.from_node:
            el_name = self.__over_element(event.pos())
            if el_name:
                pos = self.main_window.model_view.model_layout['elements'][el_name]
                self.to_node = ['element', el_name, pos]
            else:
                d_name = self.__over_data(event.pos())
                if d_name and self.from_node[0] == 'element':
                    pos = self.main_window.model_view.model_layout['data'][d_name]
                    self.to_node = ['data', d_name, pos]
                else:
                    self.to_node = None
            painter = QtGui.QPainter()
            pixmap = self.main_window.model_view.pixmap.copy()
            painter.begin(pixmap)
            pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
            if self.to_node:
                if self.from_node[0] == 'data' or self.to_node[0] == 'data':
                    pen = QtGui.QPen(QtCore.Qt.blue, 2, QtCore.Qt.SolidLine)
                self.__draw_arrow(painter, pen, \
                    self.from_node[2][0] + self.from_node[2][4]/2, \
                    self.from_node[2][1] + self.from_node[2][5]/2, \
                    self.to_node[2][0] + self.to_node[2][4]/2, \
                    self.to_node[2][1] + self.to_node[2][5]/2)
            else:
                if self.from_node[0] == 'data':
                    pen = QtGui.QPen(QtCore.Qt.blue, 2, QtCore.Qt.SolidLine)
                self.__draw_arrow(painter, pen, \
                    self.from_node[2][0] + self.from_node[2][4]/2, \
                    self.from_node[2][1] + self.from_node[2][5]/2, \
                    event.pos().x(), event.pos().y())
            painter.end()
            self.setPixmap(pixmap)

    def mouseReleaseEvent(self, event):
        """@brief mouse release event"""
        pixmap = self.main_window.model_view.pixmap.copy()
        self.setPixmap(pixmap)
        if self.from_node and self.to_node:
            if (self.from_node[0] == 'data') or (self.to_node[0] == 'data'):
                cmd = 'model.add_data_flow("' + \
                    self.from_node[1] + '","' + self.to_node[1] + '")'
            else:
                cmd = 'model.add_control_flow("' + \
                    self.from_node[1] + '","' + self.to_node[1] + '")'
            self.main_window.command_le.setPalette(self.main_window.palette_highlight)
            self.main_window.command_le.setText(cmd)
            self.main_window.command_le.setFocus()
        self.from_node = None
        self.to_node = None
