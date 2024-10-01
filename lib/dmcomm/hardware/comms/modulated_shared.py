# This file is part of the DMComm project by BladeSabre. License: MIT.

import array

from dmcomm import ReceiveError
from dmcomm.hardware import WAIT_REPLY, misc

def reverse_bits_8(x):
	y = 0
	for j in range(8):
		y <<= 1
		y |= (x & 1)
		x >>= 1
	return y

def send(output_pulses, params, bytes_to_send):
	if not params.low_byte_first:
		bytes_to_send = bytes_to_send[:]  #copy
	else:
		bytes_to_send = bytes_to_send[::-1]  #reversed copy
	if not params.low_bit_first:
		for i in range(len(bytes_to_send)):
			bytes_to_send[i] = reverse_bits_8(bytes_to_send[i])
	num_durations = len(bytes_to_send) * 16 + 4
	array_to_send = array.array("H")
	for i in range(num_durations):
		array_to_send.append(0)
		#This function would be simpler if we append as we go along,
		#but still hoping for a fix that allows reuse of the array.
	array_to_send[0] = params.start_pulse_send
	array_to_send[1] = params.start_gap_send
	buf_cursor = 2
	for current_byte in bytes_to_send:
		for j in range(8):
			array_to_send[buf_cursor] = params.bit_pulse_send
			buf_cursor += 1
			if current_byte & 1:
				array_to_send[buf_cursor] = params.bit_gap_send_long
			else:
				array_to_send[buf_cursor] = params.bit_gap_send_short
			buf_cursor += 1
			current_byte >>= 1
	array_to_send[buf_cursor] = params.stop_pulse_send
	array_to_send[buf_cursor + 1] = params.stop_gap_send
	output_pulses.send(array_to_send)

def receive(input_pulses, params, timeout_ms):
	pulses = input_pulses
	pulses.clear()
	pulses.resume()
	if timeout_ms == WAIT_REPLY:
		timeout_ms = params.reply_timeout_ms
	misc.wait_for_length_no_more(pulses, timeout_ms,
		params.packet_length_timeout_ms, params.packet_continue_timeout_ms)
	pulses.pause()
	if len(pulses) == pulses.maxlen:
		raise ReceiveError("buffer full")
	if len(pulses) == 0:
		return []
	bytes_received = []
	t_pulse = misc.pop_pulse(pulses, -2)
	t_gap = misc.pop_pulse(pulses, -1)
	t_total = t_pulse + t_gap
	if t_total < params.start_min or t_total > params.start_max:
		raise ReceiveError(f"start pulse={t_pulse} gap={t_gap} total={t_total}")
	current_byte = 0
	bit_count = 0
	while True:
		t_pulse = misc.pop_pulse(pulses, 2*bit_count+1)
		if len(pulses) == 0:
			# Stop pulse?
			if t_pulse < params.stop_pulse_min or t_pulse > params.stop_pulse_max:
				raise ReceiveError(f"last pulse (bit {bit_count}) = {t_pulse}")
			else:
				# We are done
				break
		t_gap = pulses.popleft()
		t_total = t_pulse + t_gap
		if t_total < params.bit_min or t_total > params.bit_max:
			raise ReceiveError(f"bit {bit_count} pulse={t_pulse} gap={t_gap} total={t_total}")
		current_byte >>= 1
		if t_total > params.bit_threshold:
			current_byte |= 0x80
		bit_count += 1
		if bit_count % 8 == 0:
			bytes_received.append(current_byte)
			current_byte = 0
	if bit_count % 8 != 0:
		raise ReceiveError("bit_count = %d" % bit_count)
	if params.low_byte_first:
		bytes_received.reverse()
	if not params.low_bit_first:
		for i in range(len(bytes_received)):
			bytes_received[i] = reverse_bits_8(bytes_received[i])
	return bytes_received
