# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2025 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_usb_host_mouse`
================================================================================

Helper class that encapsulates the objects needed for user code to interact with
a USB mouse, draw a visible cursor, and determine when buttons are pressed.


* Author(s): Tim Cocks

Implementation Notes
--------------------

**Hardware:**

* `USB Wired Mouse - Two Buttons plus Wheel <https://www.adafruit.com/product/2025>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads


# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

import array
from traceback import print_exception

import adafruit_usb_host_descriptors
import supervisor
import usb
from displayio import OnDiskBitmap, TileGrid

__version__ = "1.5.1"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_USB_Host_Mouse.git"

BUTTONS = ["left", "right", "middle"]
DEFAULT_CURSOR = "/".join(__file__.split("/")[:-1]) + "/mouse_cursor.bmp"


def find_and_init_boot_mouse(cursor_image=DEFAULT_CURSOR):  # noqa: PLR0912
    """
    Scan for an attached boot mouse connected via USB host.
    If one is found initialize an instance of :class:`BootMouse` class
    and return it.

    :param cursor_image: Provide the absolute path to the desired cursor bitmap image. If set as
      `None`, the :class:`BootMouse` instance will not control a :class:`displayio.TileGrid` object.
    :return: The :class:`BootMouse` instance or None if no mouse was found.
    """
    mouse_interface_index, mouse_endpoint_address = None, None
    mouse_device = None

    # scan for connected USB device and loop over any found
    print("scanning usb")
    for device in usb.core.find(find_all=True):
        # print device info
        try:
            try:
                print(f"{device.idVendor:04x}:{device.idProduct:04x}")
            except usb.core.USBError as e:
                print_exception(e, e, None)
            try:
                print(device.manufacturer, device.product)
            except usb.core.USBError as e:
                print_exception(e, e, None)
            print()
            config_descriptor = adafruit_usb_host_descriptors.get_configuration_descriptor(
                device, 0
            )
            print(config_descriptor)

            _possible_interface_index, _possible_endpoint_address = (
                adafruit_usb_host_descriptors.find_boot_mouse_endpoint(device)
            )
            if _possible_interface_index is not None and _possible_endpoint_address is not None:
                mouse_device = device
                mouse_interface_index = _possible_interface_index
                mouse_endpoint_address = _possible_endpoint_address
                print(
                    f"mouse interface: {mouse_interface_index} "
                    + f"endpoint_address: {hex(mouse_endpoint_address)}"
                )
                break
            print("was not a boot mouse")
        except usb.core.USBError as e:
            print_exception(e, e, None)

    mouse_was_attached = None
    if mouse_device is not None:
        # detach the kernel driver if needed
        if mouse_device.is_kernel_driver_active(0):
            mouse_was_attached = True
            mouse_device.detach_kernel_driver(0)
        else:
            mouse_was_attached = False

        # set configuration on the mouse so we can use it
        mouse_device.set_configuration()

        # load the mouse cursor bitmap
        if isinstance(cursor_image, str):
            mouse_bmp = OnDiskBitmap(cursor_image)

            # make the background pink pixels transparent
            mouse_bmp.pixel_shader.make_transparent(0)

            # create a TileGrid for the mouse, using its bitmap and pixel_shader
            mouse_tg = TileGrid(mouse_bmp, pixel_shader=mouse_bmp.pixel_shader)

        else:
            mouse_tg = None

        return BootMouse(mouse_device, mouse_endpoint_address, mouse_was_attached, mouse_tg)

    # if no mouse found
    return None


class BootMouse:
    """
    Helpler class that encapsulates the objects needed to interact with a boot
    mouse, show a visible cursor on the display, and determine when buttons
    were pressed.

    :param device: The usb device instance for the mouse
    :param endpoint_address: The address of the mouse endpoint
    :param was_attached: Whether the usb device was attached to the kernel
    :param tilegrid: The TileGrid that holds the visible mouse cursor
    :param scale: The scale of the group that the Mouse TileGrid will be put into.
      Needed in order to properly clamp the mouse to the display bounds
    """

    def __init__(self, device, endpoint_address, was_attached, tilegrid=None, scale=1):  # noqa: PLR0913, too many args
        self.device = device

        self.tilegrid = tilegrid
        """TileGrid containing the Mouse cursor graphic."""

        self.endpoint = endpoint_address
        self.buffer = array.array("b", [0] * 4)
        self.was_attached = was_attached

        self.scale = scale
        """The scale of the group that the Mouse TileGrid will be put into.
        Needed in order to properly clamp the mouse to the display bounds."""

        self.sensitivity = 1
        """The sensitivity of the mouse cursor. Larger values will make
        the mouse cursor move slower relative to physical mouse movement. Default is 1."""

        self.pressed_btns = []
        """List of buttons currently pressed (one or more of "left", "right", "middle")
        If there's no new mouse data (nothing changes) this property can be checked to see
        which buttons are currently pressed."""

        if tilegrid is not None:
            self.display_size = (
                supervisor.runtime.display.width,
                supervisor.runtime.display.height,
            )
            self.tilegrid.x, self.tilegrid.y = (
                x // 2 for x in self.display_size
            )  # center cursor in display
        else:
            self._x, self._y = 0, 0

    @property
    def x(self) -> int:
        """
        The x coordinate of the mouse cursor
        """
        return self.tilegrid.x if self.tilegrid else self._x

    @x.setter
    def x(self, new_x: int) -> None:
        if self.tilegrid:
            self.tilegrid.x = new_x
        else:
            self._x = new_x

    @property
    def y(self) -> int:
        """
        The y coordinate of the mouse cursor
        """
        return self.tilegrid.y if self.tilegrid else self._y

    @y.setter
    def y(self, new_y: int) -> None:
        if self.tilegrid:
            self.tilegrid.y = new_y
        else:
            self._y = new_y

    def release(self):
        """
        Release the mouse cursor and re-attach it to the kernel
        if it was attached previously.
        """
        if self.was_attached and not self.device.is_kernel_driver_active(0):
            self.device.attach_kernel_driver(0)

    def update(self):
        """
        Read data from the USB mouse and update the location of the visible cursor
        and check if any buttons are pressed.

        :return: a tuple containing one or more of the strings "left", "right", "middle"
          indicating which buttons are pressed. If no buttons are pressed, the tuple will be empty.
          If a error occurred while trying to read from the usb device, `None` will be returned.
        """
        try:
            # attempt to read data from the mouse
            # 20ms timeout, so we don't block long if there
            # is no data
            count = self.device.read(self.endpoint, self.buffer, timeout=20)  # noqa: F841, var assigned but not used
        except usb.core.USBTimeoutError:
            # skip the rest if there is no data
            return None
        except usb.core.USBError:
            return None

        # update the mouse x and y coordinates
        # based on the delta values read from the mouse
        dx, dy = self.buffer[1:3]
        dx = int(round((dx / self.sensitivity), 0))
        dy = int(round((dy / self.sensitivity), 0))
        if self.tilegrid:
            self.tilegrid.x = max(
                0, min((self.display_size[0] // self.scale) - 1, self.tilegrid.x + dx)
            )
            self.tilegrid.y = max(
                0, min((self.display_size[1] // self.scale) - 1, self.tilegrid.y + dy)
            )
        else:
            self._x += dx
            self._y += dy

        self.pressed_btns = []
        for i, button in enumerate(BUTTONS):
            # check if each button is pressed using bitwise AND shifted
            # to the appropriate index for this button
            if self.buffer[0] & (1 << i) != 0:
                # append the button name to the string to show if
                # it is being clicked.
                self.pressed_btns.append(button)

        return tuple(self.pressed_btns)
