# This file is part of the DMComm project by BladeSabre. License: MIT.

import array
import pulseio

from dmcomm import CommandError, ReceiveError
from . import WAIT_REPLY
from . import misc

def reverse_bits_8(x):
	y = 0
	for j in range(8):
		y <<= 1
		y |= (x & 1)
		x >>= 1
	return y

def send(output_pulses, params, bytes_to_send):
	if params.low_byte_first:
		bytes_to_send = bytes_to_send[:]  #copy
	else:
		bytes_to_send = bytes_to_send[::-1]  #reversed copy
	if not params.low_bit_first:
		for i in range(len(bytes_to_send)):
			bytes_to_send[i] = reverse_bits_8(bytes_to_send[i])
	num_durations = len(bytes_to_send) * 16 + 4
	array_to_send = array.array("H")
	for i in range(num_durations):
		array_to_send.append(0)
		#This function would be simpler if we append as we go along,
		#but still hoping for a fix that allows reuse of the array.
	array_to_send[0] = params.start_pulse_send
	array_to_send[1] = params.start_gap_send
	buf_cursor = 2
	for current_byte in bytes_to_send:
		for j in range(8):
			array_to_send[buf_cursor] = params.bit_pulse_send
			buf_cursor += 1
			if current_byte & 1:
				array_to_send[buf_cursor] = params.bit_gap_send_long
			else:
				array_to_send[buf_cursor] = params.bit_gap_send_short
			buf_cursor += 1
			current_byte >>= 1
	array_to_send[buf_cursor] = params.stop_pulse_send
	array_to_send[buf_cursor + 1] = params.stop_gap_send
	output_pulses.send(array_to_send)

def receive(input_pulses, params, timeout_ms):
	pulses = input_pulses
	pulses.clear()
	pulses.resume()
	if timeout_ms == WAIT_REPLY:
		timeout_ms = params.reply_timeout_ms
	misc.wait_for_length_no_more(pulses, timeout_ms,
		params.packet_length_timeout_ms, params.packet_continue_timeout_ms)
	pulses.pause()
	if len(pulses) == pulses.maxlen:
		raise ReceiveError("buffer full")
	if len(pulses) == 0:
		return []
	bytes_received = []
	t = misc.pop_pulse(pulses, -2)
	if t < params.start_pulse_min or t > params.start_pulse_max:
		raise ReceiveError("start pulse = %d" % t)
	t = misc.pop_pulse(pulses, -1)
	if t < params.start_gap_min or t > params.start_gap_max:
		raise ReceiveError("start gap = %d" % t)
	current_byte = 0
	bit_count = 0
	while True:
		t = misc.pop_pulse(pulses, 2*bit_count+1)
		if t >= params.bit_pulse_min and t <= params.bit_pulse_max:
			#normal pulse or
			if params.stop_pulse_same and len(pulses) == 0:
				#stop pulse
				break
		elif t >= params.stop_pulse_min and t <= params.stop_pulse_max:
			#stop pulse
			break
		else:
			raise ReceiveError("bit %d pulse = %d" % (bit_count, t))
		t = misc.pop_pulse(pulses, 2*bit_count+2)
		if t < params.bit_gap_min or t > params.bit_gap_max:
			raise ReceiveError("bit %d gap = %d" % (bit_count, t))
		current_byte >>= 1
		if t > params.bit_gap_threshold:
			current_byte |= 0x80
		bit_count += 1
		if bit_count % 8 == 0:
			bytes_received.append(current_byte)
			current_byte = 0
	if bit_count % 8 != 0:
		raise ReceiveError("bit_count = %d" % bit_count)
	if not params.low_byte_first:
		bytes_received.reverse()
	if not params.low_bit_first:
		for i in range(len(bytes_received)):
			bytes_received[i] = reverse_bits_8(bytes_received[i])
	return bytes_received

class ModulatedCommunicator:
	def __init__(self, ir_output, ir_input_modulated):
		self._pin_output = ir_output.pin_output
		self._pin_input = ir_input_modulated.pin_input
		self._output_pulses = None
		self._input_pulses = None
		self._params = ModulatedParams()
		self._enabled = False
	def enable(self, protocol):
		self._params.set_protocol(protocol)
		if self._enabled:
			return
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
		self._ouput_pulses = None
		self._input_pulses = None
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

class TalisCommunicator:
	def __init__(self, talis_input_output):
		self._pin = talis_input_output.pin
		self._params = ModulatedParams()
		self._enabled = False
	def enable(self, protocol):
		self._params.set_protocol(protocol)
		self._enabled = True
	def disable(self):
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

class ModulatedParams:
	def __init__(self):
		self.set_protocol("!DL")
	def set_protocol(self, protocol):
		if protocol == "!DL":
			self.low_bit_first = True
			self.low_byte_first = True
			self.start_pulse_min = 9000
			self.start_pulse_send = 9800
			self.start_pulse_max = 11000
			self.start_gap_min = 2000
			self.start_gap_send = 2450
			self.start_gap_max = 3000
			self.bit_pulse_min = 300
			self.bit_pulse_send = 500
			self.bit_pulse_max = 650
			self.bit_gap_min = 300
			self.bit_gap_send_short = 700
			self.bit_gap_threshold = 800
			self.bit_gap_send_long = 1300
			self.bit_gap_max = 1500
			self.stop_pulse_same = False
			self.stop_pulse_min = 1000
			self.stop_pulse_send = 1300
			self.stop_pulse_max = 1400
			self.stop_gap_send = 400
			self.reply_timeout_ms = 40
			self.packet_length_timeout_ms = 300
			self.packet_continue_timeout_ms = 10
		elif protocol == "!!FL":
			self.low_bit_first = False
			self.low_byte_first = False
			self.start_pulse_min = 3800
			self.start_pulse_send = 5880
			self.start_pulse_max = 7000
			self.start_gap_min = 3000
			self.start_gap_send = 3872
			self.start_gap_max = 4000
			self.bit_pulse_min = 250
			self.bit_pulse_send = 480
			self.bit_pulse_max = 600
			self.bit_gap_min = 200
			self.bit_gap_send_short = 480
			self.bit_gap_threshold = 650
			self.bit_gap_send_long = 1450
			self.bit_gap_max = 1600
			self.stop_pulse_same = False
			self.stop_pulse_min = 700
			self.stop_pulse_send = 950
			self.stop_pulse_max = 1100
			self.stop_gap_send = 1500
			self.reply_timeout_ms = 100
			self.packet_length_timeout_ms = 300
			self.packet_continue_timeout_ms = 10
		elif protocol == "LT":
			self.low_bit_first = False
			self.low_byte_first = False
			self.start_pulse_min = 2800
			self.start_pulse_send = 3900
			self.start_pulse_max = 4800
			self.start_gap_min = 3000
			self.start_gap_send = 4000
			self.start_gap_max = 5000
			self.bit_pulse_min = 220
			self.bit_pulse_send = 420
			self.bit_pulse_max = 620
			self.bit_gap_min = 220
			self.bit_gap_send_short = 560
			self.bit_gap_threshold = 800
			self.bit_gap_send_long = 1530
			self.bit_gap_max = 1800
			self.stop_pulse_same = True
			self.stop_pulse_min = 220
			self.stop_pulse_send = 420
			self.stop_pulse_max = 620
			self.stop_gap_send = 1500
			self.reply_timeout_ms = 300
			self.packet_length_timeout_ms = 400
			self.packet_continue_timeout_ms = 10
		else:
			raise ValueError("protocol must be !DL/!!FL/LT")
		self.protocol = protocol
