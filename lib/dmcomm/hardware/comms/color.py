# This file is part of the DMComm project by BladeSabre. License: MIT.

import array

from dmcomm import ReceiveError
from dmcomm.hardware import WAIT_REPLY
from dmcomm.hardware.misc import wait_for_length_2
from dmcomm.hardware.comms.classic_shared import BaseProngCommunicator

class ColorParams:
	def __init__(self, signal_type):
		if signal_type == "C":
			self.idle_state = True
			self.pre_idle_send = 1000
			self.pre_active_min = 65535
			self.pre_active_send = 150000
			#self.pre_active_max? PulseIn only goes up to 65535
			self.bit_idle_min = 200
			self.bit_idle_send = 500
			self.bit_idle_max = 700
			self.bit_active_min = 200
			self.bit1_active_send = 1500
			self.bit_active_threshold = 1000
			self.bit0_active_send = 500
			self.bit_active_max = 1700
			self.cooldown_send = 500
			self.reply_timeout_ms = 200
			self.packet_length_timeout_ms = 400
			self.pulses_expected = 257
			self.slow_input = False
		else:
			raise ValueError("signal_type must be C")
		self.signal_type = signal_type

class ColorCommunicator(BaseProngCommunicator):
	params_class = ColorParams
	def send(self, data):
		if not self._enabled:
			raise RuntimeError("not enabled")
		DRIVE_ACTIVE = 0
		DRIVE_IDLE = 1
		RELEASE = 2
		array_to_send = array.array("L", [
			DRIVE_IDLE, self._params.pre_idle_send,
			DRIVE_ACTIVE, self._params.pre_active_send,
		])
		for bits in data:
			for i in range(16):
				array_to_send.append(DRIVE_IDLE)
				array_to_send.append(self._params.bit_idle_send)
				array_to_send.append(DRIVE_ACTIVE)
				if bits & 1:
					array_to_send.append(self._params.bit1_active_send)
				else:
					array_to_send.append(self._params.bit0_active_send)
				bits >>= 1
		array_to_send.append(DRIVE_IDLE)
		array_to_send.append(self._params.cooldown_send)
		array_to_send.append(RELEASE)
		self._output_state_machine.write(array_to_send)
	def receive(self, timeout_ms):
		if not self._enabled:
			raise RuntimeError("not enabled")
		pulses = self._input_pulses
		pulses.clear()
		pulses.resume()
		if timeout_ms == WAIT_REPLY:
			timeout_ms = self._params.reply_timeout_ms
		wait_for_length_2(pulses, self._params.pulses_expected, timeout_ms, self._params.packet_length_timeout_ms)
		pulses.pause()
		if len(pulses) == pulses.maxlen:
			raise ReceiveError("buffer full")
		if len(pulses) == 0:
			return []
		ic_bug = False
		if len(pulses) < self._params.pulses_expected:
			raise ReceiveError("incomplete: %d pulses" % len(pulses))
		t = pulses.popleft()
		if t < self._params.pre_active_min:
			raise ReceiveError("pre_active = %d" % t)
		pulses = self._input_pulses
		results = []
		bit_count = 0
		while len(pulses) > 0:
			result = 0
			for i in range(16):
				t = pulses.popleft()
				if t < self._params.bit_idle_min or t > self._params.bit_idle_max:
					raise ReceiveError("bit_idle %d = %d" % (bit_count + 1, t))
				t = pulses.popleft()
				if t < self._params.bit_active_min or t > self._params.bit_active_max:
					raise ReceiveError("bit_active %d = %d" % (bit_count + 1, t))
				result >>= 1
				if t > self._params.bit_active_threshold:
					result |= 0x8000
				bit_count += 1
			results.append(result)
		return results
