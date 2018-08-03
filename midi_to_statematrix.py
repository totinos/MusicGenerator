import sys
import midi
import numpy as np

lower_bound = 24
upper_bound = 102


#
# FUNCTION to convert MIDI file info into a state matrix
#
def midi_to_state_matrix(midi_file):

	m = midi.MIDI()
	m.read_file(midi_file)
	print(m.tracks)

	timeleft = [track.events[0].delta_time for track in m.tracks]

	posns = [0 for track in m.tracks]

	statematrix = []
	span = upper_bound - lower_bound
	time = 0

	state = [[0,0] for x in range(span)]
	statematrix.append(state)
	
	while True:
		if time % (m.resolution / 4) == (m.resolution / 8):
			# Crossed a note boundary. Create new state, defaulting to holding notes
			oldstate = state
			state = [[oldstate[x][0],0] for x in range(span)]
			statematrix.append(state)

		for i in range(len(timeleft)):
			# print('timeleft[{}]: {}'.format(i, timeleft[i]))
			while timeleft[i] == 0:
				track = m.tracks[i]
				pos = posns[i]
				event = track.events[pos]

				if event.type == 0x9 or event.type == 0x8:
					pitch = event.data[0]
					velocity = event.data[1]
					if (event.data[0] < lower_bound) or (pitch > upper_bound):
						pass
						print('Note {} at time {} out of bounds (ignoring).'.format(pitch, time))
					else:
						if event.type == 0x8 or velocity == 0:
							state[pitch-lower_bound] = [0, 0]
						else:
							state[pitch-lower_bound] = [1, 1]
				
				elif event.meta_type == 0x58:
					numerator = event.data[0]
					# If the time signature is non-4, then bail.
					if numerator not in (2, 4):
						return statematrix

				try:
					timeleft[i] = track.events[pos + 1].delta_time
					posns[i] += 1
				except IndexError:
					timeleft[i] = None

			if timeleft[i] is not None:
				timeleft[i] -= 1
		
		if all(t is None for t in timeleft):
			break

		time += 1

	return statematrix


#
# FUNCTION to convert a state matrix into MIDI file info
#
def state_matrix_to_midi(statematrix, midi_file):

	statematrix = np.asarray(statematrix)
	m = midi.MIDI()
	t = midi.Track()
	m.tracks.append(t)

	span = upper_bound - lower_bound
	time_scale = 55

	last_cmd_time = 0
	prevstate = [[0,0] for x in range(span)]

	for time, state in enumerate(statematrix + [prevstate[:]]):
		off_notes = []
		on_notes = []
		for i in range(span):
			n = state[i]
			p = prevstate[i]
			if p[0] == 1:
				if n[0] == 0:
					off_notes.append(i)
				elif n[1] == 1:
					off_notes.append(i)
					on_notes.append(i)
			elif n[0] == 1:
				on_notes.append(i)

		# Write all note off events to MIDI event list
		for note in off_notes:
			pitch = note + lower_bound
			delta_time = (time - last_cmd_time) * time_scale
			data = []
			data.append(pitch)
			event = midi.Event(data=data, delta_time=delta_time, etype=0x8)
			m.tracks[0].append(event)
			last_cmd_time = time

		# Write all note on events to MIDI event list
		for note in on_notes:
			pitch = note + lower_bound
			velocity = 40
			delta_time = (time - last_cmd_time) * time_scale
			data = []
			data.append(pitch)
			data.append(velocity)
			event = midi.Event(data=data, delta_time=delta_time, etype=0x9)
			m.tracks[0].append(event)
			last_cmd_time = time

		prevstate = state

	# Append an End of Track Event to the MIDI event list
	eot = midi.Event(delta_time=1, meta_type=0x2F, etype=0xFF)
	m.tracks[0].append(eot)

	# Write all events in MIDI event list to output file
	print('outputting...')


if __name__ == '__main__':
	mat = midi_to_state_matrix(sys.argv[1])
	print(mat)