"""
Error Propagation Library V6
Checking DEPM
"""

import re

class Checker(object):
    """@brief Checking class"""

    def __init__(self):
        """@brief Constructor"""
        self.model_status = ['Error', 'Mode is not checked']
        self.elements_status = {}
        self.data_status = {}
        self.failure_status = {}

    def reset(self):
        """@brief clears state"""
        self.model_status = ['Error', 'Mode is not checked']
        self.elements_status = {}
        self.data_status = {}
        self.failure_status = {}

    def __check_cf_prism_commands(self, model, element_name):
        """@brief checking correctness of the cf_prism_commands"""
        # element existence check
        if not element_name in model.elements:
            model.logger.error("No element \"" + element_name + "\"")
            return False
        the_element = model.elements[element_name]
        cf_commands = the_element['cf_prism_commands']
        if cf_commands:
            findcfoutg = {cfout:False for cfout in the_element['cf_outputs']}
            for command in cf_commands:
                cfapart = re.split("[^A-Za-z0-9_]", command)
                cwords = ['max', 'min', 'log', 'mod', 'pow', 'floor', 'stop']
                cfapart = [part for part in cfapart if part == "cf'" or not part in cwords \
                    and not part == '' and bool(re.fullmatch('[A-Za-z_][A-Za-z0-9_]*', part))]
                k = 0
                e_nfound = False
                cfapartb = {cfout:False for cfout in cfapart}
                while k < len(cfapart):
                    if cfapart[k] == 'cf' and not e_nfound:
                        e_nfound = True
                        cfapartb[cfapart[k]] = True
                        if cfapart[k+1] == element_name:
                            cfapartb[cfapart[k+1]] = True
                        else:
                            self.elements_status[element_name] = \
                                model.logger.error('Element ' + element_name + \
                               ' has wrong element_name in cf_prism_commands')
                            return False
                    elif cfapart[k] == 'cf' and e_nfound:
                        cfapartb[cfapart[k]] = True
                        for output in findcfoutg.keys():
                            if cfapart[k+1] == output:
                                cfapartb[cfapart[k+1]] = True
                                findcfoutg[cfapart[k+1]] = True
                    else:
                        for df_input in the_element['df_inputs']:
                            if cfapart[k] == df_input:
                                cfapartb[cfapart[k]] = True
                    for df_input in the_element['df_inputs']:
                        for value in model.data[df_input]['values']:
                            if cfapart[k] == value:
                                cfapartb[cfapart[k]] = True
                    k += 1
                for cfab in cfapartb.values():
                    if not cfab:
                        self.elements_status[element_name] = \
                            model.logger.error('Element ' + element_name + \
                            ' has error in cf_prism_commands')
                        return False
            for fcg in findcfoutg.values():
                if not fcg:
                    self.elements_status[element_name] = \
                        model.logger.error('Element ' + element_name + \
                        ' has error in cf_prism_commands')
                    return False
        #if all cf prism commands are ok
        return True

    def __check_ep_prism_commands(self, model, element_name):
        """@brief checking correctness of the ep_prism_commands"""
        # element existence check
        if not element_name in model.elements:
            model.logger.error("No element \"" + element_name + "\"")
            return False
        the_element = model.elements[element_name]
        ep_commands = the_element['ep_prism_commands']
        globb = {b:True for b in ep_commands}
        if ep_commands:
            for command in ep_commands:
                cwords = ['max', 'min', 'log', 'mod', 'pow', 'floor']
                leftsplited = re.split("[^A-Za-z0-9_]", re.split("->", command)[0])
                leftsplited = [split for split in leftsplited if not split in cwords \
                    and not split == '' and not bool(re.fullmatch('[0-9]*e', split)) \
                    and not bool(re.fullmatch('[0-9]*', split))]
                lsplitb = {split:False for split in leftsplited}
                for split in leftsplited:
                    for df_input in the_element['df_inputs']:
                        for value in model.data[df_input]['values']:
                            if split == value:
                                lsplitb[split] = True
                        if split == df_input:
                            lsplitb[split] = True
                    if split == 'true':
                        lsplitb[split] = True
                rightsplited = re.split("[^A-Za-z0-9_]", re.split("->", command)[1])
                rightsplited = [split for split in rightsplited if not split in cwords \
                    and not split == '' and not bool(re.fullmatch('[0-9]*e', split)) \
                    and not bool(re.fullmatch('[0-9]*', split))]
                rsplitb = {split:False for split in rightsplited}
                for split in rightsplited:
                    for d_name in set(the_element['df_outputs'] + the_element['df_inputs']):
                        for value in model.data[d_name]['values']:
                            if split == value:
                                rsplitb[split] = True
                        if split == d_name:
                            rsplitb[split] = True
                    if split == 'true':
                        rsplitb[split] = True
                if False in rsplitb.values() or False in lsplitb.values():
                    globb[command] = False
        if False in globb.values():
            self.elements_status[element_name] = \
                model.logger.error('Element ' + element_name + \
                ' has error in ep_prism_commands')
            return False
        #if all ep prism commands are ok
        return True

    def check_element(self, model, element_name):
        """@brief checking element correctness"""
        # element existence check
        if element_name not in model.elements:
            model.logger.error("No element \"" + element_name + "\"")
            return False
        the_element = model.elements[element_name]
        # check the name of the element
        if not model.check_name_correct(element_name):
            self.elements_status[element_name] = model.logger.error(\
                "Bad element name \"" + element_name + "\"")
            return False
        # unique name check with data and failures
        if not model.check_name_unique(element_name, check_elements=False):
            self.elements_status[element_name] = model.logger.error(\
                "Non-unique element name \"" + element_name + "\"")
            return False
        # a non-initial element has an incoming CF arc
        if element_name != model.initial_element and the_element['cf_inputs'] == []:
            self.elements_status[element_name] = model.logger.error(\
                "Element \"" + element_name + "\" has no incoming control flow arc")
            return False
        # compound
        if model.elements[element_name]['sub_model']:
            self.elements_status[element_name] = model.logger.warning(\
                "Element \"" + element_name + "\" contains a sub_model that should be computed")
        if model.elements[element_name]['sub_model']\
            and model.elements[element_name]['ep_prism_commands']:
            self.elements_status[element_name] = model.logger.warning(\
                "Element \"" + element_name + \
                "\" contains both a sub_model and ep_prism_commands")
        else:
            if not self.__check_cf_prism_commands(model, element_name):
                return False
            if not self.__check_ep_prism_commands(model, element_name):
                return False
        # if OK
        self.elements_status[element_name] = model.logger.message(\
            "Element \"" + element_name + "\" is OK")
        return True

    def check_data(self, model, data_name):
        """@brief checking data correctness"""
        # data existence check
        if not data_name in model.data:
            model.logger.error("No data \"" + data_name + "\"")
            return False
        # check the name of the data
        if not model.check_name_correct(data_name):
            self.data_status[data_name] = model.logger.error(\
                "Bad data name \"" + data_name + "\"")
            return False
        # unique name check with elements and failures
        if not model.check_name_unique(data_name, check_data=False):
            self.data_status[data_name] = model.logger.error(\
                "Non-unique data name \"" + data_name + "\"")
            return False
        # check values
        values = model.data[data_name]['values']
        initial_value = model.data[data_name]['initial_value']
        if not model.check_data_values(data_name, values, initial_value):
            self.data_status[data_name] = model.logger.error(\
                "Bad values of data \"" + data_name + "\"")
            return False
        # if OK
        self.data_status[data_name] = model.logger.message(\
            "Data \"" + data_name + "\" is OK")
        return True

    def check_failure(self, model, failure_name):
        """@brief checking failure correctness"""
        # failure existence check
        if not failure_name in model.failures:
            model.logger.error("No failure \"" + failure_name + "\"")
            return False
        # check failure expression
        expression = model.failures[failure_name]
        ok_flag = False
        cwords = ['max', 'min', 'log', 'mod', 'pow', 'floor', 'true', 'cf']
        for split in re.split("[^A-Za-z0-9_]", expression):
            for data in model.data:
                for value in model.data[data]['values']:
                    if str(value) in split:
                        ok_flag = True
                if data in split:
                    ok_flag = True
            for element in model.elements:
                if element in split:
                    ok_flag = True
            if bool(re.fullmatch('[0-9]*', split)):
                ok_flag = True
            if bool(re.fullmatch('[0-9]*e', split)):
                ok_flag = True
            elif split in cwords:
                ok_flag = True
            if not ok_flag:
                self.failure_status[failure_name] = model.logger.error(\
                    "Bad expression of failure \"" + failure_name + "\"")
                return False
            ok_flag = False
        # if OK
        self.failure_status[failure_name] = model.logger.message(\
            "Failure \"" + failure_name + "\" is OK")
        return True

    def check(self, model, host_model=None, host_element_name=None):
        """@brief checks the model before the analysis"""
        model.logger.message('Checking ...')
        self.reset()
        ret = True
        #check elements
        for element_name in model.elements:
            ret = self.check_element(model, element_name) and ret
        # check datas
        for data_name in model.data:
            ret = self.check_data(model, data_name) and ret
        # check failures
        for failure_name in model.failures:
            ret = self.check_failure(model, failure_name) and ret
        # check that model has an initial element
        if model.initial_element is None:
            model.logger.error('Model has no initial element')
            ret = False
        else:
            if model.initial_element not in model.elements.keys():
                model.logger.error('Bad initial element')
                ret = False
        # check data consitency with host model
        if host_model and host_element_name:
            ext_ins = set(host_model.elements[host_element_name]['df_inputs'])
            ext_outs = set(host_model.elements[host_element_name]['df_outputs'])
            int_ins = set()
            int_outs = set()
            for element in model.elements.keys():
                int_ins |= {df_input for df_input in model.elements[element]['df_inputs']}
                int_outs |= {df_output for df_output in model.elements[element]['df_outputs']}
            if not ext_ins <= int_ins or not ext_outs <= int_outs:
                model.logger.error('Inconsistent data flow with host model')
                ret = False
        if ret:
            self.model_status = model.logger.message('Model is OK')
        else:
            self.model_status = model.logger.error('Model contains errors')
        return ret

    def check_sub_models(self, model, compound_elements=None):
        """@brief checks that submodels has no host elements with the same names"""
        if compound_elements is None:
            compound_elements = []
        else:
            same_el = next((el_name for el_name, el_value in model.elements.items() \
                if el_value['sub_model'] and el_name in compound_elements), None)
            if same_el:
                model.logger.error("Model contains two compound elements with the same name \"" \
                    + same_el + "\"")
                return False
        local_compound_elements = [el_name \
            for el_name, el_value in model.elements.items() if el_value['sub_model']]
        for el_name, el_value in model.elements.items():
            if el_value['sub_model']:
                if not self.check(el_value['sub_model'], \
                    host_model=model, host_element_name=el_name):
                    return False
                if not self.check_sub_models(el_value['sub_model'], \
                    compound_elements + local_compound_elements):
                    return False
        return True
