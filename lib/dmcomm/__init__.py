# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm`
========
Communication with Digimon toys.

Note: This API is still under development and may change at any time.
"""

class CommandError(ValueError):
	"""Exception raised when an incorrect command is provided."""

class ReceiveError(Exception):
	"""Exception raised when a broken transmission is received."""
