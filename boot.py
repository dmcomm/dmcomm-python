# This file is part of the DMComm project by BladeSabre. License: MIT.

# Use this with a push-to-close button between the assigned pin and GND.
# Disables HID and status bar.
# Normally makes CIRCUITPY read-only and switches to data serial,
# but leaves these in the default configuration if the button is held on startup.

import board
import digitalio
import storage
import supervisor
import usb_cdc
import usb_hid

# HID is not used in this project
usb_hid.disable()

try:
	supervisor.status_bar.console = False
	supervisor.status_bar.display = False
except:
	print("Status bar API not present")

if board.board_id == "arduino_nano_rp2040_connect":
	button_pin = board.D3
elif board.board_id in ["raspberry_pi_pico", "raspberry_pi_pico_w"]:
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
		print("Button was not pressed: CIRCUITPY drive is read-only; using data serial")
		storage.remount("/", False)
		usb_cdc.enable(console=False, data=True)
	else:
		print("Button was pressed: CIRCUITPY drive is writeable; using console serial")
else:
	print("No button defined")
