#!/usr/bin/env sh

echo "Start to install Infrasmacon."

echo "  Copying Infrasmacon to /var/opt/"
cp -R ../infrasmacon /var/opt

echo "  Changing Owner and Group of Infrasmacon directory"
chown -R pi:pi /var/opt/infrasmacon

echo "  Copying 'config.json' file to /var/lib/homebridge/"
cp ./config.json /var/lib/homebridge/

echo "  Replacing sensitive infomation in /var/lib/homebridge/config.json"
sed -i -e 's/DYSON-IP/XXX.XXX.XXX.XXX/g' /var/lib/homebridge/config.json
sed -i -e 's/DYSON-SERIALNUMBER/XXXXX-XXX-XX-XXXXXXXX-XXX/g' /var/lib/homebridge/config.json
sed -i -e 's/DYSON-PASSWORD/XXXXXXXXXXXXXXXX/g' /var/lib/homebridge/config.json

echo "Installing Infrasmacon is finished."
