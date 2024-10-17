# This file is part of the DMComm project by BladeSabre. License: MIT.

import pulseio

from dmcomm.hardware.comms.modulated_shared import send, receive

class ModulatedParams:
	def __init__(self, signal_type):
		if signal_type == "DL":
			self.low_bit_first = True
			self.low_byte_first = False
			self.start_pulse_send = 9800
			self.start_gap_send = 2450
			self.start_min = 4000  # ?
			self.start_max = 14000
			self.bit_pulse_send = 500
			self.bit_gap_send_short = 700
			self.bit_gap_send_long = 1300
			self.bit_min = 900
			self.bit_threshold = 1500
			self.bit_max = 2200
			self.stop_pulse_min = 800  # DL pulse widths most affected by sensor type
			self.stop_pulse_send = 1300
			self.stop_pulse_max = 1400
			self.stop_gap_send = 2000  # Delay start of pulse capture?
			self.reply_timeout_ms = 40
			self.packet_length_timeout_ms = 300
			self.packet_continue_timeout_ms = 10
		elif signal_type == "FL":
			self.low_bit_first = False
			self.low_byte_first = False
			self.start_pulse_send = 5880
			self.start_gap_send = 3872
			self.start_min = 7000
			self.start_max = 12000
			self.bit_pulse_send = 480
			self.bit_gap_send_short = 480
			self.bit_gap_send_long = 1450
			self.bit_min = 600
			self.bit_threshold = 1400
			self.bit_max = 2000
			self.stop_pulse_min = 600
			self.stop_pulse_send = 950
			self.stop_pulse_max = 1100
			self.stop_gap_send = 1500
			self.reply_timeout_ms = 100
			self.packet_length_timeout_ms = 300
			self.packet_continue_timeout_ms = 10
		else:
			raise ValueError("signal_type must be DL/FL")
		self.signal_type = signal_type

class ModulatedCommunicator:
	def __init__(self, ir_output, ir_input_modulated):
		self._pin_output = ir_output.pin_output
		self._pin_input = ir_input_modulated.pin_input
		self._output_pulses = None
		self._input_pulses = None
		self._params = None
		self._enabled = False
	def enable(self, signal_type):
		if self._enabled:
			if signal_type == self._params.signal_type:
				return
			self.disable()
		self._params = ModulatedParams(signal_type)
		try:
			self._output_pulses = pulseio.PulseOut(self._pin_output, frequency=38000, duty_cycle=0x8000)
			self._input_pulses = pulseio.PulseIn(self._pin_input, maxlen=300, idle_state=True)
			self._input_pulses.pause()
		except:
			self.disable()
			raise
		self._enabled = True
	def disable(self):
		for item in [self._output_pulses, self._input_pulses]:
			if item is not None:
				item.deinit()
		self._output_pulses = None
		self._input_pulses = None
		self._params = None
		self._enabled = False
	def reset(self):
		pass
	def send(self, bytes_to_send):
		if not self._enabled:
			raise RuntimeError("not enabled")
		send(self._output_pulses, self._params, bytes_to_send)
	def receive(self, timeout_ms):
		if not self._enabled:
			raise RuntimeError("not enabled")
		return receive(self._input_pulses, self._params, timeout_ms)
