# This file is part of the DMComm project by BladeSabre. License: MIT.

import pulseio

from dmcomm.hardware.comms.modulated_shared import send, receive

class TalisParams:
	def __init__(self, signal_type):
		if signal_type == "LT":
			self.low_bit_first = False
			self.low_byte_first = False
			self.start_pulse_send = 3900
			self.start_gap_send = 4000
			self.start_min = 4000  # Start pulse comes out much lower than expected
			self.start_max = 10000
			self.bit_pulse_send = 420
			self.bit_gap_send_short = 560
			self.bit_gap_send_long = 1530
			self.bit_min = 600
			self.bit_threshold = 1400
			self.bit_max = 2200
			self.stop_pulse_min = 220
			self.stop_pulse_send = 420
			self.stop_pulse_max = 620
			self.stop_gap_send = 1500
			self.reply_timeout_ms = 300
			self.packet_length_timeout_ms = 400
			self.packet_continue_timeout_ms = 10
		else:
			raise ValueError("signal_type must be LT")
		self.signal_type = signal_type

class TalisCommunicator:
	def __init__(self, talis_input_output):
		self._pin = talis_input_output.pin
		self._params = None
		self._enabled = False
	def enable(self, signal_type):
		if self._enabled:
			if signal_type == self._params.signal_type:
				return
			self.disable()
		self._params = TalisParams(signal_type)
		self._enabled = True
	def disable(self):
		self._params = None
		self._enabled = False
	def reset(self):
		pass
	def send(self, bytes_to_send):
		if not self._enabled:
			raise RuntimeError("not enabled")
		output_pulses = pulseio.PulseOut(self._pin, frequency=100000, duty_cycle=0xFFFF)
		try:
			send(output_pulses, self._params, bytes_to_send)
		finally:
			output_pulses.deinit()
	def receive(self, timeout_ms):
		if not self._enabled:
			raise RuntimeError("not enabled")
		input_pulses = pulseio.PulseIn(self._pin, maxlen=600, idle_state=False)
		input_pulses.pause()
		try:
			bytes_received = receive(input_pulses, self._params, timeout_ms)
		finally:
			input_pulses.deinit()
		return bytes_received
