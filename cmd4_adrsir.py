#!/usr/bin/env python3

# Copyright (c) 2020, 2021, anatsuk1
# All rights reserved.
#
# BSD 2-Clause License

import os
import sys
import time, datetime
import subprocess
import fcntl
import json

#
# Modify script location
#
# adrsirlib script on python3
IRCONTROL = "/usr/local/etc/adrsirlib/ircontrol"

# For debug
DEBUG = False
LOG_FILE = "/home/pi/log.txt"

# The directory of this script stored.
DIRNAME = os.path.dirname(__file__)

# Persistant States of devices.
STATE_FILE = DIRNAME + "/state.json"

# Lock for Processes
LOCK_FILE = DIRNAME + "/process.lock"

# read config.json for get default value.
# config.json must contain "platforms" attribute.
# "platforms" must contain "platform" attribute with "Cmd4" as `"platform": "Cmd4"`.
# See config.json commited with this script.
CONFIG_JSON_FILE = DIRNAME + "/config.json"

#
# Implimentation of class
#
class DeviceState:

    def __init__(self, file_name, device):

        # use state including device if loading json is failed
        state = {device:{}}

        # load state from the state file.
        # create device dictionary in state dictionary if not exist
        try:
            with open(file_name, mode="r") as state_file:
                state = json.load(state_file)

            # add device entry if not exist
            state.setdefault(device, {})

        except (json.JSONDecodeError, FileNotFoundError) as error:
            debug_print(sys._getframe().f_code.co_name + " Failed JSON load : {}", error)

        debug_print(sys._getframe().f_code.co_name + " : {}", state)

        self.state = state
        self.file_name = file_name
        self.device = device

    def __del__ (self):
        # save(self)
        pass

    def save(self):
        with open(self.file_name, mode="w") as state_file:
            json.dump(self.state, state_file)

    def get_device(self):
        return self.device

    def get_state(self):
        return self.state[self.device]

    def get_value(self, attribute):

        # Get default the value from config.json
        if attribute not in self.state[self.device].keys():
            with open(CONFIG_JSON_FILE, mode="r") as config:
                config_values = json.load(config)

            platforms = config_values["platforms"]
            for platform in platforms:
                if "Cmd4" == platform["platform"]:
                    accessories = platform["accessories"]
                    for accessory in accessories:
                        if self.device == accessory["displayName"]:
                            self.state[self.device][attribute] = accessory[attribute]
                            debug_print(sys._getframe().f_code.co_name + " initial value: {}", accessory[attribute])

        value = self.state[self.device][attribute]

        return value

    def set_value(self, attribute, value):

        debug_print(sys._getframe().f_code.co_name + ": {} {}", attribute, value)

        self.state[self.device][attribute] = value

#
# Implimentation of functions 
#
# for debug
def debug_print(formatted_string, *args):

    if DEBUG:
        with open(LOG_FILE, mode="a") as log:
            # additional date header
            header = "[{}]".format(datetime.datetime.now().timetz())
            body = formatted_string.format(*args)
            print(header + body, file=log)

def select_light_name(on_str, bright_str, name_prefix):

    debug_print(sys._getframe().f_code.co_name + ": {}, {}, {}", on_str, bright_str, name_prefix)

    light_name = None
    on = on_str.upper() # to make sure calling upper()
    bright = int(bright_str)

    # On atteribute is true
    if on == "TRUE":

        # Bright 100% ir data
        if bright == 100:
            light_name = name_prefix + "_full"

        # off ir data
        elif bright == 0:
            light_name = name_prefix + "_off"

        # Bright night ir data
        elif bright <= 20:
            light_name = name_prefix + "_night"

        # Bright xx%(prefered).
        # 20% < prefered bright < 100%
        else:
            light_name = name_prefix + "_preference"

    # On atteribute is false
    elif on == "FALSE":
        light_name = name_prefix + "_off"
    
    return light_name

