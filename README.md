# DeviceJson #

Python script for interfacing serial weighing devices

### Compatible Devices ###

* PR1612
* X5 - to be included
* IP devices - to be included

### Setup ###

````
sudo cp deviceJson /etc/init.d/deviceJson
sudo chmod 755 /etc/init.d/deviceJson
sudo chown root:root /etc/init.d/deviceJson
sudo update-rc.d deviceJson defaults
sudo update-rc.d deviceJson enable
````
