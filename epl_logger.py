"""
Error Propagation Library V6.
Logging class for console messages, warnings, errors.
"""

from colorama import init
init()

class Logger(object):
    """@brief Logging class"""

    def __init__(self, out_widget=None):#, epl):
        """@brief Constructor"""
        self.out_widget = out_widget
        self.has_errors = False
        self.log = []

    def error(self, message):
        """@brief Error messaging"""
        self.has_errors = True
        c_error_color = '\033[91m'
        c_endc = '\033[0m'
        print(c_error_color + message + c_endc)
        if self.out_widget:
            w_error_color = "<font color=\"Red\">"
            w_endc = "</font>"
            self.out_widget.append(w_error_color + message + w_endc)
        entry = ['Error', message]
        self.log.append(entry)
        return entry

    def warning(self, message):
        """@brief Error messaging"""
        c_warning_color = '\033[93m'
        c_endc = '\033[0m'
        print(c_warning_color + message + c_endc)
        if self.out_widget:
            w_warning_color = "<font color=\"Yellow\">"
            w_endc = "</font>"
            self.out_widget.append(w_warning_color + message + w_endc)
        entry = ['Warning', message]
        self.log.append(entry)
        return entry

    def message(self, message):
        """@brief Messaging"""
        c_ok_color = '\033[96m'
        c_endc = '\033[0m'
        print(c_ok_color + message + c_endc)
        if self.out_widget:
            w_ok_color = "<font color=\"Aqua\">"
            w_endc = "</font>"
            self.out_widget.append(w_ok_color + message + w_endc)
        entry = ['OK', message]
        self.log.append(entry)
        return entry

    def save(self, file_name="model.log", \
            only_errors=False, only_warnings_and_errors=False):
        """saves log to gile"""
        model_file = open(file_name, 'w')
        for log_line in self.log:
            if only_errors:
                if log_line[0] == 'Error':
                    model_file.write(str(log_line)+"\n")
            elif only_warnings_and_errors:
                if (log_line[0] == 'Error') or (log_line[0] == 'Warning'):
                    model_file.write(str(log_line)+"\n")
            else:
                model_file.write(str(log_line)+"\n")
        model_file.close()

    def clear(self):
        """saves log to gile"""
        self.log = []
        self.has_errors = False
        return True
