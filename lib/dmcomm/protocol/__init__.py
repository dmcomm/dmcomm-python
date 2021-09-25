# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol`
=================

...

Note: This API is still under development and may change at any time.

"""

from dmcomm import CommandError

def parse_command(text):
	parts = text.strip().upper().split("-")
	if len(parts[0]) >= 2:
		op = parts[0][:-1]
		turn = parts[0][-1]
	else:
		op = parts[0]
		turn = ""
	if op in ["D", "T"]:
		return OtherCommand(op, turn)
	elif op in ["V", "X", "Y", "!IC"]:
		from dmcomm.protocol.core16 import CommandSegment, DigiROM
	elif op in ["!DL", "!FL"]:
		from dmcomm.protocol.core_bytes import CommandSegment, DigiROM
	elif op in ["!BC"]:
		from dmcomm.protocol.core_digits import CommandSegment, DigiROM
	else:
		raise CommandError("op=" + op)
	if turn not in "012":
		raise CommandError("turn=" + turn)
	segments = [CommandSegment.from_string(part) for part in parts[1:]]
	return DigiROM(op, int(turn), segments)

class OtherCommand:
	def __init__(self, op, param):
		self.op = op
		self.param = param

class BaseDigiROM:
	"""Base class for describing the communication and recording the results.
	"""
	def __init__(self, result_segment_class, physical, turn, segments=[]):
		self.result_segment_class = result_segment_class
		self.physical = physical
		self.turn = turn
		self._segments = segments
		self.result = None
	def append(self, c):
		self._segments.append(c)
	def prepare(self):
		self.result = Result(self.physical, 0)
		self._command_index = 0
	def send(self):
		if self._command_index >= len(self._segments):
			return None
		c = self._segments[self._command_index]
		self._command_index += 1
		self.result.append(self.result_segment_class(True, c.data))
		return c.data
	def receive(self, data):
		self.result.append(self.result_segment_class(False, data))
	def __len__(self):
		return len(self._segments)

class Result:
	"""Describes the result of the communication.
	"""
	def __init__(self, physical, turn):
		self.physical = physical
		self.turn = turn
		self._results = []
	def append(self, segment):
		self._results.append(segment)
	def __str__(self):
		"""Returns text formatted for the serial protocol."""
		return " ".join([str(r) for r in self._results])
