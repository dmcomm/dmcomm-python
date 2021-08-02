# This file is part of the DMComm project by BladeSabre. License: MIT.

from . import dmio

class Controller:
	def __init__(self):
		self._protocol = None
		self._communicator = None
		self._encoder = None
		self._prong_output = None
		self._prong_input = None
		self._prong_comm = None
		self._prong_encoder = None
	def register(self, io_object):
		if isinstance(io_object, dmio.ProngOutput):
			self._prong_output = io_object
		#...
		if self._prong_comm is None and self._prong_output is not None and self._prong_input is not None:
			from . import prongs
			self._prong_comm = prongs.ProngCommunicator(self._prong_output, self._prong_input)
			from . import encoder16
			self._prong_encoder = encoder16.Encoder16(self._prong_comm)
	def execute(self, command):
		parts = command.strip().upper().split("-")
		if len(parts[0]) >= 2:
			op = parts[0][:-1]
			turn = parts[0][-1]
		else:
			op = parts[0]
			turn = ""
		if op == "D":
			raise NotImplementedError("debug")
		elif op == "T":
			raise NotImplementedError("test")
		elif op not in ["V", "X", "Y", "!DL", "!FL", "!IC"]:
			raise ValueError("op=" + op)
		elif turn not in "012":
			raise ValueError("turn=" + turn)
		self._protocol = op
	def communicate(self):
		if self._protocol is None:
			raise ValueError("no protocol set")
		self.prepare(None)
		#...
	def prepare(self, protocol):
		if protocol is None:
			protocol = self._protocol
		self._protocol = None
		#TODO disable everything?
		if protocol in ["V", "X", "Y"]:
			if self._prong_output is None:
				raise ValueError("no prong output registered")
			if self._prong_input is None:
				raise ValueError("no prong input registered")
			self._communicator = self._prong_comm
			self._encoder = self._prong_encoder
		else:
			raise NotImplementedError("protocol=" + protocol)
		self._protocol = protocol
		self._communicator.enable(protocol)
		self._encoder.reset()

