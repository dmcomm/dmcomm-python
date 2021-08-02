# This file is part of the DMComm project by BladeSabre. License: MIT.

import board
import usb_cdc

import dmcomm

controller = dmcomm.Controller()
controller.register(dmcomm.ProngOutput(board.GP19, board.GP21))
controller.register(dmcomm.ProngInput(board.GP26))
usb_cdc.console.timeout = 1

while True:
	if usb_cdc.console.in_waiting != 0:
		serial_bytes = usb_cdc.console.readline()
		serial_str = serial_bytes.decode("ascii", "ignore")
		if serial_str[-1] != "\n":
			print("too slow")
			continue
		serial_str = serial_str.strip()
		print("got %d bytes: %s -> " % (len(serial_str), serial_str), end="")
		try:
			result = controller.execute(serial_str)
			print(result)
		except (ValueError, NotImplementedError) as e:
			print(repr(e))
