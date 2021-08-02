# This file is part of the DMComm project by BladeSabre. License: MIT.

class ProngCommunicator:
	def __init__(self, prong_output, prong_input):
		self._output = prong_output
		self._input = prong_input
		self._protocol = None
	def enable(self, protocol):
		self.disable()
		if protocol in ["V", "X"]:
			self._idle_state = True
		elif protocol == "Y":
			self._idle_state = False
		else:
			raise ValueError("protocol must be V/X/Y")
		try:
			self._output.enable(idle_state)
			self._input.enable()
		except:
			self.disable()
			raise
		self._protocol = protocol
	def disable(self):
		self._output.disable()
		self._input.disable()
		self._protocol = None
	def send(self, bits):
		pass
	def receive(self):
		pass
