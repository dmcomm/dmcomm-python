# This file is part of the DMComm project by BladeSabre. License: MIT.

import array
import time

from dmcomm import ReceiveError
from dmcomm.hardware import WAIT_REPLY
from dmcomm.hardware.comms.classic_shared import BaseProngCommunicator

class WitchesParams:
	def __init__(self, signal_type):
		if signal_type == "MW":
			self.idle_state = False
			self.clock = 19520
			self.reply_timeout_ms = 300
			self.packet_continue_timeout_seconds = 0.25
			self.slow_input = True
		else:
			raise ValueError("signal_type must be MW")
		self.signal_type = signal_type

class WitchesCommunicator(BaseProngCommunicator):
	params_class = WitchesParams
	def send(self, data):
		if not self._enabled:
			raise RuntimeError("not enabled")
		DRIVE_ACTIVE = 1
		DRIVE_IDLE = 0
		RELEASE = 2
		array_to_send = array.array("L")
		for byte_to_send in data:
			bits_to_send = (byte_to_send << 1) | 0x200
			for _ in range(10):
				if bits_to_send & 0x200:
					array_to_send.append(DRIVE_ACTIVE)
				else:
					array_to_send.append(DRIVE_IDLE)
				array_to_send.append(self._params.clock)
				bits_to_send <<= 1
		array_to_send.append(RELEASE)
		self._output_state_machine.write(array_to_send)
	def receive(self, timeout_ms):
		if not self._enabled:
			raise RuntimeError("not enabled")
		digital_input = self._input_pulses
		if timeout_ms == WAIT_REPLY:
			timeout_ms = self._params.reply_timeout_ms
		timeout_seconds = timeout_ms / 1000
		prev_time = time.monotonic()
		while digital_input.value == self._params.idle_state:
			if time.monotonic() - prev_time > timeout_seconds:
				return []
		prev_value = not self._params.idle_state
		prev_time = time.monotonic()
		clocked_pulses = []
		clock_seconds = self._params.clock / 1000000
		while True:
			current_value = digital_input.value
			current_time = time.monotonic()
			dur = current_time - prev_time
			if dur > self._params.packet_continue_timeout_seconds:
				break
			if current_value != prev_value:
				pulse = round(dur / clock_seconds)
				clocked_pulses.append(pulse)
				prev_value = current_value
				prev_time = current_time
		return decode(clocked_pulses)

def decode(clocked_pulses):
	result = []
	current_byte = 0
	bit_count = 0
	level = 1
	for new_bits in clocked_pulses:
		for _ in range(new_bits):
			current_byte <<= 1
			current_byte |= level
		bit_count += new_bits
		level = 1 - level
		if bit_count == 10:
			result.append((current_byte >> 1) & 0xFF)
			current_byte = 0
			bit_count = 0
		if bit_count > 10:
			raise ReceiveError("byte too long")
	current_byte <<= 10 - bit_count
	result.append((current_byte >> 1) & 0xFF)
	return result
