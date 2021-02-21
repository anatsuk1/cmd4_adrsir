#!/usr/bin/env sh

echo "Start to install InfraredRemocon."

echo "  Copying InfraredRemocon to /usr/local/"
cp -R ../infrared-remocon /usr/local

echo "  Changing Owner and Group of InfraredRemocon directory"
chown -R pi:pi /usr/local/infrared-remocon

echo "  Copying 'config.json' file to /var/lib/homebridge/"
cp ./config.json /var/lib/homebridge/

echo "  Replacing sensitive infomation in /var/lib/homebridge/config.json"
sed -i -e 's/DYSON-IP/XXX.XXX.XXX.XXX/g' /var/lib/homebridge/config.json
sed -i -e 's/DYSON-SERIALNUMBER/XXXXX-XXX-XX-XXXXXXXX-XXX/g' /var/lib/homebridge/config.json
sed -i -e 's/DYSON-PASSWORD/XXXXXXXXXXXXXXXX/g' /var/lib/homebridge/config.json

echo "Installing InfraredRemocon is finished."
