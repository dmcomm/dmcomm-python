# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol.core_bytes`
============================

Handling of byte-sequence low-level protocols.

Note: This API is still under development and may change at any time.
"""

from dmcomm import CommandError
from dmcomm.protocol import BaseDigiROM, Result

class DigiROM(BaseDigiROM):
	"""Describes the communication for byte-sequence protocols and records the results.
	"""
	def __init__(self, physical, turn, segments=None):
		super().__init__(ResultSegment, physical, turn, segments)

class CommandSegment:
	"""Describes how to carry out one segment of the communication for byte-sequence protocols.
	"""
	@classmethod
	def from_string(cls, text):
		"""Creates a `CommandSegment` from one of the dash-separated parts of a text command.
		"""
		if len(text) < 2 or len(text) % 2 != 0:
			raise CommandError("bad length: " + text)
		data = []
		for i in range(0, len(text)-1, 2):
			digits = text[i:i+2]
			try:
				b = int(digits, 16)
			except:
				raise CommandError("not hex number: " + digits)
			data.append(b)
		return cls(data)
	def __init__(self, data):
		self.data = data
	#def __str__():

class ResultSegment:
	"""Describes the result of one segment of the communication for byte-sequence protocols.

	:param sent: True if this represents data sent, False if data received.
	:param data: A list of 8-bit integers representing the bytes sent or received.
		If sent is False, can be empty to indicate nothing was received before timeout.
	"""
	def __init__(self, sent: bool, data: list):
		self.sent = sent
		self.data = data
	def __str__(self):
		"""Returns text formatted for the serial protocol."""
		hex_parts = ["%02X" % b for b in self.data]
		hex_str = "".join(hex_parts)
		if self.sent:
			return "s:" + hex_str
		elif self.data == []:
			return "t"
		else:
			return "r:" + hex_str
