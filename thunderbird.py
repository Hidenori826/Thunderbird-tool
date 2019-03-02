#!/usr/bin/env python3
import argparse
import sys

import usb.core
import usb.util
import os.path


interface = 1
data = [0x04, 0x8A, 0x25, 0x07, 0x10, 0x30, 0x01, 0x80, 0x3C, 0x0A, 0x53, 0x49, 0x4E, 0x4F, 0x57, 0x45, 0x41, 0x4C,
        0x54, 0x48, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x0A, 0x47, 0x61, 0x6D, 0x65, 0x20, 0x4D, 0x6F, 0x75, 0x73, 0x65, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x15,
        0x80, 0x00, 0x04, 0x07, 0x0A, 0x0E, 0x10, 0x81, 0x81, 0x82, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x48, 0x02, 0x00, 0x48, 0x04, 0x00, 0x00, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00,
        0xFF, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0xFA, 0x03, 0x6A, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0xCB, 0x34,
        0x78, 0xFF, 0xFF, 0x00, 0x00, 0xFF, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0xFF, 0xFF, 0xFF,
        0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]


def open_usb():
    global dev

    dev = usb.core.find(idVendor=0x258a, idProduct=0x1007)
    if dev is None:
        raise ValueError("Device not found")
    if dev.is_kernel_driver_active(interface) is True:
        dev.detach_kernel_driver(interface)
        usb.util.claim_interface(dev, interface)


def close_usb():
    usb.util.release_interface(dev, interface)
    dev.attach_kernel_driver(interface)


def usb_write(data):
    dev.ctrl_transfer(bmRequestType=0x21, bRequest=0x9, wValue=0x0304, wIndex=0x0001, data_or_wLength=data,
                      timeout=1000)


def open_config():
    if not (os.path.isfile("thunderbird.conf")):
        color_file = open("thunderbird.conf", "w+")
        color_file.write("0 255 0 255 0 0 0 0 255 0 255 255 255 255 0 72 162 115")
        color_file.close()
    color_file = open("thunderbird.conf", "r+")

    return color_file


def set_mode(led_mode, led_frequency):
    config = open_config()
    if led_mode == "-s":
        data[93] = 0x28
    elif led_mode == "-b":
        data[93] = 0x22
    elif led_mode == "-n":
        data[93] = 0x44
    data[96] = led_frequency
    temp_config = str_to_list(config.read())
    temp_config[15] = led_frequency
    temp_config[16] = ord(led_mode[1])
    temp_config = list_to_str(temp_config, 17)
    config.seek(0,0)
    config.write(temp_config)
    config.close()


def set_color(led_brightness, color_profile, colors):
    current_colors = []
    config = open_config()
    line = config.read()

    current_colors = str_to_list(line)
    for color in range(3):
        current_colors[(color + (color_profile * 3))] = colors[color]
        color += 1
    data[96] = led_brightness
    data[100:115] = current_colors[0:15]

    current_colors = list_to_str(current_colors, 15)
    config.seek(0, 0)
    config.write(current_colors)
    config.close()
    usb_write(data)


def str_to_list(string):
    temp = []
    for i in string.split():
        if i.isdigit():
            temp.append(int(i))
    return temp


def list_to_str(list, index):
    return ' '.join(str(x) for x in list[0:index])


if __name__ == "__main__":
    open_usb()
    parser = argparse.ArgumentParser(description="Command line tool to modify mouse LED settings",
                                    usage="thunderbird.py [-h] [-s] [-b] [-n] [-p profile] [-r r g b] power")
    parser.add_argument("-s", "--solid", action="store_true",  help="Set mouse mode to solid")
    parser.add_argument("-b", "--breath", action="store_true",  help="Set mouse mode to breath")
    parser.add_argument("-n", "--neon", action="store_true",  help="Set mouse mode to neon")
    parser.add_argument("power", type=str, help="The brightness/speed of the mouse color setting")
    parser.add_argument("-p", "--profile", type=int, help="The profile of the mouse from 0-4", dest="profile", metavar='')
    parser.add_argument("-r", "--rgb", type=int, default=[], nargs=3, help="Color of the mouse to be set in decimal [r g b]", dest="rgb", metavar='')
    args = parser.parse_args()
    
    if args.rgb is not None and len(args.rgb) != 3 and (args.solid or args.breath):
        print("Please enter 3 values for rgb.")
        sys.exit()
    if not (args.solid or args.breath or args.neon):
        print("Please enter a mode.")
        sys.exit()

    if sys.argv[1] == "-s":
        set_color(int(args.power, 16), args.profile, args.rgb)
    else:
        set_mode(sys.argv[1], int(args.power, 16))
        usb_write(data)
    close_usb()
