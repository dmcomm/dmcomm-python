# This file is part of the DMComm project by BladeSabre. License: MIT.

# Use this with a push-to-close button between GP3 and GND.
# Disables HID.
# Normally disables CIRCUITPY and console serial, and enables data serial,
# but leaves these in the default configuration if the button is pressed.

import board
import digitalio
import storage
import usb_cdc
import usb_hid

# HID is not used in this project
usb_hid.disable()

# Configure depending on button press
button = digitalio.DigitalInOut(board.GP3)
button.pull = digitalio.Pull.UP
if button.value:
	# button is not pressed
	storage.disable_usb_drive()
	usb_cdc.enable(console=False, data=True)
