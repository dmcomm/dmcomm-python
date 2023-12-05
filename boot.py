# This file is part of the DMComm project by BladeSabre. License: MIT.

# Use this with a push-to-close button between the assigned pin and GND.
# Disables HID and status bar.
# Makes CIRCUITPY read-only, unless the button is held on startup.

import board
import digitalio
import storage
import supervisor
import usb_hid

import board_config

# HID is not used in this project
usb_hid.disable()

try:
	supervisor.status_bar.console = False
	supervisor.status_bar.display = False
except:
	print("Status bar API not present")

button_pin = board_config.ui_pins["button_c"]

# Configure depending on button press
protect = False
if button_pin is not None:
	# push-to-close button between button_pin and GND
	button = digitalio.DigitalInOut(button_pin)
	button.pull = digitalio.Pull.UP
	if button.value:
		print("Button was not pressed")
		protect = True
	else:
		print("Button was pressed")
else:
	print("No button defined")

if protect:
	print("CIRCUITPY drive is read-only")
	storage.remount("/", False)
else:
	print("CIRCUITPY drive is writeable")
