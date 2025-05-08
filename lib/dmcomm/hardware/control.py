# This file is part of the DMComm project by BladeSabre. License: MIT.

from dmcomm import CommandError
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
		self._talis_input_output = None
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
		if isinstance(io_object, pins.TalisInputOutput):
			self._talis_input_output = io_object
	def execute(self, digirom) -> None:
		"""Carries out the communication specified.

		:param digirom: The DigiROM to execute.
		:raises CommandError: If the required pins for the selected signal type are not registered.
		:raises ReceiveError: If a broken transmission was received.
		"""
		self._digirom = digirom
		try:
			self._prepare()
			if digirom.turn in [0, 2]:
				if not self._received(5000):
					return
			if digirom.turn == 0:
				while True:
					if not self._received(WAIT_REPLY):
						return
			else:
				while True:
					data_to_send = self._digirom.next()
					if data_to_send is None:
						return
					self._communicator.send(data_to_send)
					if not self._received(WAIT_REPLY):
						return
		finally:
			self._digirom = None
	def _prepare(self):
		"""Prepares for a single interaction.
		"""
		signal_type = self._digirom.signal_type
		self._digirom.prepare()
		if self._communicator is not None:
			try:
				self._communicator.enable(signal_type)
				return
			except ValueError:
				self._disable()  # going to create a new communicator
		if signal_type in ["V", "X", "Y", "C", "MW"]:
			if self._prong_output is None:
				raise CommandError("no prong output registered")
			if self._prong_input is None:
				raise CommandError("no prong input registered")
			if signal_type == "C":
				from .comms import color
				comm = color.ColorCommunicator(self._prong_output, self._prong_input)
			elif signal_type == "MW":
				from .comms import witches
				comm = witches.WitchesCommunicator(self._prong_output, self._prong_input)
			else:
				from .comms import classic
				comm = classic.ClassicCommunicator(self._prong_output, self._prong_input)
		elif signal_type in ["IC"]:
			if self._ir_output is None:
				raise CommandError("no infrared output registered")
			if self._ir_input_raw is None:
				raise CommandError("no raw infrared input registered")
			from .comms import ic
			comm = ic.iC_Communicator(self._ir_output, self._ir_input_raw)
		elif signal_type in ["!XL"]:
			if self._ir_output is None:
				raise CommandError("no infrared output registered")
			if self._ir_input_raw is None:
				raise CommandError("no raw infrared input registered")
			from .comms import xloader
			comm = xloader.XLoaderCommunicator(self._ir_output, self._ir_input_raw)
		elif signal_type in ["DL", "FL"]:
			if self._ir_output is None:
				raise CommandError("no infrared output registered")
			if self._ir_input_modulated is None:
				raise CommandError("no modulated infrared input registered")
			from .comms import modulated
			comm = modulated.ModulatedCommunicator(self._ir_output, self._ir_input_modulated)
		elif signal_type in ["LT"]:
			if self._talis_input_output is None:
				raise CommandError("no talis pin registered")
			from .comms import talis
			comm = talis.TalisCommunicator(self._talis_input_output)
		elif signal_type in ["BC"]:
			if self._ir_output is None:
				raise CommandError("no infrared output registered")
			from .comms import barcode
			comm = barcode.BarcodeCommunicator(self._ir_output)
		else:
			raise CommandError("signal_type=" + signal_type)
		comm.enable(signal_type)
		self._communicator = comm
	def _received(self, timeout_ms):
		received_data = self._communicator.receive(timeout_ms)
		self._digirom.store(received_data)
		if received_data is None or received_data == []:
			return False
		return True
	def _disable(self):
		if self._communicator is not None:
			self._communicator.disable()
			self._communicator = None
