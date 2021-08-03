# This file is part of the DMComm project by BladeSabre. License: MIT.

from .misc import CommandError
from . import misc
from . import pins

class Controller:
	def __init__(self):
		self._protocol = None
		self._turn = None
		self._data_to_send = []
		self._results = []
		self._communicator = None
		self._encoder = None
		self._prong_output = None
		self._prong_input = None
		self._prong_comm = None
		self._prong_encoder = None
	def register(self, io_object):
		if isinstance(io_object, pins.ProngOutput):
			self._prong_output = io_object
		if isinstance(io_object, pins.ProngInput):
			self._prong_input = io_object
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
			raise CommandError("op=" + op)
		elif turn not in "012":
			raise CommandError("turn=" + turn)
		self._protocol = op
		self._turn = int(turn)
		self._data_to_send = parts[1:]
		return f"{op}{turn}-[{len(self._data_to_send)} packets]"
	def communicate(self):
		if self._protocol is not None:
			self.prepare(self._protocol)
			if self._turn in [0, 2]:
				if self.receive(3000) is None:
					return True
			if self._turn == 0:
				while True:
					if self.receive(misc.WAIT_REPLY) is None:
						return False
			else:
				for item in self._data_to_send:
					if self.send_code_segment(item) is None:
						break
					if self.receive(misc.WAIT_REPLY) is None:
						break
			return False
	def prepare(self, protocol):
		self.disable()
		if protocol in ["V", "X", "Y"]:
			if self._prong_output is None:
				raise CommandError("no prong output registered")
			if self._prong_input is None:
				raise CommandError("no prong input registered")
			self._communicator = self._prong_comm
			self._encoder = self._prong_encoder
		else:
			raise NotImplementedError("protocol=" + protocol)
		self._protocol = protocol
		self._communicator.enable(protocol)
		self._encoder.reset()
	def send_code_segment(self, text):
		(sent_data, sent_desc) = self._encoder.send_code_segment(text)
		self._results.append(sent_desc)
		return sent_data
	def receive(self, timeout_ms):
		(received_data, received_desc) = self._encoder.receive(timeout_ms)
		self._results.append(received_desc)
		return received_data
	def disable(self):
		self._protocol = None
		self._results = []
		if self._communicator is not None:
			self._communicator.disable()
			self._communicator = None
	def result(self):
		return " ".join(self._results)
