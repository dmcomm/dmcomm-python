# This file is part of the DMComm project by BladeSabre. License: MIT.

import board
import busio
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

# Serial port selection
if usb_cdc.data is not None:
	serial = usb_cdc.data
else:
	serial = usb_cdc.console
#serial = usb_cdc.console  # same as REPL
#serial = usb_cdc.data  # alternate USB serial
#serial = busio.UART(board.GP0, board.GP1)  # for external UART

# Choose an initial digirom / auto-responder here:
digirom = None  # disable
#digirom = dmcomm.protocol.auto.AutoResponderVX("V")  # 2-prong auto-responder
#digirom = dmcomm.protocol.auto.AutoResponderVX("X")  # 3-prong auto-responder
#digirom = dmcomm.protocol.parse_command("IC2-0007-^0^207-0007-@400F" + "-0000" * 16)  # Twin any
# ...or use your own digirom, as for the Twin above.

serial.timeout = 1
def serial_print(s):
	serial.write(s.encode("utf-8"))
serial_print("dmcomm-python starting\n")

while True:
	time_start = time.monotonic()
	if serial.in_waiting != 0:
		digirom = None
		serial_bytes = serial.readline()
		serial_str = serial_bytes.decode("ascii", "ignore")
		# readline only accepts "\n" but we can receive "\r" after timeout
		if serial_str[-1] not in ["\r", "\n"]:
			serial_print("too slow\n")
			continue
		serial_str = serial_str.strip()
		serial_str = serial_str.strip("\0")
		serial_print(f"got {len(serial_str)} bytes: {serial_str} -> ")
		try:
			command = dmcomm.protocol.parse_command(serial_str)
			if hasattr(command, "op"):
				# It's an OtherCommand
				raise NotImplementedError("op=" + command.op)
			digirom = command
			serial_print(f"{digirom.physical}{digirom.turn}-[{len(digirom)} packets]\n")
		except (CommandError, NotImplementedError) as e:
			serial_print(repr(e) + "\n")
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
		serial_print(str(digirom.result) + result_end)
		if error != "":
			serial_print(error + "\n")
		led.value = False
	seconds_passed = time.monotonic() - time_start
	if seconds_passed < 5:
		time.sleep(5 - seconds_passed)
