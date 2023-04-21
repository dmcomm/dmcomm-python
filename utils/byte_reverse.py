# This file is part of the DMComm project by BladeSabre. License: MIT.

# Reads file named on first command-line arg,
# replaces uppercase hex strings of at least 8 digits with byte-reversed version,
# and outputs results to stdout.

import re, sys

pattern = "[0-9A-F]" * 8 + "+"

def replacer(matchobj):
	matched_text = matchobj.group(0)
	bytes_ = [matched_text[i*2:i*2+2] for i in range(len(matched_text) // 2)]
	bytes_.reverse()
	result_text = "".join(bytes_)
	if len(matched_text) % 2 != 0:
		result_text = matched_text[-1] + "!!!" + result_text
	return result_text

with open(sys.argv[1]) as f:
	text = f.read()

print(re.sub(pattern, replacer, text))
