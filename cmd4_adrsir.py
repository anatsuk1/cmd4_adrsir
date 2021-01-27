#!/usr/bin/env python3

# Copyright (c) 2020, 2021, anatsuk1
# All rights reserved.
#
# BSD 2-Clause License

import os
import sys
import time
import subprocess
import fcntl

from logger import Logger
from device_state import DeviceState
#
# Modify script location
#
# adrsirlib script on python3
IRCONTROL = "/usr/local/etc/adrsirlib/ircontrol"

# For debug
LOG_LEVEL = Logger.OFF
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
# See more infomation read config.json.
CONFIG_JSON_FILE = DIRNAME + "/config.json"

#
# Implimentation of class
#


def select_light_name(on_str, bright_str, name_prefix):

    Logger.debug_print_trace(sys._getframe().f_code.co_name + ": {}, {}, {}", on_str, bright_str, name_prefix)

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

    Logger.debug_print_trace(sys._getframe().f_code.co_name + ": {}, {}", active_str, heater_cooler_str)

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

    Logger.debug_print_trace(sys._getframe().f_code.co_name + ": {}, {}, {}", state, interaction, level)

    data_name = None

    # Note: device is "displayName". It is NOT "name".
    device = state.get_device()

    if device == "BrightLight" or \
            device == "DimLight":

        # current device state
        on = state.get_value("on")
        bright = state.get_value("brightness")
        next_on = on
        next_bright = bright

        # next device state
        if interaction == "on":
            next_on = level
        elif interaction == "brightness":
            next_bright = level

        if on != next_on or bright != next_bright:
            # design that data name constains only lower device name.
            lower_device = device.lower()
            data_name = select_light_name(next_on, next_bright, lower_device)

    elif device == "AirConditioner":

        active = state.get_value("active")
        heater_cooler = state.get_value("targetHeaterCoolerState")
        next_active = active
        next_heater_cooler = heater_cooler

        if interaction == "active":
            next_active = level
        elif interaction == "targetHeaterCoolerState":
            next_heater_cooler = level

        if active != next_active or heater_cooler != next_heater_cooler:
            data_name = select_aircon_name(next_active, next_heater_cooler)

    return data_name


def send_infrared_data(data_name):

    # launch ircontrol command like as "<location>/ircontrol <option> <infrared data name>".
    # e.g. $ /usr/local/etc/adrsirlib/ircontrol send brightlight_preference
    if data_name is not None:
        subprocess.run([IRCONTROL, "send", data_name])
        # for sending next, waiting 300 ms after sending infrared data
        time.sleep(0.3)

    Logger.debug_print_info("IRCONTROL: {} {} {}", IRCONTROL, "send", data_name)


def start_process(value):

    Logger.debug_print_info(sys._getframe().f_code.co_name + " IN: {}", value)

    # Depend on adrsirlib and the specification required on state_cmd of homebridge-cmd4.
    # calling ./ircontrol contained in adrsirlib, see more comments on send_infrared_data().

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

    # put the level of interaction to stdout
    # Cmd4 retrives the level from stdout
    print(result)

    Logger.debug_print_info(sys._getframe().f_code.co_name + " OUT: {}", result)

if __name__ == "__main__":

    Logger.initialize(LOG_FILE, LOG_LEVEL)
    DeviceState.initialize(CONFIG_JSON_FILE)

    # for debug
    if False:
        Logger.debug_print_info("Start with: {}", sys.argv)

    with open(LOCK_FILE, "r") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            start_process(sys.argv)
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN) 
