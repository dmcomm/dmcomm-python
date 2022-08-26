# This file is part of the DMComm project by BladeSabre. License: MIT.

# Use this with a push-to-close button between the assigned pin and GND.
# Disables HID.
# Normally disables CIRCUITPY and console serial, and enables data serial,
# but leaves these in the default configuration if the button is held on startup.

import board
import digitalio
import storage
import usb_cdc
import usb_hid

# HID is not used in this project
usb_hid.disable()

if board.board_id == "arduino_nano_rp2040_connect":
	button_pin = board.D3
elif board.board_id == "raspberry_pi_pico":
	button_pin = board.GP3
elif board.board_id == "seeeduino_xiao_rp2040":
	button_pin = board.D6
else:
	button_pin = None

# Configure depending on button press
if button_pin is not None:
	# push-to-close button between button_pin and GND
	button = digitalio.DigitalInOut(button_pin)
	button.pull = digitalio.Pull.UP
	if button.value:
		# button is not pressed
		storage.disable_usb_drive()
		usb_cdc.enable(console=False, data=True)
