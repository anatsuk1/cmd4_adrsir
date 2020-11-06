# cmd4_adrsir
A python script for [adrsirlib](https://github.com/tokieng/adrsirlib) and [Homebridges-cmd4](https://github.com/ztalbot2000/homebridge-cmd4).

# Usage
Write the path to the script as value of the state_cmd attribute in config.json that homebridge has.

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

You have to rewrite the script and config.json included into cmd4_adrsir to your environment.

# Port the script to your environment

## config.json
Add your accrssories to config.json.
Change config.json to your environment.

## cmd4_adrsir.py

Rewrite const value to your environment.

|value|Description
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
IRCONTROL = "/var/lib/homebridge/adrsir/ircontrol"
```

## Redesign select_irdata function

Rewrite handle event and action.

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
Better homebridge plugin but I did not find some documentations and examples.
