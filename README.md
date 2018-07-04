# Linux tools for Thunderbird mouse.
## About
Tools to adjust the LED color and mode of the Thunderbird mouse under linux. This should work on macOS/BSD but
I do not have a machine running these operating systems to test it on currently.
## WARNING
This program is still under development and requires root. I take no responsibility for any harm that may come to you, or your system if you run this. You may setup the following udev rule under /etc/udev/rules.d/50-Thunderbird.rules so that it does not require root access.
```
SUBSYSTEMS=="usb", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="1007", GROUP="plugdev", MODE="666"
```
## Usage
```
./Thunderbird-tools.py [OPTIONS] [frequency] [r] [g] [b]
```
For example to set the led to blue:
```
./Thunderbird-tools.py -s 0xA2 0x00 0x00 0xFF
```
or to set the led to neon:
```
./Thunderbird-tools.py -n 0xA2
```
## Options
```
-n    Neon mode
-r    Pulsate mode
-s    Solid mode
```

## Requirements
* Python2.7 and up
* Pyusb
