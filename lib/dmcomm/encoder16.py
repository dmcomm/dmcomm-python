# This file is part of the DMComm project by BladeSabre. License: MIT.

class Encoder16:
	def __init__(self, communicator):
		self._communicator = communicator
		self.reset()
	def reset(self):
		self.bits_received = 0
		self._checksum = 0
	def send_bits(self, data, copy_mask=0, invert_mask=0, check_digit_pos=None):
		pass
	def send_code_segment(self, text):
		pass
