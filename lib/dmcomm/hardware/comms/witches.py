# This file is part of the DMComm project by BladeSabre. License: MIT.

import array
import time

from dmcomm import ReceiveError
from dmcomm.hardware import WAIT_REPLY
from dmcomm.hardware.comms.classic_shared import BaseProngCommunicator

class WitchesParams:
	def __init__(self, signal_type):
		if signal_type == "!MW":
			self.idle_state = False
			self.clock = 19520
			self.reply_timeout_ms = 100
			self.packet_continue_timeout_seconds = 0.25
			self.slow_input = True
		else:
			raise ValueError("signal_type must be !MW")
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
		input_durations = [0]
		while True:
			current_value = digital_input.value
			current_time = time.monotonic()
			dur = current_time - prev_time
			if dur > self._params.packet_continue_timeout_seconds:
				break
			if current_value != prev_value:
				dur_micros = int(dur * 1000000)
				input_durations.append(dur_micros)
				prev_value = current_value
				prev_time = current_time
		print(input_durations)  #TODO remove this later
		return decode(input_durations, self._params.clock)

def decode(pulses, clock):
	result = []
	current_byte = 0
	bit_count = 0
	level = True
	for pulse in pulses:
		if level:
			# falling edge, round down prev high
			new_bits = pulse // clock
			for _ in range(new_bits):
				current_byte <<= 1
				current_byte |= 1
			bit_count += new_bits
		else:
			# rising edge, round up prev low
			new_bits = (pulse + clock // 2) // clock
			current_byte <<= new_bits
			bit_count += new_bits
		level = not level
		if bit_count == 10:
			result.append((current_byte >> 1) & 0xFF)
			current_byte = 0
			bit_count = 0
		if bit_count > 10:
			result.append(0x1000 + bit_count)
			return result
	current_byte <<= 10 - bit_count
	result.append((current_byte >> 1) & 0xFF)
	return result
