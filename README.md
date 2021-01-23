# cmd4_adrsir

[adrsirlib]: https://github.com/tokieng/adrsirlib
[homebridges-cmd4]: https://github.com/ztalbot2000/homebridge-cmd4

The cmd4_adrsir is to select and send ir data, written in Python 3.7(perhaps 3.0 or latar).

`cmd4_adrsir` launchs [adrsirlib][adrsirlib], just fit to value of state_cmd attribute of [homebridges-cmd4][homebridges-cmd4].

# Usage
Describe the path to `cmd_adrsir` stored in **state_cmd** attribute in `config.json` contained into homebridge.

An example for description is here:

**e.g.**
```
    {
        "type": "Lightbulb",
        "displayName": "BrightLight",
        "on": "FALSE",
        "brightness": 0,
        "colorTemperature": 0,
        "name": "BrightLight",
        "Manufacturer": "Panasonic",
        "Model": "Cmd4 model",
        "SerialNumber": "anatsuk1",
        "stateChangeResponseTime": 1,
        "state_cmd": "/var/lib/homebridge/cmd4_adrsir.py"
    },
```

# Port cmd4_adrsir to your environment

1. Describe config.json of your preference.
1. Port cmd4_adrsir.py to your environment.

The present both files are for my environment and preference.

## config.json

Describe the path to `cmd_adrsir` stored in **state_cmd** attribute in `config.json`

```
"state_cmd": "/var/lib/homebridge/cmd4_adrsir.py"
```

## cmd4_adrsir.py
Set environment dependent commands in below Variables.

|Variable|Description
|:-----------|:------------
|STATE_INTPRT|path to the node command
|STATE_SCRIPT|path to `State.js` file contained in Homebridges-cmd4
|IRCONTROL|path to `ircontrol` script file contained in adrsirlib

ircontrol is the python script to send and receive infrared data and it store infrared data in persistent storage.

**e.g.**

```python3:cmd4_adrsir.py
# homebridge-cmd4 state script on node.js
STATE_INTPRT = "node"
STATE_SCRIPT = "/var/lib/homebridge/Cmd4Scripts/State.js"
# adrsirlib script on python3
IRCONTROL = "/usr/local/etc/adrsirlib/ircontrol"
```

## Redesign send_irdata() function

### Function signature is here:

```python3:cmd4_adrsir.py
def send_irdata(device, action, next):
```
- device: value of "displayName" attribute. It is NOT "name".
- action: attribute in element of accessories attribute array.
- next: next device state of `action` attribute.

### Implementation

You should implement the following behavior for your preference and environment:
1. choose the name of infrared data of stored from the device states.
1. Set the name in `irdata` variable. 

Finally, this function send `irdata` as infrared data, move the device state to next.

**e.g.**
```python3:cmd4_adrsir.py
    if device == "BrightLight":

        if action == "On":
            bright = exec_state_stript("Get", device, "Brightness")
            irdata = select_light_name(next, bright, "brightlight")
        elif action == "Brightness":
            on = exec_state_stript("Get", device, "On")
            irdata = select_light_name(on, next, "brightlight")
```

# Thanks
## adrsirlib
@tokieng created the python script which great and helpful.

[Bit Trade One, LTD.](https://bit-trade-one.co.jp) provided useless scripts and no supports. 

But I am happy to have found adrsirlib now.

[tokieng's GitHub page is here.][adrsirlib]


## Homebridges-cmd4

@ztalbot2000 provide me better homebridge plugin.

I hope that ztalbot2000 provides documentations and examples of comebridges-cmd4 more.

[ztalbot2000's GitHub page is here.][Homebridges-cmd4]

# Environment

cmd4_adrsir is running but not limited with the followings.
- Python 3.7.3
- Homebridges-cmd4 3.0.7
- Homebridge 1.2.5
