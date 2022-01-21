# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol.core_digits`
=============================

Handling of digit sequence low-level protocols.

Note: This API is still under development and may change at any time.
"""

from dmcomm import CommandError
from dmcomm.protocol import BaseDigiROM, Result

class DigiROM(BaseDigiROM):
	"""Describes the communication for digit-sequence protocols and records the results.
	"""
	def __init__(self, physical, turn, segments=[]):
		super().__init__(ResultSegment, physical, turn, segments)

class CommandSegment:
	"""Describes how to carry out one segment of the communication for digit-sequence protocols.
	"""
	@classmethod
	def from_string(cls, text):
		"""Creates a `CommandSegment` from one of the dash-separated parts of a text command.
		"""
		data = []
		for digit in text:
			try:
				n = int(digit)
			except:
				raise CommandError("not a number: " + digit)
			data.append(n)
		return cls(data)
	def __init__(self, data):
		self.data = data
	#def __str__():

class ResultSegment:
	"""Describes the result of one segment of the communication for digit-sequence protocols.

	:param sent: True if this represents data sent, False if data received.
	:param data: A list of integers representing the digits sent or received.
		If sent is False, can be empty to indicate nothing was received before timeout.
	"""
	def __init__(self, sent: bool, data: list):
		self.sent = sent
		self.data = data
	def __str__(self):
		"""Returns text formatted for the serial protocol."""
		digits = ["%d" % n for n in self.data]
		digit_str = "".join(digits)
		if self.sent:
			return "s:" + digit_str
		elif self.data == []:
			return "t"
		else:
			return "r:" + digit_str
