# This file is part of the DMComm project by BladeSabre. License: MIT.

# Reads file named on first command-line arg,
# replaces uppercase hex strings of at least 8 digits with bit-reversed version
# (across whole string so bytes reversed too), and outputs results to stdout.

import re, sys

pattern = "[0-9A-F]" * 8 + "+"

digit_mapping = {
	"0": "0", "1": "8", "2": "4", "3": "C",
	"4": "2", "5": "A", "6": "6", "7": "E",
	"8": "1", "9": "9", "A": "5", "B": "D",
	"C": "3", "D": "B", "E": "7", "F": "F",
}

def replacer(matchobj):
	digits = list(matchobj.group(0))
	digits.reverse()
	digits = [digit_mapping[d] for d in digits]
	return "".join(digits)

with open(sys.argv[1]) as f:
	text = f.read()

print(re.sub(pattern, replacer, text))
