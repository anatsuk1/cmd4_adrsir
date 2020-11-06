#!/usr/bin/env python3

# Copyright (c) 2020, anatsuk1
# All rights reserved.
#
# BSD 2-Clause License

import subprocess
import sys
import time, datetime
import fcntl

#
# Modify interpreter and script location
#
DEBUG = False
LOG_FILE = "/home/pi/log.txt"

# Lock for Processes
LOCK_FILE = "/var/lib/homebridge/process.lock"

# homebridge-cmd4 state script on node.js
STATE_INTPRT = "node"
STATE_SCRIPT = "/var/lib/homebridge/Cmd4Scripts/State.js"
# adrsir script on python3
IRCONTROL = "/var/lib/homebridge/adrsir/ircontrol"

#
# Implimentation of functions 
#
def exec_state_stript(direction, device, action, param=""):
    # Get the state of devices from homebridge-cmd4 state script.
    # Prepare argument to shift right for run script. 
    command = [STATE_INTPRT, STATE_SCRIPT, direction, device, action, param]

    result = subprocess.run(command, encoding="utf-8", stdout=subprocess.PIPE)
    current = result.stdout.strip()

    # for debug
    if DEBUG:
        with open(LOG_FILE, mode="a") as log:
            print("[{}]Script Result {}: {}".format(datetime.datetime.now().timetz(),
                    command[2:], current), file=log)
    return current

def select_light_name(on, bright, name_prefix):

    irdata = None
    bright_int = int(bright)

    # On atteribute is true
    if on == "true":

        # Bright 100% ir data
        if bright_int == 100:
            irdata = name_prefix + "_full"

        # off ir data
        elif bright_int == 0:
            irdata = name_prefix + "_off"

        # Bright xx%(prefered) ir data
        elif bright_int <= 20:
            irdata = name_prefix + "_night"
        else:
            irdata = name_prefix + "_preference"

    # On atteribute is false
    elif on == "false":
        irdata = name_prefix + "_off"
    
    return irdata

def send_irdata(device, action, next):

    irdata = None

    # Note: device is "displayName". It is NOT "name".
    if device == "CeilingFan":
        if action == "On":
            # On atteribute is associate true or false
            irdata = "ceiling_fan_power"
 
    elif device == "BrightLight":

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

    # Run ircontrol command like as "<location>/ircontrol send ceiling_fan_power".
    if irdata is not None:
        if DEBUG:
            with open(LOG_FILE, mode="a") as log:
                print("[{}] IrCommand: {} {} {}".format(datetime.datetime.now().timetz(), 
                        IRCONTROL, "send", irdata), file=log)
        subprocess.run([IRCONTROL, "send", irdata])


def start_process(value):

    # for debug
    if DEBUG:
        with open(LOG_FILE, mode="a") as log:
            print("[{}]start with sys.argv: {}".format(datetime.datetime.now().timetz(),
                    value), file=log)

    # Depend on adrsirlib and homebridge-cmd4 state script.
    # ./ircontrol script with SEND command and stored ir data.

    # value[1]: "Set", "Get"
    # value[2]: is value of "displayName" attribute. It is NOT "name" attribute.
    #           "displayName" is attribute name on config.json in homebridge, defined by homebridge-cmd4.
    # value[3]: user choiced attribute with maybe upper case.
    # value[4]: only if value[1] is "Set", numeric value of value[3] attribute. overwise nothing.

    if value[1] == "Set":
        send_irdata(value[2], value[3], value[4])

    param = value[4] if len(value) > 4 else ""
    current = exec_state_stript(value[1], value[2], value[3], param)
    print(current)

if __name__ == "__main__":

    # for debug
    if DEBUG:
        with open(LOG_FILE, mode="a") as log:
            print("[{}]sys.argv: {}".format(datetime.datetime.now().timetz(),
                    sys.argv), file=log)

    with open(LOCK_FILE, "r") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            start_process(sys.argv)
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN) 