def select_aircon_name(active_str, heater_cooler_str):

    debug_print(sys._getframe().f_code.co_name + ": {}, {}", active_str, heater_cooler_str)

    aircon_name = None
    active = active_str.upper() # to make sure calling upper()
    heater_cooler = heater_cooler_str.upper() #  to make sure calling upper()

    # INACTIVE
    if active == "INACTIVE":
        aircon_name = "aircon_off"
    # ACTIVE
    elif active == "ACTIVE":
        # AUTO, if INACTIVE or IDLE comes, perhaps cmd4 is in bug
        if heater_cooler == "AUTO" or \
                heater_cooler == "INACTIVE" or \
                heater_cooler == "IDLE":
            aircon_name = "aircon_off"
        # HEAT
        elif heater_cooler == "HEAT":
            aircon_name = "aircon_warm-22-auto"
        # COOL
        elif heater_cooler == "COOL":
            aircon_name = "aircon_cool-26-auto"

    return aircon_name

def choose_data_name(state, interaction, level):

    debug_print(sys._getframe().f_code.co_name + ": {}, {}, {}", state, interaction, level)

    data_name = None

    # Note: device is "displayName". It is NOT "name".
    device = state.get_device()

    if device == "BrightLight" or \
            device == "DimLight":

        # next device state
        on = state.get_value("on")
        bright = state.get_value("brightness")

        if interaction == "on":
            on = level
        elif interaction == "brightness":
            bright = level

        # design start filename with lower device name.
        lower_device = device.lower()

        data_name = select_light_name(on, bright, lower_device)

    elif device == "AirConditioner":

        active = state.get_value("active")
        heater_cooler = state.get_value("targetHeaterCoolerState")

        if interaction == "active":
            active = level
        elif interaction == "targetHeaterCoolerState":
            heater_cooler = level

        data_name = select_aircon_name(active, heater_cooler)

    return data_name

def send_infrared_data(data_name):

    # Run ircontrol command like as "<location>/ircontrol <option> <ir data name>".
    # e.g. $ /usr/local/etc/adrsirlib/ircontrol send brightlight_preference
    if data_name is not None:
        subprocess.run([IRCONTROL, "send", data_name])

    debug_print("IRCONTROL: {} {} {}", IRCONTROL, "send", data_name)

def start_process(value):

    debug_print(sys._getframe().f_code.co_name + ": {}", value)

    # Depend on adrsirlib and homebridge-cmd4 state script.
    # ./ircontrol script with SEND command and stored ir data.

    # value[1]: is "Set" or "Get".
    # value[2]: is value of "displayName" attribute. It is NOT "name" attribute.
    #           "displayName" is attribute name on config.json in homebridge.
    #           homebridge-cmd4 use "displayName" in wrong.
    # value[3]: is name of attribute which is bound to user interaction.
    #           First charactor of the name is UPPERCASE.
    #           homebridge-cmd4 converts the character to uppercase in wrong.
    # value[4]: is value of value[3] attribute if value[1] is "Set", otherwise nothing.
    direction = value[1]
    device = value[2]
    interaction = value[3][0].lower() + value[3][1:]
    level = value[4] if direction == "Set" else None

    state = DeviceState(STATE_FILE, device)

    if direction == "Set":

        # choose infrared data.
        name = choose_data_name(state, interaction, level)

        debug_print(sys._getframe().f_code.co_name + ": check name: {}, state: {}", name, state.get_state())

        # send infrared data.
        send_infrared_data(name)

        # store state as value of attribute
        state.set_value(interaction, level)

        # Simulate current state.
        # When set target state, set current state in the same time.
        if interaction == "targetHeaterCoolerState":
            if level != "AUTO":
                state.set_value("currentHeaterCoolerState", level)

    result = state.get_value(interaction)

    # save state in persistent storage.
    state.save()

    # the level of interaction to stdout
    # CMD4 recieves the level from stdout
    print(result)

    debug_print("End with: {}", result)

if __name__ == "__main__":

    # for debug
    if False:
        debug_print("Start with: {}", sys.argv)

    with open(LOCK_FILE, "r") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            start_process(sys.argv)
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN) 
