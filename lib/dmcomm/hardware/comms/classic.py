# This file is part of the DMComm project by BladeSabre. License: MIT.

import array

from dmcomm import ReceiveError
from dmcomm.hardware import WAIT_REPLY
from dmcomm.hardware.misc import wait_for_length_2
from dmcomm.hardware.comms.classic_shared import BaseProngCommunicator

class ClassicParams:
	def __init__(self, signal_type):
		if signal_type == "V":
			self.idle_state = True
			self.invert_bit_read = False
			self.pre_idle_send = 3000
			self.pre_active_min = 40000
			self.pre_active_send = 59000
			#self.pre_active_max? PulseIn only goes up to 65535
			self.start_idle_min = 1500
			self.start_idle_send = 2083
			self.start_idle_max = 2500
			self.start_active_min = 600
			self.start_active_send = 917
			self.start_active_max = 1400
			self.bit_idle_min = 700
			self.bit0_idle_send = 1000
			self.bit_idle_threshold = 1800
			self.bit1_idle_send = 2667
			self.bit_idle_max = 3400
			self.bit_active_min = 1000
			self.bit1_active_send = 1667
			self.bit0_active_send = 3167
			self.bit_active_max = 4000
			self.cooldown_send = 400
			self.reply_timeout_ms = 100
			self.packet_length_timeout_ms = 300
		elif signal_type == "X":
			self.idle_state = True
			self.invert_bit_read = False
			self.pre_idle_send = 3000
			self.pre_active_min = 40000
			self.pre_active_send = 60000
			#self.pre_active_max? PulseIn only goes up to 65535
			self.start_idle_min = 1500
			self.start_idle_send = 2200
			self.start_idle_max = 3500
			self.start_active_min = 1000
			self.start_active_send = 1600
			self.start_active_max = 2600
			self.bit_idle_min = 800
			self.bit0_idle_send = 1600
			self.bit_idle_threshold = 2600
			self.bit1_idle_send = 4000
			self.bit_idle_max = 5500
			self.bit_active_min = 1200
			self.bit1_active_send = 1600
			self.bit0_active_send = 4000
			self.bit_active_max = 5500
			self.cooldown_send = 400
			self.reply_timeout_ms = 200
			self.packet_length_timeout_ms = 300
		elif signal_type == "Y":
			self.idle_state = False
			self.invert_bit_read = True
			self.pre_idle_send = 5000
			self.pre_active_min = 30000
			self.pre_active_send = 40000
			#self.pre_active_max? PulseIn only goes up to 65535
			self.start_idle_min = 9000
			self.start_idle_send = 11000
			self.start_idle_max = 13000
			self.start_active_min = 4000
			self.start_active_send = 6000
			self.start_active_max = 8000
			self.bit_idle_min = 1000
			self.bit0_idle_send = 4000
			self.bit_idle_threshold = 3000
			self.bit1_idle_send = 1400
			self.bit_idle_max = 4600
			self.bit_active_min = 1200
			self.bit1_active_send = 4400
			self.bit0_active_send = 1600
			self.bit_active_max = 5000
			self.cooldown_send = 200
			self.reply_timeout_ms = 100
			self.packet_length_timeout_ms = 300
		else:
			raise ValueError("signal_type must be V/X/Y")
		self.signal_type = signal_type

class ClassicCommunicator(BaseProngCommunicator):
	params_class = ClassicParams
	def send(self, bits):
		if not self._enabled:
			raise RuntimeError("not enabled")
		if self._params.idle_state == True:
			DRIVE_ACTIVE = 0
			DRIVE_IDLE = 1
		else:
			DRIVE_ACTIVE = 1
			DRIVE_IDLE = 0
		RELEASE = 2
		array_to_send = array.array("L", [
			DRIVE_IDLE, self._params.pre_idle_send,
			DRIVE_ACTIVE, self._params.pre_active_send,
			DRIVE_IDLE, self._params.start_idle_send,
			DRIVE_ACTIVE, self._params.start_active_send,
		])
		for i in range(16):
			array_to_send.append(DRIVE_IDLE)
			if bits & 1:
				array_to_send.append(self._params.bit1_idle_send)
				array_to_send.append(DRIVE_ACTIVE)
				array_to_send.append(self._params.bit1_active_send)
			else:
				array_to_send.append(self._params.bit0_idle_send)
				array_to_send.append(DRIVE_ACTIVE)
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
		wait_for_length_2(pulses, 35, timeout_ms, self._params.packet_length_timeout_ms)
		pulses.pause()
		if len(pulses) == pulses.maxlen:
			raise ReceiveError("buffer full")
		if len(pulses) == 0:
			return None
		ic_bug = False
		if len(pulses) < 35:
			if self._params.signal_type == "X" and len(pulses) == 34:
				ic_bug = True
			else:
				raise ReceiveError("incomplete: %d pulses" % len(pulses))
		t = pulses.popleft()
		if t < self._params.pre_active_min:
			raise ReceiveError("pre_active = %d" % t)
		t = pulses.popleft()
		if t < self._params.start_idle_min or t > self._params.start_idle_max:
			raise ReceiveError("start_idle = %d" % t)
		t = pulses.popleft()
		if t < self._params.start_active_min or t > self._params.start_active_max:
			raise ReceiveError("start_active = %d" % t)
		result = 0
		for i in range(16):
			t = pulses.popleft()
			if t < self._params.bit_idle_min or t > self._params.bit_idle_max:
				raise ReceiveError("bit_idle %d = %d" % (i + 1, t))
			result >>= 1
			if t > self._params.bit_idle_threshold:
				result |= 0x8000
			if ic_bug and i == 15:
				break
			t = pulses.popleft()
			if t < self._params.bit_active_min or t > self._params.bit_active_max:
				raise ReceiveError("bit_active %d = %d" % (i + 1, t))
		if self._params.invert_bit_read:
			result ^= 0xFFFF
		return result
