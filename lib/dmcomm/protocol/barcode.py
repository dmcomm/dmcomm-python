# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol.barcode`
=========================

Functions for generating EAN-13 patterns.
"""

# https://en.wikipedia.org/wiki/International_Article_Number
_START_END = "101"
_CENTRE = "01010"
_CODES = {
	"L": ["0001101", "0011001", "0010011", "0111101", "0100011", "0110001", "0101111", "0111011", "0110111", "0001011"],
	"G": ["0100111", "0110011", "0011011", "0100001", "0011101", "0111001", "0000101", "0010001", "0001001", "0010111"],
	"R": ["1110010", "1100110", "1101100", "1000010", "1011100", "1001110", "1010000", "1000100", "1001000", "1110100"],
}
_SELECT = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG", "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]

def ean13_bits(barcode_number: list) -> str:
	result = [_START_END]
	selection = _SELECT[barcode_number[0]]
	for i in range(6):
		digit = barcode_number[i + 1]
		code = _CODES[selection[i]][digit]
		result.append(code)
	result.append(_CENTRE)
	for i in range(6):
		digit = barcode_number[i + 7]
		code = _CODES["R"][digit]
		result.append(code)
	result.append(_START_END)
	return "".join(result)

def run_lengths(seq) -> list:
	if len(seq) == 0:
		return []
	result = []
	prev = seq[0]
	count = 1
	for item in seq[1:]:
		if item == prev:
			count += 1
		else:
			result.append(count)
			count = 1
			prev = item
	result.append(count)
	return result

def ean13_lengths(barcode_number: list) -> list:
	return run_lengths(ean13_bits(barcode_number))
