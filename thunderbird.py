#!/usr/bin/env python3
import argparse
import pickle
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
    if not (os.path.isfile("thunderbird.pkl")):
        default_config = [0, 255, 0, 255, 0, 0, 0, 0, 255, 0, 255, 255, 255, 255, 0, 72, 162, 115]
        write_config(default_config)
    pickle_file = open("thunderbird.pkl", "rb")
    config = pickle.load(pickle_file)
    pickle_file.close()
    return config


def write_config(config):
    pickle_file = open("thunderbird.pkl", "wb")
    pickle.dump(config, pickle_file)
    pickle_file.close()


def set_mode(led_mode, led_power, color=[], profile=0):
    config = open_config()
    led_power = (18 + (16 * led_power))
    # Set mouse mode to solid
    if led_mode == 1:
        set_color(profile, color)
        data[93] = 0x28
        config[16] = 0x28
    # Set mouse mode to breath
    elif led_mode == 2:
        set_color(profile, color)
        data[93] = 0x22
        config[16] = 0x22
    # Set mouse mode to neon
    elif led_mode == 3:
        data[93] = 0x44
        config[16] = 0x44
    config[15] = led_power
    data[96] = led_power
    write_config(config)
    usb_write(data)


def set_color(profile, colors):
    config = open_config()
    for i, color in enumerate(colors):
        config[(i + (profile * 3))] = color
    data[100:115] = config[0:15]
    write_config(config)
    usb_write(data)


if __name__ == "__main__":
    open_usb()
    parser = argparse.ArgumentParser(description="Command line tool to modify mouse LED settings",
                                    usage="thunderbird.py [-h] [-s] [-b] [-n] [-p profile] [-r r g b] power")
    parser.add_argument("-s", "--solid", action="store_true", help="Set mouse mode to solid")
    parser.add_argument("-b", "--breath", action="store_true",  help="Set mouse mode to breath")
    parser.add_argument("-n", "--neon", action="store_true",  help="Set mouse mode to neon")
    parser.add_argument("power", type=int, help="The brightness/speed of the mouse color setting from 0-9")
    parser.add_argument("-p", "--profile", type=int, help="The profile of the mouse from 0-4", dest="profile", metavar='')
    parser.add_argument("-r", "--rgb", type=int, default=[], nargs=3, help="Color of the mouse to be set in decimal [r g b]", dest="rgb", metavar='')
    args = parser.parse_args()
    
    if args.rgb is not None and len(args.rgb) != 3 and (args.solid or args.breath):
        print("Please enter 3 values for rgb.")
        sys.exit()
    if not (args.solid or args.breath or args.neon):
        print("Please enter a mode.")
        sys.exit()

    if args.solid == True:
        set_mode(1, args.power, args.rgb, args.profile)
    elif args.breath == True:
        set_mode(2, args.power, args.rgb, args.profile)
    elif args.neon == True:
        set_mode(3, args.power)
    close_usb()