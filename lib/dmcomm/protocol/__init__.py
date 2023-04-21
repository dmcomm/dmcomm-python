# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol`
=================

Protocol handling for Digimon toys.

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
	if op in ["D", "T", "?"]:
		return OtherCommand(op, turn)
	elif op in ["V", "X", "Y", "IC"]:
		from dmcomm.protocol.core16 import CommandSegment, DigiROM
	elif op in ["C"]:
		from dmcomm.protocol.core_words import CommandSegment, DigiROM
	elif op in ["!DL", "FL", "LT"]:
		from dmcomm.protocol.core_bytes import CommandSegment, DigiROM
	elif op in ["BC"]:
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
	def __init__(self, result_segment_class, signal_type, turn, segments=None):
		self.result_segment_class = result_segment_class
		self.signal_type = signal_type
		self.turn = turn
		self._segments = [] if segments is None else segments
		self.result = None
	def append(self, c):
		self._segments.append(c)
	def prepare(self):
		self.result = Result(self.signal_type)
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
	def __getitem__(self, i):
		return self._segments[i]

class Result:
	"""Describes the result of the communication.
	"""
	def __init__(self, signal_type):
		self.signal_type = signal_type
		self._results = []
	def append(self, segment):
		self._results.append(segment)
	def __len__(self):
		return len(self._results)
	def __getitem__(self, i):
		return self._results[i]
	def __str__(self):
		"""Returns text formatted for the serial protocol."""
		return " ".join([str(r) for r in self._results])

class ResultView:
	"""Describes the result of one side of the communication.

	:param result: The Result to view.
	:param turn: 1 for the side who went first, 2 for the side who went second.
	"""
	def __init__(self, result, turn):
		self._result = result
		self._turn = turn
		if turn == 2:
			self._turn_index = 1
		else:
			self._turn_index = 0
	def __getitem__(self, i):
		return self._result[2 * i + self._turn_index]
