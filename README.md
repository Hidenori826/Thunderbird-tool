# Linux tool for the Pictek Thunderbird mouse.
## About
Tool to adjust the LED color and mode of the Picktek Thunderbird mouse for linux. This should work on other operating systems but I have not tested it.
## WARNING
This program is still under development and requires root. I take no responsibility for any harm that may come to you, or your system if you run this. You may setup the following udev rule under /etc/udev/rules.d/50-Thunderbird.rules so that it does not require root access.
```
SUBSYSTEMS=="usb", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="1007", GROUP="plugdev", MODE="666"
```
## Usage
```
./thunderbird.py [OPTIONS] POWER
```
For example to set the led to solid blue:
```
./thunderbird.py --solid --profile 0 --rgb 0 0 255 9
```
or to set the led to neon:
```
./thunderbird.py -n 9
```
## Options
```
-n    Neon mode
-b    Breath mode
-s    Solid mode
```

## Requirements
* Python2.7 and up
* Pyusb
