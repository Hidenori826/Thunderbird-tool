#!/usr/bin/env python3
import sys

import usb.core
import usb.util
import os.path

IDVENDOR = 0x258a
IDPRODUCT = 0x1007
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

    dev = usb.core.find(idVendor=IDVENDOR, idProduct=IDPRODUCT)
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
        color_file.write("0 255 0 255 0 0 0 0 255 0 255 255 255 255 0 72")
        color_file.close()
    color_file = open("thunderbird.conf", "r+")

    return color_file


def set_mode(led_mode, led_frequency):
    color_file = open_config()
    if led_mode == "-n":
        data[93] = 132
    elif led_mode == "-r":
        data[93] = 66
    elif led_mode == "-s":
        data[93] = 0x48
    data[96] = led_frequency
    color_file.close()


def set_color(led_brightness, color_profile, colors):
    current_colors = []
    color_file = open_config()
    line = color_file.read()

    for i in line.split():
        if i.isdigit():
            current_colors.append(int(i))

    for color in range(3):
        current_colors[(color + (color_profile * 3))] = colors[color]
        color += 1
    data[96] = led_brightness
    data[100:115] = current_colors[0:15]

    current_colors = ' '.join(str(x) for x in current_colors[0:15])
    color_file.seek(0, 0)
    color_file.write(current_colors)
    color_file.close()
    usb_write(data)


if __name__ == "__main__":
    open_usb()
    if len(sys.argv) < 2 or len(sys.argv) > 7:
        sys.exit("Usage: %s hex_value hex_value hex_value led_brightness profile")

    set_mode(sys.argv[1], int(sys.argv[2], 16))
    if sys.argv[1] != "-n":
        set_color(int(sys.argv[2], 16), int(sys.argv[3], 16), [int(sys.argv[4], 16), int(sys.argv[5], 16),
                                                               int(sys.argv[6], 16)])
    else:
        usb_write(data)
    close_usb()
