# This file is part of the DMComm project by BladeSabre. License: MIT.

class ProngOutput:
	"""Description of the outputs for the RP2040 prong circuit.

	:param pin_drive_signal: The first pin to use for signal output.
		Note that `pin_drive_low=pin_drive_signal+1` due to the rules of PIO.
	:param pin_weak_pull: The pin to use for the weak pull-up / pull-down.
	"""
	def __init__(self, pin_drive_signal, pin_weak_pull):
		#pin_drive_low must be pin_drive_signal+1
		self.pin_drive_signal = pin_drive_signal
		self.pin_weak_pull = pin_weak_pull

class ProngInput:
	"""Description of the input for the RP2040 prong circuit.

	:param pin_input: The pin to use for input.
		An analog pin is recommended for compatibility with the Arduino version
		and for a possible future voltage test.
	"""
	def __init__(self, pin_input):
		self.pin_input = pin_input

class InfraredOutput:
	"""Description of the infrared LED output.

	:param pin_output: The pin to use for output.
	"""
	def __init__(self, pin_output):
		self.pin_output = pin_output

class InfraredInputModulated:
	"""Description of the modulated infrared input (TSOP4838 recommended).

	:param pin_input: The pin to use for input.
	"""
	def __init__(self, pin_input):
		self.pin_input = pin_input

class InfraredInputRaw:
	"""Description of the non-modulated infrared input (TSMP58000 recommended).

	:param pin_input: The pin to use for input.
	"""
	def __init__(self, pin_input):
		self.pin_input = pin_input

class TalisOutput:
	"""Description of the Talispod/dam output.

	:param pin_output: The pin to use for output.
	"""
	def __init__(self, pin_output):
		self.pin_output = pin_output

class TalisInput:
	"""Description of the Talispod/dam input.

	:param pin_input: The pin to use for input.
	"""
	def __init__(self, pin_input):
		self.pin_input = pin_input
