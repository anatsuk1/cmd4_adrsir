#!/usr/bin/env bash

echo "Copy cmd4_adrsir.py to /var/lib/homebridge/"
cp ./cmd4_adrsir.py /var/lib/homebridge/

echo "Copy config.json to /var/lib/homebridge/"
cp ./config.json /var/lib/homebridge/

echo "Replace sensitive infomation /var/lib/homebridge/config.json"
sed -i -e 's/DYSON-IP/XXX.XXX.XXX.XXX/g' /var/lib/homebridge/config.json
sed -i -e 's/DYSON-SERIALNUMBER/XXXXX-XXX-XX-XXXXXXXX-XXX/g' /var/lib/homebridge/config.json
sed -i -e 's/DYSON-PASSWORD/XXXXXXXXXXXXXXXX/g' /var/lib/homebridge/config.json

echo "Finished!"
