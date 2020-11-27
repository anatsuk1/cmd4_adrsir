# cmd4_adrsir
cmd4_adrsir is a python script for [adrsirlib](https://github.com/tokieng/adrsirlib) and [Homebridges-cmd4](https://github.com/ztalbot2000/homebridge-cmd4).

# Usage
Set the path you stored this script to **state_cmd** attribute in config.json contained into homebridge.

**e.g.**
```
    {
        "type": "Fanv1",
        "displayName": "CeilingFan",
        "on": "FALSE",
        "name": "CeilingFan",
        "Manufacturer": "Unknown",
        "Model": "Cmd4 Model",
        "SerialNumber": "anatsuk1",
        "stateChangeResponseTime": 3,
        "state_cmd": "/var/lib/homebridge/cmd4_adrsir.py"
    },
```

# Port the script to your environment
You need to port this script and config.json included into cmd4_adrsir to your environment.
Both files, this script and config.json, are my preference.

## config.json
Add your accessories with your environment to config.json.

## cmd4_adrsir.py
Set the paths to customizable variable.

|variable|Description
|:-----------|:------------
|STATE_INTPRT|path to node command
|STATE_SCRIPT|path to State.js of Cmd4Script
|IRCONTROL|path to ircontrol script

**e.g.**

```python3:cmd4_adrsir.py
# homebridge-cmd4 state script on node.js
STATE_INTPRT = "node"
STATE_SCRIPT = "/var/lib/homebridge/Cmd4Scripts/State.js"
# adrsir script on python3
IRCONTROL = "/usr/local/etc/adrsirlib/ircontrol"
```

## Redesign send_irdata function

Redesign send_irdata function for your devices you join apple home network.
Determine events you dispatch, program event handler which controls your devices.

**e.g.**

```python3:cmd4_adrsir.py
if device == "CeilingFan":
    if action == "On":
        # On atteribute is associate true or false
        irdata = "ceiling_fan_power"
```

# Thanks
## adrsirlib : https://github.com/tokieng/adrsirlib
Great and helpful python script. 

I have a trouble. Provided useless official scripts and no support. 

But I found adrsirlib and am happy.

## Homebridges-cmd4 : https://github.com/ztalbot2000/homebridge-cmd4
Better homebridge plugin, I want more documentations and examples.
