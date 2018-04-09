"""
ErrorPro V6.
PySide GUI element properties.
"""

from PySide import QtGui
from PySide import QtCore

from epl_prism import PRISM

class ElementPropertiesDialog(QtGui.QDialog):
    """@brief element properties dialog"""
    def __create_current_cf_text(self):
        """@brief CF inputs"""
        cf_inputs_text = "Current CF:\n"
        cf_inputs_text += "  cf=" + self.el_name + "\n"
        return cf_inputs_text

    def __create_cf_outputs_text(self):
        """@brief CF outputs"""
        if not self.element['cf_outputs']:
            return ""
        cf_outputs_text = "CF outputs:\n"
        if self.element['cf_outputs']:
            cf_outputs_text += "  cf'={"
            for cf_output in self.element['cf_outputs']:
                cf_outputs_text += cf_output + ", "
            cf_outputs_text = cf_outputs_text[:-2]
            cf_outputs_text += "}\n"
        return cf_outputs_text

    def __create_df_inputs_text(self):
        """@brief DF inputs"""
        if not self.element['df_inputs']:
            return ""
        df_inputs_text = "DF inputs:\n"
        for df_input in self.element['df_inputs']:
            df_inputs_text += "  " + df_input + "={"
            values = self.model.data[df_input]['values'] if \
            len(self.model.data[df_input]['values']) <= 4 else \
            self.model.data[df_input]['values'][:2] + ['...', \
                self.model.data[df_input]['values'][-1]]
            for value in values:
                df_inputs_text += str(value) + ", "
            df_inputs_text = df_inputs_text[:-2] + "}\n"
        return df_inputs_text

    def __create_df_outputs_text(self):
        """@brief DF outputs"""
        if not self.element['df_outputs']:
            return ""
        df_outputs_text = "DF outputs:\n"
        for df_output in self.element['df_outputs']:
            df_outputs_text += "  " + df_output + "'={"
            values = self.model.data[df_output]['values'] if \
            len(self.model.data[df_output]['values']) <= 4 else \
            self.model.data[df_output]['values'][:2] + ['...', self.model.data[df_output]['values'][-1]]
            for value in values:
                df_outputs_text += str(value) + ", "
            df_outputs_text = df_outputs_text[:-2] + "}\n"
        return df_outputs_text

    def __add_cf_part(self):
        """@brief generate layout for cf part"""
        cfc_res_btn = QtGui.QPushButton("Restore")
        cfc_res_btn.clicked.connect(self.res_cfc)
        cfc_def_btn = QtGui.QPushButton("Default")
        cfc_def_btn.clicked.connect(self.def_cfc)
        cfc_save_btn = QtGui.QPushButton("Save")
        cfc_save_btn.clicked.connect(self.save_cfc)
        cfc_label = QtGui.QLabel("Control flow commands")
        cf_current_cf_text = self.__create_current_cf_text()
        df_inputs_text = self.__create_df_inputs_text()
        cf_outputs_text = self.__create_cf_outputs_text()
        cfc_in_label = QtGui.QLabel(cf_current_cf_text+df_inputs_text)
        cfc_in_label.setAlignment(QtCore.Qt.AlignTop)
        cfc_out_label = QtGui.QLabel(cf_outputs_text)
        cfc_out_label.setAlignment(QtCore.Qt.AlignTop)
        self.cf_commands_te = QtGui.QTextEdit()
        if self.element['cf_prism_commands']:
            for cfc in self.element['cf_prism_commands']:
                self.cf_commands_te.append(cfc)
        self.layout.addWidget(cfc_label)
        cfc_hbox_1 = QtGui.QHBoxLayout()
        cfc_hbox_1.addWidget(cfc_in_label)
        cfc_hbox_1.addWidget(cfc_out_label)
        cfc_hbox_2 = QtGui.QHBoxLayout()
        cfc_hbox_2.addStretch(1)
        cfc_hbox_2.addWidget(cfc_def_btn)
        cfc_hbox_2.addWidget(cfc_res_btn)
        cfc_hbox_2.addWidget(cfc_save_btn)
        self.layout.addLayout(cfc_hbox_1)
        self.layout.addWidget(self.cf_commands_te)
        self.layout.addLayout(cfc_hbox_2)

    def __add_ep_part(self):
        """@brief generate layout for ep part"""
        epc_res_btn = QtGui.QPushButton("Restore")
        epc_res_btn.clicked.connect(self.res_epc)
        epc_def_btn = QtGui.QPushButton("Default")
        epc_def_btn.clicked.connect(self.def_epc)
        epc_save_btn = QtGui.QPushButton("Save")
        epc_save_btn.clicked.connect(self.save_epc)
        epc_label = QtGui.QLabel("Error propagation commands")
        df_inputs_text = self.__create_df_inputs_text()
        df_outputs_text = self.__create_df_outputs_text()
        epc_in_label = QtGui.QLabel(df_inputs_text)
        epc_in_label.setAlignment(QtCore.Qt.AlignTop)
        epc_out_label = QtGui.QLabel(df_outputs_text)
        epc_out_label.setAlignment(QtCore.Qt.AlignTop)
        self.ep_commands_te = QtGui.QTextEdit()
        if self.element['ep_prism_commands']:
            for epc in self.element['ep_prism_commands']:
                self.ep_commands_te.append(epc)
        self.layout.addWidget(epc_label)
        epc_hbox_1 = QtGui.QHBoxLayout()
        epc_hbox_1.addWidget(epc_in_label)
        epc_hbox_1.addWidget(epc_out_label)
        epc_hbox_2 = QtGui.QHBoxLayout()
        epc_hbox_2.addStretch(1)
        epc_hbox_2.addWidget(epc_def_btn)
        epc_hbox_2.addWidget(epc_res_btn)
        epc_hbox_2.addWidget(epc_save_btn)
        self.layout.addLayout(epc_hbox_1)
        self.layout.addWidget(self.ep_commands_te)
        self.layout.addLayout(epc_hbox_2)

    def __init__(self, el_name, model, parent=None):
        """@brief constructor"""
        super(ElementPropertiesDialog, self).__init__(parent)
        self.model_view = parent
        self.element = model.elements[el_name]
        self.el_name = el_name
        self.model = model
        self.setWindowTitle('Properties of ' + el_name)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setGeometry(0, 0, 600, 600)
        self.layout = QtGui.QVBoxLayout()
        if (len(self.element['cf_outputs']) > 1) or \
            (self.element['cf_prism_commands']):
            self.__add_cf_part()
        if (not self.element['sub_model'] and self.element['df_outputs']) or \
            (self.element['ep_prism_commands']):
            if len(self.element['cf_outputs']) > 1:
                line = QtGui.QFrame()
                line.setFrameShape(QtGui.QFrame.HLine)
                line.setFrameShadow(QtGui.QFrame.Sunken)
                self.layout.addWidget(line)
            self.__add_ep_part()
        self.setLayout(self.layout)

    def def_cfc(self):
        self.cf_commands_te.clear()
        self.cf_commands_te.append(PRISM.generate_default_cf_commands(self.model, self.el_name))

    def res_cfc(self):
        self.cf_commands_te.clear()
        if self.element['cf_prism_commands']:
            for cfc in self.element['cf_prism_commands']:
                self.cf_commands_te.append(cfc)

    def save_cfc(self):
        self.element['cf_prism_commands'] = \
            [cfc for cfc in self.cf_commands_te.toPlainText().split('\n') if cfc]
        self.model_view.draw_model()

    def def_epc(self):
        self.ep_commands_te.clear()
        for command in PRISM.generate_default_ep_commands(self.model, self.el_name):
            self.ep_commands_te.append(command)

    def res_epc(self):
        self.ep_commands_te.clear()
        if not self.element['sub_model']:
            if self.element['ep_prism_commands']:
                for epc in self.element['ep_prism_commands']:
                    self.ep_commands_te.append(epc)

    def save_epc(self):
        if not self.element['sub_model']:
            self.element['ep_prism_commands'] = \
            [epc for epc in self.ep_commands_te.toPlainText().split('\n') if epc]
        self.model_view.draw_model()
