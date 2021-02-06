#!/usr/bin/env python3

# Copyright (c) 2021, anatsuk1
# All rights reserved.
#
# BSD 2-Clause License

import time, datetime

class Logger:

    # public final parameters
    OFF = 0
    ERROR = 1
    WARN = 2
    INFO = 3
    TRACE = 4

    @classmethod
    def initialize(cls, file_name, log_level):
        cls.file_name = file_name
        cls.log_level = log_level

    @classmethod
    def debug_print(cls, level, formatted_string, *args):

        if level > cls.log_level:
            return

        with open(cls.file_name, mode="a") as log:
            # additional date header
            header = "[{}][{}]".format(datetime.datetime.now().timetz(), level)
            body = formatted_string.format(*args)
            print(header + body, file=log)

    @classmethod
    def debug_print_error(cls, formatted_string, *args):
        cls.debug_print(cls.ERROR, formatted_string, *args)

    @classmethod
    def debug_print_info(cls, formatted_string, *args):
        cls.debug_print(cls.INFO, formatted_string, *args)

    @classmethod
    def debug_print_trace(cls, formatted_string, *args):
        cls.debug_print(cls.TRACE, formatted_string, *args)

if __name__ == "__main__":
    print("Import module.") 
