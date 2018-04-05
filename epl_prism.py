"""
Error Propagation Library V6.
PRISM interface.
"""

import os
import errno
import itertools
import subprocess

# keep this sequence of imports
import matplotlib
matplotlib.use('qt4agg')
import matplotlib.pyplot as plt

class PRISM(object):
    """@brief PRISM class """

    def __init__(self, no_output=False, timeout=180):
        """@brief Constructor"""
        # Update these settings for your system !
        self.prism_dir = "/Please/change/this/to/your/path/to/prism/bin"
        #self.prism_dir = "/Users/andrey/SourceTree/ErrorPro/prism-4.4-osx64/bin"
        self.prism_executable = "./prism"
        self.prism_model_file = "temp.pm"
        self.prism_properties_file = "temp.prop"
        self.prism_results_file = "temp.csv"
        self.prism_states_file = "states.txt"
        self.prism_ss_tr_file = "ss_tr.txt"
        self.no_output = no_output
        self.timeout = timeout

    @staticmethod
    def __generate_elements_consts(model):
        """@brief generates consts for data values"""
        res = "//Element consts\n"
        has_final_elements = False
        for i, el_name in enumerate(model.elements.keys()):
            res += "const int " + el_name + "=" + str(i) + ";\n"
            if not model.elements[el_name]['cf_outputs']:
                has_final_elements = True
        if has_final_elements:
            res += "const int stop=" + str(len(model.elements)) + ";\n"
        return res

    @staticmethod
    def __get_maximum_value(model):
        """@brief generates consts for data values"""
        str_values, int_values = PRISM.__separate_int_and_str_values(model)
        len_i = len(int_values)
        len_s = len(str_values)
        if len_i > 0:
            max_i = max(int_values)
        else:
            max_i = 1
        return max(max_i, len_s + len_i - 1)

    @staticmethod
    def __separate_int_and_str_values(model):
        """@brief generates consts for data values"""
        str_values = []
        int_values = []
        for data in model.data.values():
            for value in data['values']:
                if isinstance(value, str):
                    if value not in str_values:
                        str_values.append(value)
                elif isinstance(value, int):
                    if value not in int_values:
                        int_values.append(value)
        str_values.sort()
        int_values.sort()
        return [str_values, int_values]

    @staticmethod
    def encode_string_values(model):
        """@brief generates consts for data values"""
        str_values, int_values = PRISM.__separate_int_and_str_values(model)
        res = {}
        i = 0
        while str_values:
            if i not in int_values:
                res[i] = str_values.pop()
            i += 1
        return res

    @staticmethod
    def __generate_data_values_consts(model):
        """@brief generates consts for data values in prism format"""
        values = PRISM.encode_string_values(model)
        res = "//Data values consts\n"
        for key, value in values.items():
            res += "const int " + value + \
                    "=" + str(key) + ";\n"
        return res

    @staticmethod
    def generate_default_cf_commands(model, el_name):
        """@brief creates default prism cf commands"""
        res = "cf=" + el_name + " -> "
        el_value = model.elements[el_name]
        if not el_value['cf_outputs']:
            res += "(cf'=stop);"
        else:
            for cf_output in el_value['cf_outputs']:
                res += str(1/len(el_value['cf_outputs'])) + \
                ":(cf'=" + cf_output + ") + "
            res = res[:-3] + ";"
        return res

    @staticmethod
    def __generate_cf_module(model):
        """@brief creates cf prism module"""
        res = "//Control flow commands\n"
        res += "module control_flow\n"
        res += "\tcf:[0.." + str(len(model.elements)) +"] init " + model.initial_element + ";\n"
        for el_name, el_value in model.elements.items():
            res += "\t//Element " + el_name
            if el_value['df_inputs']:
                res += ", df inputs " + str(el_value['df_inputs'])
            res += ", cf transitions " + str(el_value['cf_outputs']) + "\n"
            if el_value['cf_prism_commands']:
                for cfc in el_value['cf_prism_commands']:
                    res += "\t[" + el_name + "] " + cfc + "\t// <-- \n"
            else:
                res += "\t[" + el_name + "] "
                res += PRISM.generate_default_cf_commands(model, el_name)
                res += "\n"
        res += "endmodule\n"
        return res

    @staticmethod
    def generate_default_ep_commands(model, el_name):
        """@brief creates default prism ep commands"""
        commands = []
        el_value = model.elements[el_name]
        if el_value['df_outputs']:
            if not el_value['df_inputs']:
                res = "(true) -> 1:"
                for df_output in el_value['df_outputs']:
                    ok_value = str(model.data[df_output]['initial_value'])
                    res += "(" + df_output + "'=" + ok_value + ") & "
                res = res[:-3] + ";"
                commands.append(res)
            else:
                # if all inputs OK than all outputs OK
                # OK = initial value
                res = ""
                for df_input in el_value['df_inputs']:
                    ok_value = str(model.data[df_input]['initial_value'])
                    res += "(" + df_input + "=" + ok_value + ") & "
                res = res[:-3]
                res += " -> "
                for df_output in el_value['df_outputs']:
                    ok_value = str(model.data[df_output]['initial_value'])
                    res += "(" + df_output + "'=" + ok_value + ") & "
                res = res[:-3] + ";"
                commands.append(res)
                # if one input is not OK than all outputs are not OK
                # not OK = first value that do not equal to the inital value
                res = ""
                for df_input in el_value['df_inputs']:
                    ok_value = model.data[df_input]['initial_value']
                    res += "(" + df_input + "!=" + str(ok_value) + ") | "
                res = res[:-3]
                res += " -> "
                for df_output in el_value['df_outputs']:
                    ok_value = model.data[df_output]['initial_value']
                    err_value = next((val for val in model.data[df_output]['values'] \
                        if val != ok_value), ok_value)
                    res += "(" + df_output + "'=" + str(err_value) + ") & "
                res = res[:-3] + ";"
                commands.append(res)
        return commands

    @staticmethod
    def __generate_ep_module(model, init_values=None):
        """@brief creates cf prism module"""
        res = "//Error propagation commands\n"
        res += "module error_propagation\n"
        for d_name, d_value in model.data.items():
            res += "\t" + d_name + " : [0 .. " + str(PRISM.__get_maximum_value(model)) + "] init "
            if init_values and d_name in init_values:
                res += str(init_values[d_name]) + ";\n"
            else:
                res += str(d_value['initial_value']) + ";\n"
        for el_name, el_value in model.elements.items():
            if el_value['sub_model']:
                model.logger.warning('Sub-model of element \"' + el_name + \
                    '\" is ignored in the PRISM model.')
            if el_value['repetitions'] > 1:
                model.logger.warning('Repetitions of element \"' + el_name + \
                    '\" are ignored in the PRISM model.')
            if el_value['df_outputs']:
                res += "\t//Element " + el_name
                if el_value['df_inputs']:
                    res += ", df inputs " + str(el_value['df_inputs'])
                res += ", df outputs " + str(el_value['df_outputs']) + "\n"
                if el_value['ep_prism_commands']:
                    for epc in el_value['ep_prism_commands']:
                        res += "\t[" + el_name + "] " + epc + "\t// <-- \n"
                else:
                    for command in PRISM.generate_default_ep_commands(model, el_name):
                        res += "\t[" + el_name + "] " + command + "\n"
        res += "endmodule\n"
        return res

    @staticmethod
    def __generate_time_reward(model):
        """@brief creates rewards for failures and time"""
        res = "//Time reward\n"
        res += "rewards \"time\"\n"
        for el_name, el_value in model.elements.items():
            res += "\tcf=" + el_name + ":" + str(el_value['time'])+ ";\n"
        res += "endrewards\n"
        return res

    @staticmethod
    def __generate_failure_formulas(model):
        """@brief creates rewards for failures and time"""
        res = "//Failure formulas\n"
        for f_name, f_value in model.failures.items():
            res += "formula " + f_name + " = " + f_value + ";\n"
        return res

    @staticmethod
    def generate_prism_model(model, time_reward=False, ep_module=True, init_values=None):
        """@brief creates prism model"""
        res = "//Generated by ErrorPro\n"
        res += "dtmc\n"
        res += PRISM.__generate_elements_consts(model)
        if ep_module:
            res += PRISM.__generate_data_values_consts(model)
        res += PRISM.__generate_cf_module(model)
        if ep_module:
            res += PRISM.__generate_ep_module(model, init_values=init_values)
        if time_reward:
            res += PRISM.__generate_time_reward(model)
        return res

    @staticmethod
    def generate_prism_model_for_repetitions(model, el_name, init_values=None):
        """@brief creates prism model"""
        res = "//Generated by ErrorPro\n"
        res += "dtmc\n"
        res += PRISM.__generate_data_values_consts(model)
        res += "//Error propagation commands\n"
        res += "module error_propagation\n"
        d_ins = model.elements[el_name]['df_inputs']
        d_outs = model.elements[el_name]['df_outputs']
        d_ins_outs = set(d_ins + d_outs)
        el_data = {d_name:d_value for d_name, d_value in model.data.items() if d_name in d_ins_outs}
        for d_name, d_value in el_data.items():
            res += "\t" + d_name + " : [0 .. " + str(PRISM.__get_maximum_value(model)) + "] init "
            if init_values and d_name in init_values:
                res += str(init_values[d_name]) + ";\n"
            else:
                res += str(d_value['initial_value']) + ";\n"
        el_value = model.elements[el_name]
        if el_value['df_outputs']:
            if el_value['ep_prism_commands']:
                for epc in el_value['ep_prism_commands']:
                    res += "\t[] " + epc + "\t// <-- \n"
            else:
                for command in PRISM.generate_default_ep_commands(model, el_name):
                    res += "\t[] " + command + "\n"
        res += "endmodule\n"
        return res

    @staticmethod
    def silent_remove(filename):
        """@brief remove file if exists"""
        try:
            os.remove(filename)
        except OSError as exception:
            if exception.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
                raise # re-raise exception if a different error occurred

    def delete_temp_files(self):
        """@brief removes temporary PRISM files"""
        PRISM.silent_remove(self.prism_model_file)
        PRISM.silent_remove(self.prism_properties_file)
        PRISM.silent_remove(self.prism_results_file)
        PRISM.silent_remove(self.prism_ss_tr_file)
        PRISM.silent_remove(self.prism_states_file)

    @staticmethod
    def save(prism_model, file_name="model.pm"):
        """@brief save to prism format"""
        model_file = open(file_name, 'w')
        model_file.write(prism_model)
        model_file.close()

    def run_prism(self, prism_model, properties, step_range=None):
        """@brief call PRISM model checker"""
        old_dir = os.getcwd()
        os.chdir(self.prism_dir)
        #save prism model
        self.delete_temp_files()
        self.save(prism_model, file_name=self.prism_model_file)
        model_file = open(self.prism_properties_file, 'w')
        model_file.write(properties)
        model_file.close()
        if not step_range:
            call_list = [self.prism_executable, \
            self.prism_model_file, \
            self.prism_properties_file, \
            "-exportresults", self.prism_results_file, \
            "-timeout", str(self.timeout)]
        else:
            call_list = [self.prism_executable, \
            self.prism_model_file, \
            self.prism_properties_file, \
            "-exportresults", str(self.prism_results_file+":csv,matrix"),\
            "-const", "step="+step_range, \
            "-timeout", str(self.timeout)]
        if self.no_output:
            subprocess.call(call_list, stdout=subprocess.PIPE)
        else:
            subprocess.call(call_list)
        res_file = open(self.prism_results_file, 'r')
        results = [line.rstrip('\n') for line in res_file]
        res_file.close()
        os.chdir(old_dir)
        return results

    def __check_prism_result(self, res, logger):
        """@brief checks that PRISM returns a number but not an error string"""
        try:
            f_res = float(res)
            return f_res
        except ValueError:
            logger.error("Bad PRISM result: " + str(res))
            return 0

    def compute_execution_time(self, model):
        """@brief computes MTTF"""
        model.logger.message('Computing execution time ... ')
        prism_model = self.generate_prism_model(model, time_reward=True, ep_module=False)
        properties = "R{\"time\"}=? [ C ]"
        prism_res = self.run_prism(prism_model, properties)
        res = self.__check_prism_result(prism_res[1], model.logger)
        return res

    def compute_P_single(self, model, f_name, show_plot=True):
        """@brief computes MTTF"""
        model.logger.message('Computing P for ' + f_name + ' ... ')
        prism_model = self.generate_prism_model(model, time_reward=False)
        prism_model += "//Failure formulas\n"
        f_value = model.failures[f_name]
        prism_model += "formula " + f_name + " = " + f_value + ";\n"
        properties = "P=? [ F " + f_name + "]"
        prism_res = self.run_prism(prism_model, properties)
        res = self.__check_prism_result(prism_res[1], model.logger)
        return res

    def compute_MTTF(self, model, f_name, show_plot=True):
        """@brief computes MTTF"""
        model.logger.message('Computing MTTF for ' + f_name + ' ... ')
        prism_model = self.generate_prism_model(model, time_reward=True)
        prism_model += "//Failure formulas\n"
        f_value = model.failures[f_name]
        prism_model += "formula " + f_name + " = " + f_value + ";\n"
        properties = "R{\"time\"}=? [ F " + f_name + "]"
        prism_res = self.run_prism(prism_model, properties)
        res = self.__check_prism_result(prism_res[1], model.logger)
        return res

    def compute_P(self, model, f_name, show_plot=True, step_range="0:10:100"):
        """@brief computes probability over time"""
        model.logger.message('Computing P for ' + f_name + ' ... ')
        prism_model = self.generate_prism_model(model, time_reward=True)
        prism_model += "//Failure formulas\n"
        f_value = model.failures[f_name]
        prism_model += "formula " + f_name + " = " + f_value + ";\n"
        prism_model += "//Step number for properties\n"
        prism_model += "const int step;\n"
        properties = "P=? [ F<=step " + f_name + "]\n" + "R{\"time\"}=? [  C<=step ]"
        prism_res = self.run_prism(prism_model, properties, step_range=step_range)
        steps = [self.__check_prism_result(step, model.logger) \
            for step in prism_res[2].split(',')]
        times = [self.__check_prism_result(time, model.logger) \
            for time in prism_res[8].split(',')]
        probs = [self.__check_prism_result(prob, model.logger) \
            for prob in prism_res[3].split(',')]
        res = {'steps':steps, 'time':times, 'P':probs}
        if show_plot:
            plt.figure()
            plt.plot(times, probs, "bo-")
            plt.xlabel('Time (s)')
            plt.ylabel('Probability')
            plt.title(f_name + ': ' + f_value)
            plt.grid(True)
            plt.show()
        return res

    def compute_N_failures(self, model, f_name, show_plot=True, step_range="0:10:100"):
        """@brief computes probability over time"""
        model.logger.message('Computing N for ' + f_name + ' ... ')
        prism_model = self.generate_prism_model(model, time_reward=True)
        prism_model += "//Failure formulas\n"
        f_value = model.failures[f_name]
        prism_model += "formula " + f_name + " = " + f_value + ";\n"
        prism_model += "//Failure reward\n"
        prism_model += "rewards \"Failure\"\n"
        prism_model += "\t" + f_name + ":1;\n"
        prism_model += "endrewards\n"
        prism_model += "//Step number for properties\n"
        prism_model += "const int step;\n"
        properties = "R{\"Failure\"}=? [ C<=step ]\n" + "R{\"time\"}=? [  C<=step ]"
        prism_res = self.run_prism(prism_model, properties, step_range=step_range)
        steps = [self.__check_prism_result(step, model.logger) \
            for step in prism_res[2].split(',')]
        times = [self.__check_prism_result(time, model.logger) \
            for time in prism_res[8].split(',')]
        n_failures = [self.__check_prism_result(n_failure, model.logger) \
            for n_failure in prism_res[3].split(',')]
        res = {'steps':steps, 'time':times, 'P':n_failures}
        if show_plot:
            plt.figure()
            plt.plot(times, n_failures, "bo-")
            plt.xlabel('Time (s)')
            plt.ylabel('Number of failures')
            plt.title(f_name + ': ' + f_value)
            plt.grid(True)
            plt.show()
        return res

    def compute_downtime(self, model, f_name, show_plot=True, step_range="0:10:100"):
        """@brief computes downtime"""
        model.logger.message('Computing downtime for ' + f_name + ' ... ')
        prism_model = self.generate_prism_model(model, time_reward=True)
        prism_model += "//Failure formulas\n"
        f_value = model.failures[f_name]
        prism_model += "formula " + f_name + " = " + f_value + ";\n"
        prism_model += "//Down time rewards\n"
        prism_model += "rewards \"downtime\"\n"
        for el_name, el_value in model.elements.items():
            prism_model += "\t" + f_name +" & cf=" + el_name + ":" + str(el_value['time'])+ ";\n"
        prism_model += "endrewards\n"
        prism_model += "//Step number for properties\n"
        prism_model += "const int step;\n"
        properties = "R{\"downtime\"}=? [ C<=step ]\n" + "R{\"time\"}=? [ C<=step ]"
        prism_res = self.run_prism(prism_model, properties, step_range=step_range)
        steps = [self.__check_prism_result(step, model.logger) \
            for step in prism_res[2].split(',')]
        times = [self.__check_prism_result(time, model.logger) \
            for time in prism_res[8].split(',')]
        dtimes = [self.__check_prism_result(dtime, model.logger) \
            for dtime in prism_res[3].split(',')]
        res = {'steps':steps, 'time':times, 'downtime':dtimes}
        if show_plot:
            plt.figure()
            plt.plot(times, dtimes, "bo-")
            plt.xlabel('Time (s)')
            plt.ylabel('Downtime (s)')
            plt.title(f_name + ': ' + f_value)
            plt.grid(True)
            plt.show()
        return res

    def __run_prism_ss_tr(self, prism_model, tr=None, logger=None):
        """@brief Computes steady states"""
        old_dir = os.getcwd()
        os.chdir(self.prism_dir)
        #save prism model
        self.delete_temp_files()
        self.save(prism_model, file_name=self.prism_model_file)
        if tr:
            call_list = [self.prism_executable, \
            self.prism_model_file, \
            "-tr", str(tr), \
            "-exporttr", self.prism_ss_tr_file, \
            "-exportstates", self.prism_states_file, \
            "-timeout", str(self.timeout)]
        else:
            call_list = [self.prism_executable, \
            self.prism_model_file, \
            "-ss", "-exportss", self.prism_ss_tr_file, \
            "-exportstates", self.prism_states_file, \
            "-timeout", str(self.timeout)]
        if self.no_output:
            subprocess.call(call_list, stdout=subprocess.PIPE)
        else:
            subprocess.call(call_list)
        #read probabilities
        ss_tr_file = open(self.prism_ss_tr_file, 'r')
        # the nex line is beacuse of different outputs for ss and tr states of PRISM
        probs = [float(line.rstrip('\n').split('=')[-1]) for line in ss_tr_file]
        ss_tr_file.close()
        #read states
        states_file = open(self.prism_states_file)
        state_lines = [line.rstrip('\n') for line in states_file]
        states_file.close()
        os.chdir(old_dir)
        probs_sum = sum(probs)
        if probs_sum < 1.0:
            non_zero_probs = [prob for prob in probs if prob > 0]
            if logger:
                logger.warning("Summ of computed probabilities (" + str(probs_sum) + \
                    ") less than 1, " + str(non_zero_probs) + \
                    ", corrected, but might cause problems")
            for index, value in enumerate(probs):
                if value > 0:
                    probs[index] = probs[index] + 1.0 - probs_sum
                    break
        return [probs, state_lines]

    def __generate_ep_prism_command_repetitions(self, model, el_name, init_values):
        """@brief Computes steady states"""
        ep_prism_command = ""
        the_element = model.elements[el_name]
        if the_element['df_outputs']:
            if the_element['df_inputs']:
                for df_input, value in init_values.items():
                    model.data[df_input]['init'] = value
                    ep_prism_command += "(" + df_input + "=" + str(value) + ") & "
                ep_prism_command = ep_prism_command[:-3] + " -> "
            else:
                ep_prism_command += "(true) -> "

            prism_model = PRISM.generate_prism_model_for_repetitions(model, \
                el_name, init_values=init_values)
            [tr_probs, state_lines] = self.__run_prism_ss_tr(prism_model, \
                tr=the_element['repetitions'], logger=model.logger)
            #get vector of data names
            d_names = state_lines[0][1:-1].split(',')
            #get steady states with >0 probabilities
            states = [state.split(':')[1][1:-1].split(',') \
                for i, state in enumerate(state_lines) if i > 0]
            #aggregate for the df outputs only
            reduced_states = [[s_val for (d_name, s_val) in\
                zip(d_names, state) if d_name in the_element['df_outputs']]\
                for state in states]
            #reduce data names vector for the df outputs only
            reduced_d_names = [d_name for d_name in d_names if d_name in the_element['df_outputs']]
            if not reduced_d_names:
                model.logger.error(\
                    "Something went wrong! reduced_d_names empty in __generate_ep_prism_command_repetitions")
            tr_states = {}
            for (i, r_state) in enumerate(reduced_states):
                if tr_probs[i] > 0:
                    if ",".join(r_state) in tr_states:
                        tr_states[",".join(r_state)] += tr_probs[i]
                    else:
                        tr_states[",".join(r_state)] = tr_probs[i]
            values_names = PRISM.encode_string_values(model)
            for state, prob in tr_states.items():
                if not state.split(','):
                    model.logger.error("\
                        Something went wrong! state empty in __generate_ep_prism_command_repetitions")
                ep_prism_command += str(prob) + ":"
                for (d_name, s_val) in zip(reduced_d_names, state.split(',')):
                    if int(s_val) in values_names:
                        val = values_names[int(s_val)]
                    else:
                        val = s_val
                    ep_prism_command += "(" + d_name + "'=" + val + ") & "
                ep_prism_command = ep_prism_command[:-3] + " + "
            ep_prism_command = ep_prism_command[:-3] + ";"
        return ep_prism_command

    def __generate_ep_prism_command_sub_model(self, model, host_element, init_values):
        """@brief Computes steady states"""
        ep_prism_command = ""
        if host_element['df_outputs']:
            if host_element['df_inputs']:
                for df_input, value in init_values.items():
                    model.data[df_input]['init'] = value
                    ep_prism_command += "(" + df_input + "=" + str(value) + ") & "
                ep_prism_command = ep_prism_command[:-3] + " -> "
            else:
                ep_prism_command += "(true) -> "
            prism_model = PRISM.generate_prism_model(model, init_values=init_values)
            [ss_probs, state_lines] = self.__run_prism_ss_tr(prism_model, logger=model.logger)
            #get vector of data names
            d_names = state_lines[0][1:-1].split(',')
            #get steady states with >0 probabilities
            states = [state.split(':')[1][1:-1].split(',') \
                for i, state in enumerate(state_lines) if i > 0]
            #aggregate for the df outputs only
            reduced_states = [[s_val for (d_name, s_val) in\
                zip(d_names, state) if d_name in host_element['df_outputs']]\
                for state in states]
            #reduce data names vector for the df outputs only
            reduced_d_names = [d_name for d_name in d_names if d_name in host_element['df_outputs']]
            steady_states = {}
            for (i, r_state) in enumerate(reduced_states):
                if ss_probs[i] > 0:
                    if ",".join(r_state) in steady_states:
                        steady_states[",".join(r_state)] += ss_probs[i]
                    else:
                        steady_states[",".join(r_state)] = ss_probs[i]
            values_names = PRISM.encode_string_values(model)
            for state, prob in steady_states.items():
                ep_prism_command += str(prob) + ":"
                for (d_name, s_val) in zip(reduced_d_names, state.split(',')):
                    if int(s_val) in values_names:
                        val = values_names[int(s_val)]
                    else:
                        val = s_val
                    ep_prism_command += "(" + d_name + "'=" + val + ") & "
                ep_prism_command = ep_prism_command[:-3] + " + "
            ep_prism_command = ep_prism_command[:-3] + ";"
        return ep_prism_command

    def compute_repetitions(self, model, el_name):
        """@brief Computes repetitions for the elements"""
        # generate and return prism commands for the element
        ep_prism_commands = []
        the_element = model.elements[el_name]
        #get lists of all df input values
        values_vectors = [model.data[df_input]['values'] \
            for df_input in the_element['df_inputs']]
        #prepare models for all possible combinations of input values
        for init_values_vector in itertools.product(*values_vectors):
            init_values = dict(zip(the_element['df_inputs'], init_values_vector))
            #compute and generate prism commands
            model.logger.message('Computing repetitions with inputs: ' + str(init_values))
            ep_prism_command = self.__generate_ep_prism_command_repetitions(model, \
                el_name, init_values)
            if ep_prism_command:
                ep_prism_commands.append(ep_prism_command)
        return ep_prism_commands

    def compute_sub_models_and_repetitions(self, model, host_element=None):
        """@brief Computes nested models up to the top level"""
        # recursively ensure that all composite elements are computed
        for el_name, el_value in model.elements.items():
            if el_value['sub_model']:
                # generate prism commands istead of sub model
                model.logger.message('Computing sub model of element \"' + el_name + '\" ... ')
                model.elements[el_name]['ep_prism_commands'] = \
                    self.compute_sub_models_and_repetitions(\
                    el_value['sub_model'], el_value)
                # compute execution time of the compund element
                time = self.compute_execution_time(el_value['sub_model'])
                model.elements[el_name]['sub_model'] = None
                model.elements[el_name]['time'] = time
                model.logger.message('Computing sub model of element \"' + el_name + '\" finished ')
            if el_value['repetitions'] > 1:
                # generate prism commands istead of repetitions
                model.logger.message('Computing repetitions of element \"' + el_name + '\" ... ')
                model.elements[el_name]['ep_prism_commands'] = self.compute_repetitions(\
                    model, el_name)
                # compute execution time of the compund element
                model.elements[el_name]['time'] *= model.elements[el_name]['repetitions']
                model.elements[el_name]['repetitions'] = 1
                model.logger.message('Computing repetitions of element \"' + el_name + '\" finished ')
        # return top level flat prism model
        if not host_element:
            return model
        # generate and return prism commands for the host element
        ep_prism_commands = []
        #get lists of all df input values
        values_vectors = [model.data[df_input]['values'] \
            for df_input in host_element['df_inputs']]
        #prepare models for all possible combinations of input values
        for init_values_vector in itertools.product(*values_vectors):
            init_values = dict(zip(host_element['df_inputs'], init_values_vector))
            #compute and generate prism commands
            model.logger.message('Computing sub model with inputs: ' + str(init_values))
            ep_prism_command = self.__generate_ep_prism_command_sub_model(model, \
                host_element, init_values)
            if ep_prism_command:
                ep_prism_commands.append(ep_prism_command)
        return ep_prism_commands
