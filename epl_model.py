"""
Error Propagation Library V6.
Model class.
"""

import re

class Model(object):
    """@brief Model class"""

    def __init__(self, logger):
        """@brief constructor"""
        self.logger = logger
        self.elements = {} # key = element name
        self.data = {}     # key = data name
        self.failures = {} # key = failure name
        self.initial_element = None
        self.logger.message("Model created")

    def check_name_correct(self, name):
        """@brief checks that name is not keyword and matches to PRISM regexp"""
        prism_keywords = ['A', 'bool', 'clock', 'const', 'ctmc', 'C', \
            'double', 'dtmc', 'E', 'endinit', 'endinvariant', 'endmodule', \
            'endrewards', 'endsystem', 'false', 'formula', 'filter', 'func', \
            'F', 'global', 'G', 'init', 'invariant', 'I', 'int', 'label', 'max', \
            'mdp', 'min', 'module', 'X', 'nondeterministic', 'Pmax', 'Pmin', 'P', \
            'probabilistic', 'prob', 'pta', 'rate', 'rewards', 'Rmax', 'Rmin', 'R', \
            'S', 'stochastic', 'system', 'true', 'U', 'W', 'stop', 'pow', 'mod', \
            'log', 'floor']
        if not isinstance(name, str):
            self.logger.error("Name \"" + str(name)+ "\" is not a string")
            return False
        if not name:
            self.logger.error("Empty name")
            return False
        if name in prism_keywords or not bool(re.fullmatch('[A-Za-z_][A-Za-z0-9_]*', name)):
            self.logger.error("Bad name: \"" + name + \
                "\" is either a reserved keyword or does not match to \"[A-Za-z_][A-Za-z0-9_]*\"")
            return False
        return True

    def check_name_unique(self, name, check_elements=True, check_data=True, check_failures=True):
        """@brief checks that no element, data, or failure with such name exists"""
        if check_elements and name in self.elements:
            self.logger.error("Bad name: Element \"" + name + "\" already exists")
            return False
        if check_data and name in self.data:
            self.logger.error("Bad name: Data \"" + name + "\" already exists")
            return False
        if check_failures and name in self.failures:
            self.logger.error("Bad name: Failure \"" + name + "\" already exists")
            return False
        return True

    def check_name(self, name):
        """@brief checks that name is correct and unique"""
        return self.check_name_correct(name) and self.check_name_unique(name)

    def clear(self):
        """@brief clears model"""
        self.elements.clear()
        self.data.clear()
        self.failures.clear()
        self.initial_element = None
        self.logger.message("Model cleared")

    def set_initial_element(self, name):
        """@brief sets initial element"""
        # name check
        if not name in self.elements:
            self.logger.error("No element " + name + " found")
            return False
        # set initial element
        self.initial_element = name
        self.logger.message("Initial element is set to " + name)
        return True

    def add_element(self, name, time=1, sub_model=None, repetitions=1):
        """@brief adds new element"""
        # check name
        if not self.check_name(name):
            return False
        # check time
        if not isinstance(time, (float, int)):
            self.logger.error("Time value of \"" + name + "\" is not float or int")
            return False
        # check sub_model
        if not (sub_model is None or isinstance(sub_model, Model)):
            self.logger.error("Sub model \"" + name + \
                "\" is not an instance of class epl_model.Model")
            return False
        # check repetitions
        if not isinstance(repetitions, int):
            self.logger.error("Repetitions value of \"" + name + "\" is not int")
            return False
        if repetitions < 1:
            self.logger.error("Repetitions value of \"" + name + "\" is less than 1")
            return False
        # add element
        self.elements[name] = {\
            'sub_model': sub_model, \
            'repetitions': repetitions, \
            'time': time, \
            'cf_inputs': [], \
            'cf_outputs': [], \
            'df_inputs': [], \
            'df_outputs': [], \
            'cf_prism_commands': [], \
            'ep_prism_commands': []}
        self.logger.message("Element \"" + name + "\" added")
        return True

    def update_element_repetitions(self, name, repetitions=1):
        """@brief adds new element"""
        # element existence check
        if not name in self.elements:
            self.logger.error("No element \"" + name + "\"")
            return False
        # check repetitions
        if not isinstance(repetitions, int):
            self.logger.error("Repetitions value of \"" + name + "\" is not int")
            return False
        if repetitions < 1:
            self.logger.error("Repetitions value of \"" + name + "\" is less than 1")
            return False
        # update repetitions
        self.elements[name]['repetitions'] = repetitions
        self.logger.message("Repetitions of element \"" + name + "\" set to " + str(repetitions))
        return True

    def update_element_time(self, name, time=1):
        """@brief adds new element"""
        # element existence check
        if not name in self.elements:
            self.logger.error("No element \"" + name + "\"")
            return False
        # check time
        if not isinstance(time, (float, int)):
            self.logger.error("Time value of \"" + name + "\" is not float or int")
            return False
        # update time
        self.elements[name]['time'] = time
        self.logger.message("Time of element \"" + name + "\" set to " + str(time))
        return True

    def remove_element(self, name):
        """@brief removes element"""
        # element existence check
        if not name in self.elements:
            self.logger.error("No element \"" + name + "\"")
            return False
        the_element = self.elements[name]
        # remove control_flow
        cf_inputs = the_element['cf_inputs'].copy()
        for cf_input in cf_inputs:
            self.remove_control_flow(cf_input, name)
        cf_outputs = the_element['cf_outputs'].copy()
        for cf_output in cf_outputs:
            self.remove_control_flow(name, cf_output)
        # remove data_flows
        df_inputs = the_element['df_inputs'].copy()
        print(df_inputs)
        for df_input in df_inputs:
            print(df_input)
            self.remove_data_flow(df_input, name)
        df_outputs = the_element['df_outputs'].copy()
        for df_output in df_outputs:
            self.remove_data_flow(name, df_output)
        # remove the element
        del self.elements[name]
        # remove if initial
        if self.initial_element == name:
            self.initial_element = None
        self.logger.message("Element \"" + name + "\" removed")
        return True

    def check_data_values(self, data_name, values, initial_value):
        """@brief checks that values and initial_value are correct"""
        if not isinstance(values, list):
            self.logger.error("Values of \"" + data_name + "\" should be defined as a list")
            return False
        for value in values:
            if not isinstance(value, (int, str)):
                self.logger.error("Values of \"" + data_name + "\" should be str or int")
                return False
            if isinstance(value, int):
                if value < 0:
                    self.logger.error("Int values of \"" + data_name + "\" should be positive")
                    return False
                elif value > 1000:
                    self.logger.error("Int value of \"" + data_name + \
                        "\" is larger than 1000, check PRSIM range")
            if isinstance(value, str) and not self.check_name(value):
                self.logger.error("Bad value \"" + value + \
                    "\" of \"" + data_name + "\", there is another component with this name")
                return False
        if initial_value not in values:
            self.logger.error("Initial value \"" + str(initial_value) + \
                "\" not in values")
            return False
        if len(values) > 10:
            self.logger.warning("Data \"" + data_name + \
                "\" has > 10 posssible values, think about state space")
        return True

    def add_data(self, name, values=None, initial_value=None):
        """@brief adds new data"""
        # check name
        if not self.check_name(name):
            return False
        # check values
        if values is None:
            values = ['ok', 'error']
        if initial_value is None:
            initial_value = values[0]
        if not self.check_data_values(name, values, initial_value):
            return False
        # add data
        self.data[name] = {\
            'df_inputs': [], \
            'df_outputs': [], \
            'values': values, \
            'initial_value': initial_value}
        self.logger.message("Data \"" + name + "\" added: values = " \
            + str(values) + ", initial_value = " + str(initial_value))
        return True

    def update_data_values(self, name, values=None, initial_value=None):
        """@brief updates data values and initial value"""
        # check data name
        if not name in self.data:
            self.logger.error("No data \"" + name + "\"")
            return False
        # check values
        if values is None:
            values = ['ok', 'error']
        if not isinstance(values, list):
            self.logger.error("Values of \"" + name + "\" should be defined as a list")
            return False
        if not self.check_data_values(name, values, initial_value):
            return False
        if initial_value is None:
            initial_value = values[0]
        # update values
        self.data[name]['values'] = values
        self.data[name]['initial_value'] = initial_value
        self.logger.message("Data \"" + name + "\" values updated: values = " \
            + str(values) + ", initial_value = " + str(initial_value))
        return True

    def remove_data(self, name):
        """@brief removes data"""
        # data existence check
        if not name in self.data:
            self.logger.error("No data \"" + name + "\"")
            return False
        the_data = self.data[name]
        # remove data_flows
        df_inputs = the_data['df_inputs'].copy()
        for df_input in df_inputs:
            self.remove_data_flow(df_input, name)
        df_outputs = the_data['df_outputs'].copy()
        for df_output in df_outputs:
            self.remove_data_flow(name, df_output)
        # remove the data
        del self.data[name]
        self.logger.message("Data \"" + name + "\" removed")
        return True

    def add_control_flow(self, from_name, to_name):
        """@brief adds new control flow arc"""
        # check from and to elements
        if not from_name in self.elements:
            self.logger.error("No element \"" + from_name + "\"")
            return False
        if not to_name in self.elements:
            self.logger.error("No element \"" + to_name + "\"")
            return False
        # check that no control flow exists
        if to_name in self.elements[from_name]['cf_outputs'] or \
            from_name in self.elements[to_name]['cf_inputs']:
            self.logger.error("Control flow from \"" + from_name + \
                "\" -> \"" + to_name + "\" already exists")
            return False
        # add control flow
        self.elements[from_name]['cf_outputs'].append(to_name)
        self.elements[to_name]['cf_inputs'].append(from_name)
        self.logger.message("Control flow arc added: \"" + \
            from_name + "\" -> \"" + to_name + "\"")
        return True

    def remove_control_flow(self, from_name, to_name):
        """@brief removes control flow arc"""
        # check from and to elements
        if not from_name in self.elements:
            self.logger.error("No element \"" + from_name + "\"")
            return False
        if not to_name in self.elements:
            self.logger.error("No element \"" + to_name + "\"")
            return False
        # check that this arc exists
        if not to_name in self.elements[from_name]['cf_outputs'] or \
            not from_name in self.elements[to_name]['cf_inputs']:
            self.logger.error("No control flow arc \"" + from_name + \
                "\" -> \"" + to_name + "\"")
            return False
        self.elements[from_name]['cf_outputs'].remove(to_name)
        self.elements[to_name]['cf_inputs'].remove(from_name)
        self.logger.message("Control flow arc \"" + from_name + \
                "\" -> \"" + to_name + "\" removed")
        return True

    def __get_type(self, name):
        """@brief finds types of epl components"""
        res = None
        if name in self.elements:
            res = 'element'
        elif name in self.data:
            res = 'data'
        if res is None:
            self.logger.error("Neither element nor data \"" + name + "\"")
        return res

    def add_data_flow(self, from_name, to_name):
        """@brief adds new data flow arc"""
        # check from and to parameters
        from_what = self.__get_type(from_name)
        to_what = self.__get_type(to_name)
        if from_what is None or to_what is None:
            return False
        if from_what == 'element' and to_what == 'element':
            self.logger.error("Data flow from an element to an element is forbidden")
            return False
        if from_what == 'data' and to_what == 'data':
            self.logger.error("Data flow from a data to a data is forbidden")
            return False
        # check existence and add
        if from_what == 'element':
            # check arc
            if to_name in self.elements[from_name]['df_outputs']:
                self.logger.error("Data flow arc \"" + from_name + \
                        "\" -> \"" + to_name + "\" already exists")
                return False
            # add
            self.elements[from_name]['df_outputs'].append(to_name)
            self.data[to_name]['df_inputs'].append(from_name)
        else:  # from_what == 'data'
            if from_name in self.elements[to_name]['df_inputs']:
                self.logger.error("Data flow arc \"" + from_name + \
                        "\" -> \"" + to_name + "\" already exists")
                return False
            # add
            self.elements[to_name]['df_inputs'].append(from_name)
            self.data[from_name]['df_outputs'].append(to_name)
        self.logger.message("Data flow arc added: \"" + \
            from_name + "\" -> \"" + to_name + "\"")
        return True

    def remove_data_flow(self, from_name, to_name):
        """@brief removes data flow arc"""
        # check from and to elements
        from_what = self.__get_type(from_name)
        if from_what == 'failure' or from_what is None:
            return False
        # check that this arc exists
        if from_what == 'element':
            if not to_name in self.elements[from_name]['df_outputs'] or \
                not from_name in self.data[to_name]['df_inputs']:
                self.logger.error("No data flow arc \"" + from_name + \
                    "\" -> \"" + to_name + "\"")
                return False
            self.elements[from_name]['df_outputs'].remove(to_name)
            self.data[to_name]['df_inputs'].remove(from_name)
        else:  # from_what == 'data'
            if not to_name in self.data[from_name]['df_outputs'] or \
                not from_name in self.elements[to_name]['df_inputs']:
                self.logger.error("No data flow arc \"" + from_name + \
                    "\" -> \"" + to_name + "\"")
                return False
            self.data[from_name]['df_outputs'].remove(to_name)
            self.elements[to_name]['df_inputs'].remove(from_name)
        self.logger.message("Data flow arc \"" + from_name + \
                "\" -> \"" + to_name + "\" removed")
        return True

    def add_failure(self, name, expression):
        """@brief adds new failure"""
        # check name
        if not self.check_name(name):
            return False
        self.failures[name] = expression
        self.logger.message("Failure added: " + name + " = '" + expression + "'")
        return True

    def update_failure(self, name, expression):
        """@brief updates failure expression"""
        # check existence
        if not name in self.failures:
            self.logger.error("No failure \"" + name + "\"")
            return False
        # update
        self.failures[name] = expression
        self.logger.message("Failure updated: " + name + " = '" + expression + "'")
        return True

    def remove_failure(self, name):
        """@brief removes data flow arc"""
        # check existence
        if not name in self.failures:
            self.logger.error("No failure \"" + name + "\"")
            return False
        # remove
        del self.failures[name]
        self.logger.message("Failure removed: " + name)
        return True

    def create_sub_model(self, el_name):
        """@brief creates an empty sub model for an element"""
        # check existence
        if not el_name in self.elements:
            self.logger.error("No element \"" + el_name + "\"")
            return False
        if self.elements[el_name]['sub_model']:
            self.logger.error("Element \"" + el_name + "\" already contains sub model")
            return False
        # create sub model
        sub_model = Model(self.logger)
        # create internal data
        inner_data = list(set(self.elements[el_name]['df_inputs'] + \
            self.elements[el_name]['df_outputs']))
        for d_name in inner_data:
            sub_model.add_data(d_name, \
                values=self.data[d_name]['values'], \
                initial_value=self.data[d_name]['initial_value'])
        # add submodel
        self.elements[el_name]['sub_model'] = sub_model
        self.elements[el_name]['ep_prism_commands'] = []
        self.elements[el_name]['time'] = 1
        return True

    def remove_sub_model(self, el_name):
        """@brief removes sub model for an element"""
        # check existence
        if not el_name in self.elements:
            self.logger.error("No element \"" + el_name + "\"")
            return False
        if not self.elements[el_name]['sub_model']:
            self.logger.error("Element \"" + el_name + "\" has no sub model")
            return False
        # remove submodel
        self.elements[el_name]['sub_model'] = None
        return True
