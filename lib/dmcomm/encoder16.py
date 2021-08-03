# This file is part of the DMComm project by BladeSabre. License: MIT.

from . import misc

class Encoder16:
	def __init__(self, communicator):
		self._communicator = communicator
		self.reset()
	def reset(self):
		self.bits_received = 0
		self._checksum = 0
	def send_bits(self, bits, copy_mask=0, invert_mask=0, check_digit_pos=None):
		#TODO
		self._communicator.send(bits)
		return (bits, "s:zzzz")
	def send_code_segment(self, text):
		#TODO
		try:
			bits = int(text, 16)
		except:
			raise misc.CommandError("not hex number: " + text)
		return self.send_bits(bits)
	def receive(self, timeout_ms):
		#TODO
		data = self._communicator.receive(timeout_ms)
		if data is None:
			desc = "t"
		else:
			desc = "r:zzzz"
		return (data, desc)
