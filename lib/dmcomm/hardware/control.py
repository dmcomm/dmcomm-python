# This file is part of the DMComm project by BladeSabre. License: MIT.

from dmcomm import CommandError
import dmcomm.protocol
from . import WAIT_REPLY
from . import pins

class Controller:
	"""Main class which controls the communication.

	The constructor takes no parameters.
	"""
	def __init__(self):
		self._digirom = None
		self._communicator = None
		self._prong_output = None
		self._prong_input = None
		self._ir_output = None
		self._ir_input_modulated = None
		self._ir_input_raw = None
		self._prong_comm = None
		self._ic_comm = None
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
		if self._ic_comm is None and self._ir_output is not None and self._ir_input_raw is not None:
			from . import ic
			self._ic_comm = ic.iC_Communicator(self._ir_output, self._ir_input_raw)
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
		c = dmcomm.protocol.parse_command(command)
		try:
			op = c.op
			raise NotImplementedError("op=" + op)
		except AttributeError:
			#It's a DigiROM
			self._digirom = c
			return f"{c.physical}{c.turn}-[{len(c)} packets]"
	def communicate(self) -> bool:
		"""Communicates with the toy as configured by `execute`.

		Does nothing if no communication pattern is configured.

		:returns: True if the receive delay was completed, False otherwise.
		:raises: `CommandError` if an error was found in the configured command.
		"""
		if self._digirom is not None:
			self._prepare(self._digirom.physical)
			turn = self._digirom.turn
			if turn in [0, 2]:
				if not self._received(3000):
					return True
			if turn == 0:
				while True:
					if not self._received(WAIT_REPLY):
						return False
			else:
				while True:
					data_to_send = self._digirom.send()
					if data_to_send is None:
						break
					self._communicator.send(data_to_send)
					if not self._received(WAIT_REPLY):
						break
			return False
	def _prepare(self, protocol: str) -> None:
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
		elif protocol == "!IC":
			if self._ir_output is None:
				raise CommandError("no infrared output registered")
			if self._ir_input_raw is None:
				raise CommandError("no raw infrared input registered")
			self._communicator = self._ic_comm
		elif protocol in ["!DL", "!FL"]:
			if self._ir_output is None:
				raise CommandError("no infrared output registered")
			if self._ir_input_modulated is None:
				raise CommandError("no modulated infrared input registered")
			self._communicator = self._modulated_comm
		else:
			raise NotImplementedError("protocol=" + protocol)
		self._communicator.enable(protocol)
		self._digirom.prepare()
	def _received(self, timeout_ms):
		received_data = self._communicator.receive(timeout_ms)
		self._digirom.receive(received_data)
		if received_data is None or received_data == []:
			return False
		return True
	def disable(self):
		if self._communicator is not None:
			self._communicator.disable()
			self._communicator = None
	def result(self):
		if self._digirom is not None:
			return self._digirom.result
		else:
			return None
