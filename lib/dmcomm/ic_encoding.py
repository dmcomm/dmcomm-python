
START_SEQUENCE = [0xC0,0xC0,0xC0,0xC0,0xC0,0xC0,0xC0,0xC0,0xC0,0xC0,0xFF,0x13,0x70,0x70]

def redundancy_bits(x):
	"Calculates the 16 redundancy bits for 16 bits of data."
	result = 0x79B4
	mask = 0x19D8
	for i in range(16):
		if x & 1:
			result ^= mask
		x >>= 1
		mask <<= 1
		if mask >= 0x10000:
			mask ^= 0x10811
	return result

def encode(x):
	"Calculates the byte sequence for 16 bits of data."
	r = redundancy_bits(x)
	result = START_SEQUENCE[:]
	for byte_ in [x & 0xFF, (x & 0xFF00) >> 8, r & 0xFF, (r & 0xFF00) >> 8]:
		if byte_ == 0xC0:
			result.append(0x7D)
			result.append(0xE0)
		elif byte_ == 0xC1:
			result.append(0x7D)
			result.append(0xE1)
		else:
			result.append(byte_)
	result.append(0xC1)
	return result

def decode(bytes_, start_index=0):
	offset = 0
	bytes4 = []
	while True:
		i = start_index + offset
		if i >= len(bytes_):
			raise ValueError("ended unfinished")
		b1 = bytes_[i]
		if i <= len(bytes_) - 2:
			b2 = bytes_[i+1]
		else:
			b2 = None
		if offset < 14:
			target = START_SEQUENCE[offset]
			if b1 != target:
				raise ValueError("byte at position %d expected %02X, got %02X" % (offset, target, b1))
		elif b1 == 0x7D:
			if b2 == 0xE0:
				bytes4.append(0xC0)
			elif b2 == 0xE1:
				bytes4.append(0xC1)
			elif b2 is None:
				raise ValueError("ended unfinished")
			else:
				raise ValueError("bad escape sequence %02X %02X" % (b1, b2))
			offset += 1
		elif b1 == 0xC1:
			if b2 == 0xFF:
				offset += 1
			break
		else:
			bytes4.append(b1)
		offset += 1
	if len(bytes4) != 4:
		raise ValueError("length not 4: " + str(bytes4))
	x = bytes4[0] | (bytes4[1] << 8)
	r = bytes4[2] | (bytes4[3] << 8)
	r_calc = redundancy_bits(x)
	if r_calc != r:
		raise ValueError("redundancy bits for %04X expected %04X, got %04X" % (x, r_calc, r))
	return (x, offset + 1)
