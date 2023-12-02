# This file is part of the DMComm project by BladeSabre. License: MIT.

import board
import digitalio
import os
import time
import usb_cdc

from dmcomm import CommandError, ReceiveError
import dmcomm.hardware as hw
import dmcomm.protocol
import dmcomm.protocol.auto
import board_config

VERSION = f"""dmcomm-python v0.7.0+wip
CircuitPython {os.uname().version}
{os.uname().machine}"""

outputs_extra_power = []
for (pin, value) in board_config.extra_power_pins:
	output = digitalio.DigitalInOut(pin)
	output.direction = digitalio.Direction.OUTPUT
	output.value = value
	outputs_extra_power.append(output)

controller = hw.Controller()
for pin_description in board_config.controller_pins:
	controller.register(pin_description)

led = digitalio.DigitalInOut(board_config.led_pin)
led.direction = digitalio.Direction.OUTPUT
serial = usb_cdc.console

# Choose an initial digirom / auto-responder here:
digirom = None  # disable
#digirom = dmcomm.protocol.auto.AutoResponderVX("V")  # 2-prong auto-responder
#digirom = dmcomm.protocol.auto.AutoResponderVX("X")  # 3-prong auto-responder
#digirom = dmcomm.protocol.parse_command("IC2-0007-^0^207-0007-@400F" + "-0000" * 16)  # Twin any
# ...or use your own digirom, as for the Twin above.

serial.timeout = 1
print("dmcomm-python starting")

while True:
	time_start = time.monotonic()
	if serial.in_waiting != 0:
		digirom = None
		serial_bytes = serial.readline()
		try:
			serial_str = serial_bytes.decode("utf-8")
		except UnicodeError:
			print(f"UnicodeError: {repr(serial_bytes)}")
			continue
		# readline only accepts "\n" but we can receive "\r" after timeout
		if serial_str[-1] not in ["\r", "\n"]:
			print(f"too slow: {repr(serial_bytes)}")
			continue
		serial_str = serial_str.strip()
		serial_str = serial_str.strip("\0")
		print(f"got {len(serial_str)} bytes: {serial_str} -> ", end="")
		try:
			command = dmcomm.protocol.parse_command(serial_str)
			if hasattr(command, "op"):
				# It's an OtherCommand
				if command.op == "?":
					print(VERSION)
				else:
					raise NotImplementedError("op=" + command.op)
			else:
				digirom = command
				print(f"{digirom.signal_type}{digirom.turn}-[{len(digirom)} packets]")
		except (CommandError, NotImplementedError) as e:
			print(repr(e))
		time.sleep(1)
	if digirom is not None:
		error = ""
		result_end = "\r\n"
		try:
			controller.execute(digirom)
		except (CommandError, ReceiveError) as e:
			error = repr(e)
			result_end = " "
		led.value = True
		print(str(digirom.result), end=result_end)
		if error != "":
			print(error)
		led.value = False
	seconds_passed = time.monotonic() - time_start
	if seconds_passed < 5:
		time.sleep(5 - seconds_passed)
