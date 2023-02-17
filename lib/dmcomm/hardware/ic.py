# This file is part of the DMComm project by BladeSabre. License: MIT.

import array
import pulseio
import time
import rp2pio

from dmcomm import ReceiveError
from dmcomm.protocol import ic_encoding
from . import WAIT_REPLY
from . import misc
from . import pio_programs

class iC_Communicator:
	def __init__(self, ir_output, ir_input_raw):
		self._pin_output = ir_output.pin_output
		self._pin_input = ir_input_raw.pin_input
		self._output_state_machine = None
		self._input_pulses = None
		self._params = iC_Params()
		self._enabled = False
	def enable(self, protocol):
		self._params.set_protocol(protocol)
		if self._enabled:
			return
		try:
			self._output_state_machine = rp2pio.StateMachine(
				pio_programs.iC_TX,
				frequency=100_000,
				first_out_pin=self._pin_output,
				first_set_pin=self._pin_output,
				init=pio_programs.do_nothing,  # workaround for CircuitPython bug
			)
			self._input_pulses = pulseio.PulseIn(self._pin_input, maxlen=250, idle_state=True)
			self._input_pulses.pause()
		except:
			self.disable()
			raise
		self._enabled = True
	def disable(self):
		for item in [self._output_state_machine, self._input_pulses]:
			if item is not None:
				item.deinit()
		self._ouput_state_machine = None
		self._input_pulses = None
		self._enabled = False
	def send(self, bits):
		if not self._enabled:
			raise RuntimeError("not enabled")
		bytes_to_send = ic_encoding.encode(bits)
		self.send_bytes(bytes_to_send)
	def send_bytes(self, bytes_to_send):
		if not self._enabled:
			raise RuntimeError("not enabled")
		self._output_state_machine.write(bytes(bytes_to_send))
	def receive(self, timeout_ms):
		if not self._enabled:
			raise RuntimeError("not enabled")
		bytes_received = self.receive_bytes(timeout_ms)
		if bytes_received == []:
			return None
		try:
			(result, count) = ic_encoding.decode(bytes_received)
		except ValueError as e:
			raise ReceiveError(str(e))
		return result
	def receive_bytes(self, timeout_ms):
		if not self._enabled:
			raise RuntimeError("not enabled")
		pulses = self._input_pulses
		pulses.clear()
		pulses.resume()
		if timeout_ms == WAIT_REPLY:
			timeout_ms = self._params.reply_timeout_ms
		misc.wait_for_length(pulses, 1, timeout_ms)
		time.sleep(self._params.packet_length_timeout_ms / 1000)
		pulses.pause()
		if len(pulses) == pulses.maxlen:
			raise ReceiveError("buffer full")
		if len(pulses) == 0:
			return []
		#discard first byte or part of byte since we're joining partway through
		min_gap_find = 2.5 * self._params.tick_length
		while True:
			if len(pulses) == 0:
				raise ReceiveError("fragment")
			if pulses.popleft() > min_gap_find:
				break
		bytes_received = []
		current_byte = 0
		pulse_count = 0
		ticks_into_byte = 0
		ended = False
		while not ended:
			pulse_count += 1
			if len(pulses) == 0:
				raise ReceiveError("ended with gap")
			t_pulse = pulses.popleft()
			if t_pulse > self._params.pulse_max:
				raise ReceiveError("pulse %d = %d" % (pulse_count, t_pulse))
			if len(pulses) != 0:
				t_gap = pulses.popleft()
			else:
				t_gap = 0xFFFF
				ended = True
			dur = t_pulse + t_gap
			ticks = round(dur / self._params.tick_length)
			dur_rounded = ticks * self._params.tick_length
			off_rounded = abs(dur - dur_rounded)
			if ticks_into_byte + ticks >= 9:
				#finish byte
				for i in range(8 - ticks_into_byte):
					current_byte >>= 1
					current_byte |= 0x80
				bytes_received.append(current_byte)
				current_byte = 0
				ticks_into_byte = 0
			elif off_rounded > self._params.tick_margin:
				raise ReceiveError("pulse+gap %d = %d" % (pulse_count, dur))
			else:
				for i in range(ticks - 1):
					current_byte >>= 1
					current_byte |= 0x80
				current_byte >>= 1
				ticks_into_byte += ticks
		return bytes_received

class iC_Params:
	def __init__(self):
		self.set_protocol("IC")
	def set_protocol(self, protocol):
		if protocol == "IC":
			self.reply_timeout_ms = 100
			self.packet_length_timeout_ms = 30
			self.pulse_max = 25
			self.tick_length = 100
			self.tick_margin = 30
		else:
			raise ValueError("protocol must be IC")
		self.protocol = protocol
