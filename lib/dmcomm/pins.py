# This file is part of the DMComm project by BladeSabre. License: MIT.

class ProngOutput:
	def __init__(self, pin_drive_signal, pin_weak_pull):
		#pin_drive_low must be pin_drive_signal+1
		self.pin_drive_signal = pin_drive_signal
		self.pin_weak_pull = pin_weak_pull

class ProngInput:
	def __init__(self, pin_input):
		self.pin_input = pin_input
