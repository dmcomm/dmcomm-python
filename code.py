# This file is part of the DMComm project by BladeSabre. License: MIT.

import board
import digitalio
import time
import usb_cdc

from dmcomm import CommandError, ReceiveError
import dmcomm.hardware as hw

pins_extra_power = [board.GP11, board.GP13, board.GP18]
outputs_extra_power = []
for pin in pins_extra_power:
	output = digitalio.DigitalInOut(pin)
	output.direction = digitalio.Direction.OUTPUT
	output.value = True
	outputs_extra_power.append(output)

controller = hw.Controller()
controller.register(hw.ProngOutput(board.GP19, board.GP21))
controller.register(hw.ProngInput(board.GP26))
controller.register(hw.InfraredOutput(board.GP16))
controller.register(hw.InfraredInputModulated(board.GP17))
controller.register(hw.InfraredInputRaw(board.GP14))
usb_cdc.console.timeout = 1

while True:
	if usb_cdc.console.in_waiting != 0:
		serial_bytes = usb_cdc.console.readline()
		serial_str = serial_bytes.decode("ascii", "ignore")
		# readline only accepts "\n" but we can receive "\r" after timeout
		if serial_str[-1] not in ["\r", "\n"]:
			print("too slow")
			continue
		serial_str = serial_str.strip()
		print("got %d bytes: %s -> " % (len(serial_str), serial_str), end="")
		try:
			result = controller.execute(serial_str)
			print(result)
		except (CommandError, NotImplementedError) as e:
			print(repr(e))
		time.sleep(1)
	error = ""
	result_end = "\n"
	done_time = False
	try:
		done_time = controller.communicate()
	except (CommandError, ReceiveError, NotImplementedError) as e:
		error = repr(e)
		result_end = " "
	result = controller.result()
	if result is not None:
		print(result, end=result_end)
	if error != "":
		print(error)
	if not done_time:
		time.sleep(5)
