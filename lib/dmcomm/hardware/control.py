# This file is part of the DMComm project by BladeSabre. License: MIT.

from .misc import CommandError
from . import misc
from . import pins

class Controller:
	"""Main class which controls the communication.

	The constructor takes no parameters.
	"""
	def __init__(self):
		self._protocol = None
		self._turn = None
		self._data_to_send = []
		self._results = []
		self._communicator = None
		self._encoder = None
		self._prong_output = None
		self._prong_input = None
		self._ir_output = None
		self._ir_input_modulated = None
		self._ir_input_raw = None
		self._prong_comm = None
		self._prong_encoder = None
		self._ic_comm = None
		self._ic_encoder = None
		self._modulated_comm = None
	def register(self, io_object) -> None:
		"""Registers pins for a particular type of input or output.

		Each type should only be provided once.

		:param io_object: One of the `Input` or `Output` types provided.
		"""
		if isinstance(io_object, pins.ProngOutput):
			self._prong_output = io_object
		if isinstance(io_object, pins.ProngInput):
			self._prong_input = io_object
		if isinstance(io_object, pins.InfraredOutput):
			self._ir_output = io_object
		if isinstance(io_object, pins.InfraredInputModulated):
			self._ir_input_modulated = io_object
		if isinstance(io_object, pins.InfraredInputRaw):
			self._ir_input_raw = io_object
		if self._prong_comm is None and self._prong_output is not None and self._prong_input is not None:
			from . import prongs
			self._prong_comm = prongs.ProngCommunicator(self._prong_output, self._prong_input)
			from . import encoder16
			self._prong_encoder = encoder16.Encoder16(self._prong_comm)
		if self._ic_comm is None and self._ir_output is not None and self._ir_input_raw is not None:
			from . import ic
			self._ic_comm = ic.iC_Communicator(self._ir_output, self._ir_input_raw)
			from . import encoder16
			self._ic_encoder = encoder16.Encoder16(self._ic_comm)
		if self._modulated_comm is None and self._ir_output is not None and self._ir_input_modulated is not None:
			from . import modulated
			self._modulated_comm = modulated.ModulatedCommunicator(self._ir_output, self._ir_input_modulated)
	def execute(self, command: str) -> str:
		"""Carries out the command specified.

		See the serial codes documentation for details.
		Communication pattern commands configure the system to prepare for calling `communicate`.
		Config commands are executed immediately.

		:param command: The command to execute.
		:returns: A description of how the command was interpreted.
		:raises: `CommandError` if the command was incorrect.
		"""
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
	def communicate(self) -> bool:
		"""Communicates with the toy as configured by `execute`.

		Does nothing if no communication pattern is configured.

		:returns: True if the receive delay was completed, False otherwise.
		:raises: `CommandError` if an error was found in the configured command.
		"""
		if self._protocol is not None:
			self.prepare(self._protocol)
			if self._turn in [0, 2]:
				if not self._received(3000):
					return True
			if self._turn == 0:
				while True:
					if not self._received(misc.WAIT_REPLY):
						return False
			else:
				for item in self._data_to_send:
					self.send_hex(item)
					if not self._received(misc.WAIT_REPLY):
						break
			return False
	def prepare(self, protocol: str) -> None:
		"""Prepares for a single interaction using lower-level communication functions.

		Not needed if using `execute` and `communicate`.

		:param protocol: The protocol string from "V", "X", "Y", "!IC", "!DL", "!FL".
		"""
		self.disable()
		if protocol in ["V", "X", "Y"]:
			if self._prong_output is None:
				raise CommandError("no prong output registered")
			if self._prong_input is None:
				raise CommandError("no prong input registered")
			self._communicator = self._prong_comm
			self._encoder = self._prong_encoder
		elif protocol == "!IC":
			if self._ir_output is None:
				raise CommandError("no infrared output registered")
			if self._ir_input_raw is None:
				raise CommandError("no raw infrared input registered")
			self._communicator = self._ic_comm
			self._encoder = self._ic_encoder
		elif protocol in ["!DL", "!FL"]:
			if self._ir_output is None:
				raise CommandError("no infrared output registered")
			if self._ir_input_modulated is None:
				raise CommandError("no modulated infrared input registered")
			self._communicator = self._modulated_comm
			self._encoder = self._modulated_comm
		else:
			raise NotImplementedError("protocol=" + protocol)
		self._protocol = protocol
		self._communicator.enable(protocol)
		self._encoder.reset()
	def send_hex(self, text):
		(sent_data, sent_desc) = self._encoder.send_hex(text)
		self._results.append(sent_desc)
		return sent_data
	def receive(self, timeout_ms):
		(received_data, received_desc) = self._encoder.receive(timeout_ms)
		self._results.append(received_desc)
		return received_data
	def _received(self, timeout_ms):
		received_data = self.receive(timeout_ms)
		if received_data is None or received_data == []:
			return False
		return True
	def disable(self):
		self._protocol = None
		self._results = []
		if self._communicator is not None:
			self._communicator.disable()
			self._communicator = None
	def result(self):
		return " ".join(self._results)
