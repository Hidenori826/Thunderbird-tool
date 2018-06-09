import usb.core
import usb.util

IDVENDOR = 0x258a
IDPRODUCT = 0x1007
interface = 1


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


def usb_read(data):
    usb_write(data)
    ret = dev.ctrl_transfer(bmRequestType=0xA1, bRequest=0x1, wValue=0x0304, wIndex=0x0001, data_or_wLength=data,
                            timeout=1000)
    return ret


def set_color(colors, led_brightness):
    data = [0x04, 0x8A, 0x25, 0x07, 0x10, 0x30, 0x01, 0x80, 0x3C, 0x0A, 0x53, 0x49, 0x4E, 0x4F, 0x57, 0x45, 0x41, 0x4C,
            0x54, 0x48, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x0A, 0x47, 0x61, 0x6D, 0x65, 0x20, 0x4D, 0x6F, 0x75, 0x73, 0x65, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x15,
            0x80, 0x00, 0x04, 0x07, 0x0A, 0x0E, 0x10, 0x81, 0x81, 0x82, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x48, 0x02, 0x00] + [led_brightness] + [0x04, 0x00, 0x00] + colors + [0xFA, 0x03, 0x6A,
                                                                                                    0xFF, 0xFF, 0xFF,
                                                                                                    0x00, 0x00, 0x00,
                                                                                                    0xCB,
                                                                                                    0x34, 0x78, 0xFF,
                                                                                                    0xFF, 0x00, 0x00,
                                                                                                    0xFF, 0x00, 0x00,
                                                                                                    0xFF,
                                                                                                    0xFF, 0x00, 0x00,
                                                                                                    0xFF, 0xFF, 0x00,
                                                                                                    0xFF, 0xFF, 0xFF,
                                                                                                    0xFF,
                                                                                                    0x00, 0x00, 0x00,
                                                                                                    0x00, 0x00, 0x00,
                                                                                                    0x00, 0x00, 0x00]
    usb_write(data)