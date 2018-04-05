"""
ErrorPro V6.
PySide GUI model view class.
"""

import os

import pygraphviz as pgv

from PySide import QtGui
from PySide import QtCore

import epl_drawing

import gui_pix_item
import gui_dialogs

#TODO, sometimes, expecially just after the run of the GUI the focus do not trasnfers to the cmd line


class ModelView(QtGui.QGraphicsView):
    """@brief Model view class"""

    def __init__(self, main_window):
        """@brief constructor"""
        # initialization of QtGui.QGraphicsView
        super(ModelView, self).__init__(main_window)
        self.setMouseTracking(True)

        # Layout:
        # -----------------
        # |   ModelView  |
        # | ------------ |
        # | |  scene   | |
        # | | -------- | |
        # | | |pixmap| | |
        # | | -------- | |
        # | ------------ |
        # ----------------

        # main window
        self.main_window = main_window
        # epl drawing
        self.drawing = epl_drawing.Drawing()
        # model image filename
        self.model_filename = "model.png"
        #self.logo_filename = "ep_logo.png"
        if os.path.exists(self.model_filename):
            os.remove(self.model_filename)
        # view_stack is the "path" to the current model
        # view_stack should be cleared each time a new model is loaded
        self.view_stack = []
        # positions of the elements and data in the AGraph
        self.model_layout = {'elements':{}, 'data':{}, 'failures':{}}
        # selected node
        self.selected_node = None
        # current dir for the case PRISM crashed
        self.dir = os.getcwd()

        # Widgets
        # Graphic scene
        self.scene = QtGui.QGraphicsScene()
        self.setScene(self.scene)
        # Pixmap that is drawn in the self.scene
        self.pixmap = QtGui.QPixmap(self.model_filename)
        # Logo
        #self.logo_pixmap = QtGui.QPixmap(self.logo_filename)

        # Actions for main context menu
        self.actions = {}
        self.actions['load'] = QtGui.QAction("&Load", \
            self, triggered=self.load)
        self.actions['save'] = QtGui.QAction("&Save", \
            self, triggered=self.save)
        self.actions['add_element'] = QtGui.QAction("&Add element ...", \
            self, triggered=self.add_element)#, shortcut="Ctrl+E")
        self.actions['check'] = QtGui.QAction("&Check", \
            self, triggered=self.check)#, shortcut="Ctrl+C")
        self.actions['clear'] = QtGui.QAction("&Clear", \
            self, triggered=self.clear)#, shortcut="Ctrl+C")
        self.actions['add_data'] = QtGui.QAction("&Add data ...", \
            self, triggered=self.add_data)#, shortcut="Ctrl+D")
        self.actions['add_failure'] = QtGui.QAction("&Add failure ...", \
            self, triggered=self.add_failure)#, shortcut="Ctrl+F")
        self.actions['go_back'] = QtGui.QAction("&Go back", \
            self, triggered=self.go_back)
        self.actions['go_top'] = QtGui.QAction("&Go top", \
            self, triggered=self.go_top)
        self.actions['zoom_in'] = QtGui.QAction("&Zoom in", \
            self, triggered=self.zoom_in)#, shortcut="Ctrl++")
        self.actions['zoom_out'] = QtGui.QAction("&Zoom out", \
            self, triggered=self.zoom_out)#, shortcut="Ctrl+-")
        self.actions['switch_view'] = QtGui.QAction("&All/CF/DF", \
            self, triggered=self.switch_view)#, shortcut="Ctrl+-")
        #self.actions['prism_save'] = QtGui.QAction("&Save model", \
        #    self, triggered=self.prism_save)
        self.actions['prism_compute_sub_models_and_repetitions'] = \
            QtGui.QAction("&Sub-models and repetitions", \
            self, triggered=self.prism_compute_sub_models_and_repetitions)
        # Actions for specific node right click
        self.actions['remove_element'] = QtGui.QAction("&Element", \
            self, triggered=self.remove_element)
        self.actions['make_initial'] = QtGui.QAction("&Make initial", \
            self, triggered=self.make_initial)
        self.actions['update_time'] = QtGui.QAction("&Time", \
            self, triggered=self.update_time)
        self.actions['update_repetitions'] = QtGui.QAction("&Repetitions", \
            self, triggered=self.update_repetitions)
        self.actions['update_values'] = QtGui.QAction("&Values", \
            self, triggered=self.update_values)
        self.actions['create_sub_model'] = QtGui.QAction("&Create sub model", \
            self, triggered=self.create_sub_model)
        self.actions['remove_sub_model'] = QtGui.QAction("&Sub model", \
            self, triggered=self.remove_sub_model)
        self.actions['remove_data'] = QtGui.QAction("&Data", \
            self, triggered=self.remove_data)
        self.actions['remove_failure'] = QtGui.QAction("&Remove", \
            self, triggered=self.remove_failure)
        self.actions['update_failure'] = QtGui.QAction("&Update", \
            self, triggered=self.update_failure)
        self.actions['remove_control_flow'] = QtGui.QAction("&Control flow to ...", \
            self, triggered=self.remove_control_flow)
        self.actions['remove_data_flow'] = QtGui.QAction("&Data flow to ...", \
            self, triggered=self.remove_data_flow)
        self.actions['element_properties'] = QtGui.QAction("&Properties", \
            self, triggered=self.element_properties)
        self.actions['compute_MTTF'] = QtGui.QAction("&MTTF", \
            self, triggered=self.compute_MTTF)
        self.actions['compute_P'] = QtGui.QAction("&Probability (t)", \
            self, triggered=self.compute_P)
        self.actions['compute_P_single'] = QtGui.QAction("&Probability", \
            self, triggered=self.compute_P_single)
        self.actions['compute_N_failures'] = QtGui.QAction("&Number of failures (t)", \
            self, triggered=self.compute_N_failures)
        self.actions['compute_downtime'] = QtGui.QAction("&Downtime (t)", \
            self, triggered=self.compute_downtime)

    def draw_model(self):
        """@brief redraw model and get positions of the nodes"""
        self.scene.clear()
        self.model_layout = {'elements':{}, 'data':{}, 'failures':{}}
        # change dir for the case PRISM fails
        os.chdir(self.dir)
        graph = self.drawing.draw_model(self.main_window.model, self.model_filename)
        if not graph.nodes():
            return
        self.pixmap = QtGui.QPixmap(self.model_filename)
        painter = QtGui.QPainter()
        painter.begin(self.pixmap)
        red_pen = QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.SolidLine)
        yellow_pen = QtGui.QPen(QtCore.Qt.yellow, 2, QtCore.Qt.SolidLine)
        painter.setPen(red_pen)
        # bb = graph.graph_attr['bb'].split(",")
        # the line above give a random error in my mac (python3.4, pgv 1.3)
        # dicuseed here https://github.com/pygraphviz/pygraphviz/issues/113
        bounding_box = pgv.graphviz.agget(graph.handle, \
            'bb'.encode('utf-8')).decode("utf-8").split(",")
        dpi = float(pgv.graphviz.agget(graph.handle, 'dpi'.encode('utf-8')).decode("utf-8"))
        if not dpi:
            dpi = 72.0
        pgv_width = float(bounding_box[2]) - float(bounding_box[0])
        pgv_height = float(bounding_box[3]) - float(bounding_box[1])
        if (float(pgv_width) != 0) and (float(pgv_height) != 0):
            for node in graph.nodes():
                pos = node.attr['pos'].strip().split(",")
                pos[0] = float(pos[0])
                pos[1] = (pgv_height - float(pos[1]))
                width = float(graph.get_node(node).attr['width'].strip()) * dpi
                height = float(graph.get_node(node).attr['height'].strip()) * dpi
                if node in self.main_window.model.elements:
                    self.model_layout['elements'][node] = \
                        [pos[0] - width / 2, pos[1] - height / 2, \
                        pos[0] + width / 2, pos[1] + height / 2, \
                        width, height]
                    if node in self.main_window.checker.elements_status:
                        if self.main_window.checker.elements_status[node][0] == 'Error':
                            painter.setPen(red_pen)
                            painter.drawRect(pos[0] - width / 2, pos[1] - height / 2, width, height)
                        elif self.main_window.checker.elements_status[node][0] == 'Warning':
                            painter.setPen(yellow_pen)
                            painter.drawRect(pos[0] - width / 2, pos[1] - height / 2, width, height)
                if node in self.main_window.model.data:
                    self.model_layout['data'][node] = \
                        [pos[0] - width / 2, pos[1] - height / 2, \
                        pos[0] + width / 2, pos[1] + height / 2, \
                        width, height]
                    if node in self.main_window.checker.data_status:
                        if self.main_window.checker.data_status[node][0] == 'Error':
                            painter.setPen(red_pen)
                            painter.drawRect(pos[0] - width / 2, pos[1] - height / 2, width, height)
                        elif self.main_window.checker.data_status[node][0] == 'Warning':
                            painter.setPen(yellow_pen)
                            painter.drawRect(pos[0] - width / 2, pos[1] - height / 2, width, height)
                if node in self.main_window.model.failures:
                    self.model_layout['failures'][node] = \
                        [pos[0] - width / 2, pos[1] - height / 2, \
                        pos[0] + width / 2, pos[1] + height / 2, \
                        width, height]
                    if node in self.main_window.checker.failure_status:
                        if self.main_window.checker.failure_status[node][0] == 'Error':
                            painter.setPen(red_pen)
                            painter.drawRect(pos[0] - width / 2, pos[1] - height / 2, width, height)
                        elif self.main_window.checker.failure_status[node][0] == 'Warning':
                            painter.setPen(yellow_pen)
                            painter.drawRect(pos[0] - width / 2, pos[1] - height / 2, width, height)
        item = gui_pix_item.PixItem(self.pixmap, self.main_window)
        painter.end()
        self.scene.addItem(item)
        self.show()

    def contextMenuEvent(self, event):
        """@brief context menu slot function"""
        super(ModelView, self).contextMenuEvent(event)
        if not event.isAccepted():
            menu = QtGui.QMenu(self)
            model_menu = QtGui.QMenu("&Model")
            model_menu.addAction(self.actions['add_element'])
            model_menu.addAction(self.actions['add_data'])
            model_menu.addAction(self.actions['add_failure'])
            model_menu.addSeparator()
            model_menu.addAction(self.actions['load'])
            model_menu.addAction(self.actions['save'])
            model_menu.addSeparator()
            model_menu.addAction(self.actions['check'])
            model_menu.addSeparator()
            model_menu.addAction(self.actions['clear'])
            menu.addMenu(model_menu)
            view_menu = QtGui.QMenu("&View")
            if self.view_stack:
                if len(self.view_stack) > 1:
                    view_menu.addAction(self.actions['go_back'])
                view_menu.addAction(self.actions['go_top'])
                view_menu.addSeparator()
            view_menu.addAction(self.actions['zoom_in'])
            view_menu.addAction(self.actions['zoom_out'])
            view_menu.addAction(self.actions['switch_view'])
            menu.addMenu(view_menu)
            prism_menu = QtGui.QMenu("&Compute")
            prism_menu.addAction(self.actions['prism_compute_sub_models_and_repetitions'])
            #prism_menu.addAction(self.actions['prism_save'])
            menu.addMenu(prism_menu)
            menu.exec_(event.globalPos())
            event.accept()

    def load(self):
        """@brief load from xml action function"""
        dialog = QtGui.QFileDialog()
        dialog.setFilter("*.xml")
        dialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        fname = dialog.getOpenFileName()
        if fname[0]:
            self.go_top()
            self.main_window.command_le.setText(str("xml.load(model, '" + fname[0] + "')"))
            self.main_window.execute_command()
            self.view_stack.clear()

    def save(self):
        """@brief save to xml action function"""
        dialog = QtGui.QFileDialog()
        fname = dialog.getSaveFileName(self, "Save to XML", "*.xml")
        if fname[0]:
            self.go_top()
            self.main_window.command_le.setText(str("xml.save(model, '" + fname[0] + "')"))
            self.main_window.execute_command()

    def go_back(self):
        """@brief go back on the view stack"""
        if self.view_stack:
            self.view_stack.pop()
        model = self.main_window.top_model
        for host_element in self.view_stack:
            model = model.elements[host_element]['sub_model']
        self.main_window.model = model
        self.draw_model()

    def go_top(self):
        """@brief switch to the top level model"""
        self.view_stack.clear()
        self.main_window.model = self.main_window.top_model
        self.draw_model()

    def zoom_in(self):
        """@brief zoom in"""
        self.main_window.command_le.setText(str("drawing.zoom_in()"))
        self.main_window.execute_command()

    def zoom_out(self):
        """@brief zoom out"""
        self.main_window.command_le.setText(str("drawing.zoom_out()"))
        self.main_window.execute_command()

    def switch_view(self):
        """@brief switch view"""
        self.main_window.command_le.setText(str("drawing.switch_view()"))
        self.main_window.execute_command()

    def add_element(self):
        """@brief add new element"""
        cmd = 'model.add_element("")'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setCursorPosition(len(cmd)-2)
        self.main_window.command_le.setFocus()

    def add_data(self):
        """@brief add new data"""
        cmd = 'model.add_data("")'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setCursorPosition(len(cmd)-2)
        self.main_window.command_le.setFocus()

    def add_failure(self):
        """@brief add failure"""
        cmd = 'model.add_failure("Failure", "")'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setCursorPosition(len(cmd)-2)
        self.main_window.command_le.setFocus()

    def remove_element(self):
        """@brief remove element"""
        cmd = 'model.remove_element("' + self.selected_node[1] + '")'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setCursorPosition(len(cmd))
        self.main_window.command_le.setFocus()
        self.selected_node = None

    def create_sub_model(self):
        """@brief create empty sub model"""
        cmd = 'model.create_sub_model("' + self.selected_node[1] + '")'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setFocus()
        self.selected_node = None
        self.main_window.execute_command()

    def remove_sub_model(self):
        """@brief remove sub model"""
        cmd = 'model.remove_sub_model("' + self.selected_node[1] + '")'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setCursorPosition(len(cmd))
        self.main_window.command_le.setFocus()
        self.selected_node = None

    def make_initial(self):
        """@brief make the element initial"""
        cmd = 'model.set_initial_element("' + self.selected_node[1] + '")'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setFocus()
        self.selected_node = None
        self.main_window.execute_command()

    def update_time(self):
        """@brief update element execution time"""
        time = self.main_window.model.elements[self.selected_node[1]]['time']
        cmd = 'model.update_element_time("' + self.selected_node[1] + '", ' + str(time) + ')'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setCursorPosition(len(cmd)-1)
        self.main_window.command_le.setFocus()
        self.selected_node = None

    def update_repetitions(self):
        """@brief update element repetitions number"""
        repetitions = self.main_window.model.elements[self.selected_node[1]]['repetitions']
        cmd = 'model.update_element_repetitions("' + self.selected_node[1] + '", ' + str(repetitions) + ')'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setCursorPosition(len(cmd)-1)
        self.main_window.command_le.setFocus()
        self.selected_node = None

    def update_values(self):
        """@brief update values of a data"""
        values = self.main_window.model.data[self.selected_node[1]]['values']
        initial_value = self.main_window.model.data[self.selected_node[1]]['initial_value']
        cmd = 'model.update_data_values("' + self.selected_node[1] + \
            '", values=' + str(values)
        if isinstance(initial_value, str):
            cmd += ', initial_value=\'' + initial_value + '\')'
        else: #must be int
            cmd += ', initial_value=' + str(initial_value) + ')'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setCursorPosition(len(cmd))
        self.main_window.command_le.setFocus()
        self.selected_node = None

    def remove_data(self):
        """@brief remove data"""
        cmd = 'model.remove_data("' + self.selected_node[1] + '")'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setCursorPosition(len(cmd))
        self.main_window.command_le.setFocus()
        self.selected_node = None

    def check(self):
        """@brief execute the checker"""
        cmd = 'checker.check(model)'
        if self.view_stack:
            host_model = "top_model"
            for el_name in self.view_stack[:-1]:
                host_model += ".elements['" + el_name + "']['sub_model']"
            host_element_name = self.view_stack[-1]
            cmd = 'checker.check(model, host_model=' + host_model + \
                ', host_element_name=\'' + host_element_name + '\')'
        self.main_window.command_le.setText(cmd)
        self.main_window.execute_command()

    def clear(self):
        """@brief clear the model"""
        self.go_top()
        cmd = 'model.clear()'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setCursorPosition(len(cmd))
        self.main_window.command_le.setFocus()

    def remove_failure(self):
        """@brief remove failure"""
        cmd = 'model.remove_failure("' + self.selected_node[1] + '")'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setCursorPosition(len(cmd))
        self.main_window.command_le.setFocus()
        self.selected_node = None

    def update_failure(self):
        """@brief update failure"""
        failure = self.main_window.model.failures[self.selected_node[1]]
        cmd = 'model.update_failure("' + self.selected_node[1] + '", "' + failure + '")'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        self.main_window.command_le.setCursorPosition(len(cmd)-2)
        self.main_window.command_le.setFocus()
        self.selected_node = None

    def remove_control_flow(self):
        """@brief remove a control flow arc"""
        element = self.main_window.model.elements[self.selected_node[1]]
        if not element['cf_outputs']:
            return
        elif len(element['cf_outputs']) == 1:
            cmd = 'model.remove_control_flow("' + self.selected_node[1] + \
                '", "' + element['cf_outputs'][0] + '")'
            self.main_window.command_le.setText(cmd)
        else:
            cmd = 'model.remove_control_flow("' + self.selected_node[1] + '", "")'
            self.main_window.command_le.setText(cmd)
            self.main_window.command_le.setCursorPosition(len(cmd)-2)
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setFocus()
        self.selected_node = None

    def remove_data_flow(self):
        """@brief remove a data flow arc"""
        df_to = ""
        if self.selected_node[0] == 'element':
            element = self.main_window.model.elements[self.selected_node[1]]
            if not element['df_outputs']:
                return
            elif len(element['df_outputs']) == 1:
                df_to = element['df_outputs'][0]
        elif self.selected_node[0] == 'data':
            data = self.main_window.model.data[self.selected_node[1]]
            if not data['df_outputs']:
                return
            elif len(data['df_outputs']) == 1:
                df_to = data['df_outputs'][0]
        cmd = 'model.remove_data_flow("' + self.selected_node[1] + '", "' + df_to + '")'
        self.main_window.command_le.setPalette(self.main_window.palette_highlight)
        self.main_window.command_le.setText(cmd)
        if not df_to:
            self.main_window.command_le.setCursorPosition(len(cmd)-2)
        self.main_window.command_le.setFocus()
        self.selected_node = None

    def element_properties(self):
        """@brief open element properties dialog"""
        el_name = self.selected_node[1]
        model = self.main_window.model
        dialog = gui_dialogs.ElementPropertiesDialog(el_name, model, self)
        dialog.show()

    def prism_compute_sub_models_and_repetitions(self):
        """@brief computes sub models"""
        if self.main_window.checker.check_sub_models(self.main_window.model):
            self.main_window.command_le.setText(str("prism.compute_sub_models_and_repetitions(model)"))
            self.main_window.execute_command()

    def compute_MTTF(self):
        """@brief computes MTTF"""
        if self.main_window.checker.check(self.main_window.model):
            self.main_window.command_le.setText(\
                str("prism.compute_MTTF(model, '" + self.selected_node[1] + "')"))
            self.main_window.execute_command()

    def compute_P(self):
        """@brief computes MTTF"""
        if self.main_window.checker.check(self.main_window.model):
            cmd = "prism.compute_P(model, '" + self.selected_node[1] + "', step_range='0:10:100')"
            self.main_window.command_le.setPalette(self.main_window.palette_highlight)
            self.main_window.command_le.setText(cmd)
            self.main_window.command_le.setCursorPosition(len(cmd)-2)
            self.main_window.command_le.setFocus()

    def compute_P_single(self):
        """@brief computes MTTF"""
        if self.main_window.checker.check(self.main_window.model):
            self.main_window.command_le.setText(\
                str("prism.compute_P_single(model, '" + self.selected_node[1] + "')"))
            self.main_window.execute_command()

    def compute_N_failures(self):
        """@brief computes MTTF"""
        if self.main_window.checker.check(self.main_window.model):
            cmd = "prism.compute_N_failures(model, '" + self.selected_node[1] + "', step_range='0:10:100')"
            self.main_window.command_le.setPalette(self.main_window.palette_highlight)
            self.main_window.command_le.setText(cmd)
            self.main_window.command_le.setCursorPosition(len(cmd)-2)
            self.main_window.command_le.setFocus()

    def compute_downtime(self):
        """@brief computes MTTF"""
        if self.main_window.checker.check(self.main_window.model):
            cmd = "prism.compute_downtime(model, '" + self.selected_node[1] + \
                "', step_range='0:10:100')"
            self.main_window.command_le.setPalette(self.main_window.palette_highlight)
            self.main_window.command_le.setText(cmd)
            self.main_window.command_le.setCursorPosition(len(cmd)-2)
            self.main_window.command_le.setFocus()   
