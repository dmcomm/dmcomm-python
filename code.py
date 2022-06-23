# This file is part of the DMComm project by BladeSabre. License: MIT.

import board
import digitalio
import time
import usb_cdc

from dmcomm import CommandError, ReceiveError
import dmcomm.hardware as hw
import dmcomm.protocol
import dmcomm.protocol.auto

pins_extra_power = [board.GP11, board.GP13, board.GP18]
outputs_extra_power = []
for pin in pins_extra_power:
	output = digitalio.DigitalInOut(pin)
	output.direction = digitalio.Direction.OUTPUT
	output.value = True
	outputs_extra_power.append(output)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

controller = hw.Controller()
controller.register(hw.ProngOutput(board.GP19, board.GP21))
controller.register(hw.ProngInput(board.GP26))
controller.register(hw.InfraredOutput(board.GP16))
controller.register(hw.InfraredInputModulated(board.GP17))
controller.register(hw.InfraredInputRaw(board.GP14))

usb_cdc.console.timeout = 1
digirom = dmcomm.protocol.auto.AutoResponderVX("V")

while True:
	time_start = time.monotonic()
	if usb_cdc.console.in_waiting != 0:
		digirom = None
		serial_bytes = usb_cdc.console.readline()
		serial_str = serial_bytes.decode("ascii", "ignore")
		# readline only accepts "\n" but we can receive "\r" after timeout
		if serial_str[-1] not in ["\r", "\n"]:
			print("too slow")
			continue
		serial_str = serial_str.strip()
		print("got %d bytes: %s -> " % (len(serial_str), serial_str), end="")
		try:
			command = dmcomm.protocol.parse_command(serial_str)
			if hasattr(command, "op"):
				# It's an OtherCommand
				raise NotImplementedError("op=" + command.op)
			digirom = command
			print(f"{digirom.physical}{digirom.turn}-[{len(digirom)} packets]")
		except (CommandError, NotImplementedError) as e:
			print(repr(e))
		time.sleep(1)
	if digirom is not None:
		error = ""
		result_end = "\n"
		try:
			controller.execute(digirom)
		except (CommandError, ReceiveError) as e:
			error = repr(e)
			result_end = " "
		led.value = True
		print(digirom.result, end=result_end)
		if error != "":
			print(error)
		led.value = False
	seconds_passed = time.monotonic() - time_start
	if seconds_passed < 5:
		time.sleep(5 - seconds_passed)
