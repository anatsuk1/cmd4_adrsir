#!/usr/bin/env python3

# Copyright (c) 2021, anatsuk1
# All rights reserved.
#
# BSD 2-Clause License

import sys
import json

from logger import Logger

class DeviceState:

    @classmethod
    def initialize(cls, config_name):
        cls.config_name = config_name

    def __init__(self, json_name, device):

        Logger.debug_print_trace(sys._getframe().f_code.co_name + ": {} {}", json_name, device)

        # use state only including device if loading json is failed.
        state = {device:{}}

        # load state from the state file.
        # add device dictionary in state dictionary if not exist
        try:
            with open(json_name, mode="r") as state_file:
                state = json.load(state_file)

            # add device dictionary if not exist
            state.setdefault(device, {})

        except (json.JSONDecodeError, FileNotFoundError) as error:
            Logger.debug_print_info(sys._getframe().f_code.co_name + " Loading JSON is failed: {}", error)

        Logger.debug_print_info(sys._getframe().f_code.co_name + " : {}", state)

        self.state = state
        self.json_name = json_name
        self.device = device

    def __del__ (self):
        # save(self)
        pass

    def save(self):

        Logger.debug_print_trace(sys._getframe().f_code.co_name + ":")

        with open(self.json_name, mode="w") as state_file:
            json.dump(self.state, state_file)

    def get_device(self):
        return self.device

    def get_state(self):
        return self.state[self.device]

    def get_value(self, attribute):

        

        # Get the initial value from config.json if never before set a value
        if attribute not in self.state[self.device].keys():
            with open(self.config_name, mode="r") as config:
                config_values = json.load(config)

            platforms = config_values["platforms"]
            for platform in platforms:
                if "Cmd4" == platform["platform"]:
                    accessories = platform["accessories"]
                    for accessory in accessories:
                        if self.device == accessory["displayName"]:
                            self.state[self.device][attribute] = accessory[attribute]
                            Logger.debug_print_info(sys._getframe().f_code.co_name + " initial value: {}", accessory[attribute])

        value = self.state[self.device][attribute]
        return value

    def set_value(self, attribute, value):

        Logger.debug_print_trace(sys._getframe().f_code.co_name + ": {} {}", attribute, value)

        self.state[self.device][attribute] = value

        # Simulate current state.
        # When set target state, set current state in the same time.
        if attribute == "targetHeaterCoolerState":
            if value != "AUTO":
                current_arribute = "currentHeaterCoolerState"
                self.state[self.device][current_arribute] = value
                Logger.debug_print_info(sys._getframe().f_code.co_name + " current state changed: {} {}", current_arribute, value)

if __name__ == "__main__":
    print("Import module.") 
