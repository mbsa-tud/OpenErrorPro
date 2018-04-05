"""
Error Propagation Library V6.
XML load/store related functions.
"""

from xml.dom.minidom import parse, Document
import itertools

import epl_model

class XML(object):
    """@brief class for load/save from/to XML"""

    @staticmethod
    def __load_elements(model_node, model):
        """@brief loads model elements"""
        element_nodes = model_node.getElementsByTagName('element')
        for element_node in element_nodes:
            name = str(element_node.getAttribute('name'))
            sub_model = None
            time = 1
            repetitions = 1
            if element_node.hasAttribute('compound'):
                if str(element_node.getAttribute('compound')) == "True":
                    sub_model = epl_model.Model(model.logger)
            if element_node.hasAttribute('time'):
                time = float(element_node.getAttribute('time'))
            if element_node.hasAttribute('repetitions'):
                repetitions = int(element_node.getAttribute('repetitions'))
            model.add_element(name, time, sub_model, repetitions)
            XML.__load_prism_commands(element_node, name, model)

    @staticmethod
    def __load_data(model_node, model):
        """@brief loads model data"""
        for data_node in model_node.getElementsByTagName('data'):
            name = str(data_node.getAttribute('name'))
            values = None
            initial_value = None
            if data_node.hasAttribute('values'):
                values = str(data_node.getAttribute('values')).split(",")
                values = [int(value) if value.strip().isdigit() \
                    else value.strip() for value in values]
                if len(values) > 10:
                    model.logger.warning("More than 10 possible values of \"" + \
                        name + "\", think about state space ...")
            if data_node.hasAttribute('initial_value'):
                initial_value = str(data_node.getAttribute('initial_value'))
                if initial_value.strip().isdigit():
                    initial_value = int(initial_value)
                else:
                    initial_value = initial_value.strip()
            model.add_data(name, values, initial_value)

    @staticmethod
    def __load_cf_arcs(model_node, model):
        """@brief loads cf arcs"""
        for cf_node in model_node.getElementsByTagName('control_flow'):
            model.add_control_flow(str(cf_node.getAttribute('from')), \
                str(cf_node.getAttribute('to')))

    @staticmethod
    def __load_df_arcs(model_node, model):
        """@brief loads df arcs"""
        for df_node in model_node.getElementsByTagName('data_flow'):
            model.add_data_flow(str(df_node.getAttribute('from')), \
                str(df_node.getAttribute('to')))

    @staticmethod
    def __load_prism_commands(element_node, name, model):
        """@brief loads model elements"""
        prism_cmds = element_node.getElementsByTagName('cfc')
        for prism_cmd in prism_cmds:
            model.elements[name]['cf_prism_commands'].append(prism_cmd.firstChild.nodeValue)
        prism_cmds = element_node.getElementsByTagName('epc')
        for prism_cmd in prism_cmds:
            model.elements[name]['ep_prism_commands'].append(prism_cmd.firstChild.nodeValue)

    @staticmethod
    def __load_failures(model_node, model):
        """@brief loads failures"""
        for failure in model_node.getElementsByTagName('failure'):
            name = str(failure.getAttribute('name'))
            model.add_failure(name, failure.firstChild.nodeValue)

    @staticmethod
    def load(model, file_name=""):
        """@brief loads model from an xml file"""
        try:
            dom = parse(file_name)
        except BaseException as exception:
            model.logger.error(str(exception))
            return False
        model.clear()
        models = {}
        for model_node in dom.getElementsByTagName('model'):
            if model_node.hasAttribute('host'):
                cur_model = epl_model.Model(model.logger)
                if str(model_node.getAttribute('host')) in models:
                    model.logger.error("Two submodels with the same host \"" \
                        + str(model_node.getAttribute('host')) + "\"")
                models[str(model_node.getAttribute('host'))] = cur_model
            else:
                cur_model = model
            XML.__load_elements(model_node, cur_model)
            XML.__load_data(model_node, cur_model)
            XML.__load_cf_arcs(model_node, cur_model)
            XML.__load_df_arcs(model_node, cur_model)
            XML.__load_failures(model_node, cur_model)
            if model_node.hasAttribute('initial_element'):
                cur_model.set_initial_element(\
                    str(model_node.getAttribute('initial_element')))
        #connect sub models
        for cur_model in itertools.chain([model], models.values()):
            for el_name, el_value in cur_model.elements.items():
                if el_value['sub_model']:
                    if not el_name in models:
                        model.logger.error("No sub model for \"" + el_name + "\"")
                    cur_model.elements[el_name]['sub_model'] = models[el_name]
        #print(model.elements)
        model.logger.message("The model has been loaded from file \"" + \
            file_name + "\"")
        return True

    @staticmethod
    def __save_elements(doc, model, model_node):
        """@brief saves model elements"""
        for el_name, el_value in model.elements.items():
            #elements
            element_node = doc.createElement('element')
            element_node.setAttribute('name', el_name)
            if el_value['time'] != 1:
                element_node.setAttribute('time', str(el_value['time']))
            if el_value['repetitions'] != 1:
                element_node.setAttribute('repetitions', str(el_value['repetitions']))
            if el_value['sub_model']:
                element_node.setAttribute('compound', "True")
            for cfc in el_value['cf_prism_commands']:
                cfc_node = doc.createElement("cfc")
                txt = doc.createTextNode(cfc)
                cfc_node.appendChild(txt)
                element_node.appendChild(cfc_node)
            for epc in el_value['ep_prism_commands']:
                epc_node = doc.createElement("epc")
                txt = doc.createTextNode(epc)
                epc_node.appendChild(txt)
                element_node.appendChild(epc_node)
            model_node.appendChild(element_node)

    @staticmethod
    def __save_cf_arcs(doc, model, model_node):
        """@brief saves model cf arcs"""
        for el_name, el_value in model.elements.items():
            #cf_arcs
            for val in el_value['cf_outputs']:
                cf_node = doc.createElement('control_flow')
                cf_node.setAttribute('from', el_name)
                cf_node.setAttribute('to', val)
                model_node.appendChild(cf_node)

    @staticmethod
    def __save_df_arcs(doc, model, model_node):
        """@brief saves model df arcs"""
        for el_name, el_value in model.elements.items():
            #df_arcs
            for val in el_value['df_outputs']:
                df_node = doc.createElement('data_flow')
                df_node.setAttribute('from', el_name)
                df_node.setAttribute('to', val)
                model_node.appendChild(df_node)
            for val in el_value['df_inputs']:
                df_node = doc.createElement('data_flow')
                df_node.setAttribute('from', val)
                df_node.setAttribute('to', el_name)
                model_node.appendChild(df_node)

    @staticmethod
    def __save_data(doc, model, model_node):
        """@brief saves model data slots"""
        for d_name, d_value in model.data.items():
            data_node = doc.createElement('data')
            data_node.setAttribute('name', d_name)
            if d_value['values'] != ['ok', 'error']:
                str_values = ""
                for value in d_value['values']:
                    str_values += str(value) + ", "
                str_values = str_values[:-2]
                data_node.setAttribute('values', str_values)
            if d_value['initial_value'] != d_value['values'][0]:
                data_node.setAttribute('initial_value', \
                    str(d_value['initial_value']))
            model_node.appendChild(data_node)

    @staticmethod
    def __save_failures(doc, model, model_node):
        """@brief saves failures"""
        for f_name, f_value in model.failures.items():
            f_node = doc.createElement('failure')
            f_node.setAttribute('name', f_name)
            txt = doc.createTextNode(f_value)
            f_node.appendChild(txt)
            model_node.appendChild(f_node)

    @staticmethod
    def __save_model(doc, epl_node, model, host=None):
        """@brief saves model to xml"""
        model_node = doc.createElement('model')
        if model.initial_element:
            model_node.setAttribute('initial_element', model.initial_element)
        if host:
            model_node.setAttribute('host', host)
        XML.__save_elements(doc, model, model_node)
        XML.__save_data(doc, model, model_node)
        XML.__save_cf_arcs(doc, model, model_node)
        XML.__save_df_arcs(doc, model, model_node)
        XML.__save_failures(doc, model, model_node)
        epl_node.appendChild(model_node)
        for el_name, el_value in model.elements.items():
            if el_value['sub_model']:
                XML.__save_model(doc, epl_node, el_value['sub_model'], el_name)

    @staticmethod
    def save(model, file_name="model.xml"):
        """@brief saves model to xml"""
        doc = Document()
        epl_node = doc.createElement('epl')
        XML.__save_model(doc, epl_node, model)
        doc.appendChild(epl_node)
        doc.writexml(open(file_name, 'w'), \
            indent="", addindent="    ", \
            newl='\n', encoding="utf-8")
        model.logger.message("The model has been saved to " + file_name)
        return True
