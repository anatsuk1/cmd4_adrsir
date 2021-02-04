# cmd4_adrsir

[adrsirlib]: https://github.com/tokieng/adrsirlib
[homebridges-cmd4]: https://github.com/ztalbot2000/homebridge-cmd4

The cmd4_adrsir is to select and send ir data, written in Python 3.7(perhaps 3.5 or latar).

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
|IRCONTROL|path to `ircontrol` script file contained in adrsirlib

`ircontrol` is the python script to send and receive infrared data and it store infrared data in persistent storage.

**e.g.**

```python3:cmd4_adrsir.py
#
# Configure
#
# adrsirlib script on python3
IRCONTROL = "/usr/local/etc/adrsirlib/ircontrol"
```

## Redesign choose_data_name() function

### Function signature is here:

```python3:cmd4_adrsir.py
def choose_data_name(state, interaction, level):
```
- `state`:  is value of "displayName" attribute.  
It is NOT "name" attribute. "displayName" is attribute name on config.json in homebridge.
- `interaction`: is name of attribute which is bound for user interaction.  
First charactor of the name is UPPERCASE.
- `level`: is value of `interaction` attribute.

### Implementation

You should implement the following behavior for your preference and environment:
1. choose the name of infrared data of stored from the device states.
1. Set the name in `data_name` variable as return value. 

cmd4_adrsir sends infrared data bind for `data_name`, and moves the device state to `level`

**e.g.**
```python3:cmd4_adrsir.py
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
```

# Thanks
## adrsirlib
@tokieng created the python script which great and helpful.

[Bit Trade One, LTD.(ADRSIR design, manufacturing and sales)](https://bit-trade-one.co.jp) provided useless scripts and no supports. 

But I am happy to have found adrsirlib now.

[tokieng's GitHub page is here.][adrsirlib]


## Homebridges-cmd4

@ztalbot2000 provide me better homebridge plugin.

I hope that ztalbot2000 provides documentations and examples of Homebridges-cmd4 more.

[ztalbot2000's GitHub page is here.][Homebridges-cmd4]

# Environment

cmd4_adrsir is running but not limited with the followings.
- Python 3.7.3
- Homebridges-cmd4 3.0.15
- Homebridge 1.1.7
