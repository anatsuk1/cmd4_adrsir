#!/usr/bin/env python3

# Copyright (c) 2020, 2021, anatsuk1
# All rights reserved.
#
# BSD 2-Clause License

import subprocess
import sys
import time, datetime
import fcntl

# For debug
DEBUG = False

#
# Modify interpreter and script location
#
LOG_FILE = "/home/pi/log.txt"

# Lock for Processes
LOCK_FILE = "/var/lib/homebridge/process.lock"

# homebridge-cmd4 state script on node.js
STATE_INTPRT = "node"
STATE_SCRIPT = "/var/lib/homebridge/Cmd4Scripts/State.js"
# adrsirlib script on python3
IRCONTROL = "/usr/local/etc/adrsirlib/ircontrol"

#
# Implimentation of functions 
#
def exec_state_stript(direction, device, action, param=""):

    # Get the state of devices from homebridge-cmd4 state script.
    # Prepare argument to shift right for run script. 
    command = [STATE_INTPRT, STATE_SCRIPT, direction, device, action, param]

    result = subprocess.run(command, encoding="utf-8", stdout=subprocess.PIPE)
    current = result.stdout.strip()
    current = current.strip("\"");

    # for debug
    if DEBUG:
        with open(LOG_FILE, mode="a") as log:
            print("[{}] State Result {}: {}".format(datetime.datetime.now().timetz(),
                    command[2:], current), file=log)
    return current

def select_light_name(on_str, bright_str, name_prefix):

    irdata = None
    on_value = on_str.upper()
    bright = int(bright_str)

    # On atteribute is true
    if on_value == "TRUE":

        # Bright 100% ir data
        if bright == 100:
            irdata = name_prefix + "_full"

        # off ir data
        elif bright == 0:
            irdata = name_prefix + "_off"

        # Bright night ir data
        elif bright <= 20:
            irdata = name_prefix + "_night"

        # Bright xx%(prefered).
        # 20% < prefered bright < 100%
        else:
            irdata = name_prefix + "_preference"

    # On atteribute is false
    elif on_str == "FALSE":
        irdata = name_prefix + "_off"
    
    return irdata

def select_aircon_name(active_str, heater_cooler_str):

    irdata = None
    active = active_str.upper()
    heater_cooler = heater_cooler_str.upper()

    # INACTIVE
    if active == "INACTIVE":
        irdata = "aircon_off"
    # ACTIVE
    elif active == "ACTIVE":
        # AUTO, if INACTIVE or IDLE comes, perhaps cmd4 is in bug
        if heater_cooler == "AUTO" or heater_cooler == "INACTIVE" or heater_cooler ==  "IDLE":
            irdata = "aircon_off"
        # HEAT
        elif heater_cooler == "HEAT":
            irdata = "aircon_warm-22-auto"
        # COOL
        elif heater_cooler == "COOL":
            irdata = "aircon_cool-26-auto"

    return irdata

def send_irdata(device, action, next):

    irdata = None

    # Note: device is "displayName". It is NOT "name".
 
    if device == "BrightLight":

        if action == "On":
            bright = exec_state_stript("Get", device, "Brightness")
            irdata = select_light_name(next, bright, "brightlight")
        elif action == "Brightness":
            on = exec_state_stript("Get", device, "On")
            irdata = select_light_name(on, next, "brightlight")

    elif device == "DimLight":

        if action == "On":
            bright = exec_state_stript("Get", device, "Brightness")
            irdata = select_light_name(next, bright, "dimlight")
        elif action == "Brightness":
            on = exec_state_stript("Get", device, "On")
            irdata = select_light_name(on, next, "dimlight")

    elif device == "AirConditioner":

        if action == "Active":

            heater_cooler = exec_state_stript("Get", device, "TargetHeaterCoolerState")
            irdata = select_aircon_name(next, heater_cooler)

        elif action == "TargetHeaterCoolerState":
            active = exec_state_stript("Get", device, "Active")
            irdata = select_aircon_name(active, next)

    # Run ircontrol command like as "<location>/ircontrol <option> <ir data name>".
    # e.g. $ /usr/local/etc/adrsirlib/ircontrol send brightlight_preference
    if irdata is not None:
        subprocess.run([IRCONTROL, "send", irdata])

    if DEBUG:
        with open(LOG_FILE, mode="a") as log:
            print("[{}]IrCommand: {} {} {}".format(datetime.datetime.now().timetz(), 
                    IRCONTROL, "send", irdata), file=log)

def start_process(value):

    # for debug
    if DEBUG:
        with open(LOG_FILE, mode="a") as log:
            print("[{}]Cmd Argv: {}".format(datetime.datetime.now().timetz(),
                    value), file=log)

    # Depend on adrsirlib and homebridge-cmd4 state script.
    # ./ircontrol script with SEND command and stored ir data.

    # value[1]: "Set", "Get"
    # value[2]: is value of "displayName" attribute. It is NOT "name" attribute.
    #           "displayName" is attribute name on config.json in homebridge, defined by homebridge-cmd4.
    # value[3]: user choiced attribute with maybe upper case.
    # value[4]: only if value[1] is "Set", numeric value of value[3] attribute. overwise nothing.

    if value[1] == "Set":

        current = exec_state_stript(value[1], value[2], value[3], value[4])

        # Simulate current state, When set target state, set current state in the same time.
        if value[3] == "TargetHeaterCoolerState":
            if value[4].upper() != "AUTO":
                exec_state_stript(value[1], value[2], "CurrentHeaterCoolerState", value[4])

        # send ir data.
        send_irdata(value[2], value[3], value[4])



    elif value[1] == "Get":

        current = exec_state_stript(value[1], value[2], value[3], "dummy")

    print(current)

if __name__ == "__main__":

    # for debug
    if False:
        with open(LOG_FILE, mode="a") as log:
            print("[{}]sys.argv: {}".format(datetime.datetime.now().timetz(),
                    sys.argv), file=log)

    with open(LOCK_FILE, "r") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            start_process(sys.argv)
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN) 
