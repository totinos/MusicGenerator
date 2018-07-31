import sys
import struct


DEFAULT_MIDI_HEADER_SIZE = 14


# This implementation assumes that there are only
# MThd and MTrk chunks in the file -- All other
# chunk IDs will cause the program to exit with
# a TypeError exception


#
# CLASS to store information about a MIDI track
#
class Track:
	def __init__(self):
		self.events = []
		print(' Creating track')
		return

#
# CLASS to store information about a MIDI event
#
class Event:
	def __init__(self):
		self.data = None
		self.delta_time = None
		self.meta_type = None
		self.type = None
		# print('  Creating event')
		return

#
# CLASS to read a MIDI file into memory
#
class MIDI:	
	
	def __init__(self):
		self.tracks = []
		self.track_size = 0
		self.track_data = None
		self.pointer = 0
		print('Constructing MIDI object...')
		return

	#
	# FUNCTION to read a certain number of bytes of track data
	#
	def read_data(self, num_bytes):
		start = self.pointer
		end = self.pointer + num_bytes
		if end <= self.track_size:
			data = self.track_data[start:end]
			self.pointer += num_bytes
		return data

	#
	# FUNCTION to read a variable length value
	#
	def read_vlv(self):
		value = 0
		cont = True # Value continues to next byte
		while cont:
			# char = track_data[self.pointer]
			char = int.from_bytes(self.read_data(1), 'big')
			# self.pointer += 1

			print(type(char))

			if not (char & 0x80):
				cont = False
			char = char & 0x7F
			value = value << 7
			value += char
		return value

	#
	# FUNCTION to read a MIDI file
	#
	def read_file(self, midi_file):
		try:
			with open(midi_file, 'rb') as f:	
				
				##### PARSE FILE HEADER CHUNK #####
				chunk_id = f.read(4)
				if chunk_id != b'MThd':
					raise TypeError('\"{}\": File header chunk not found.'.format(midi_file))
				data = struct.unpack('>LHHH', f.read(10))
				header_size = data[0]
				file_format = data[1]
				num_tracks = data[2]
				print('Num tracks:', num_tracks)
				resolution = data[3]
				if header_size > DEFAULT_MIDI_HEADER_SIZE:
					f.read(header_size - DEFAULT_MIDI_HEADER_SIZE)

				##### PARSE ALL OTHER CHUNKS #####
				for t in range(num_tracks):
					chunk_id = f.read(4)
					if chunk_id == '':
						break # EOF reached...
					elif chunk_id != b'MTrk':
						raise TypeError('\"{}\": Bad track header.'.format(chunk_id))
					# track_size = struct.unpack('>L', f.read(4))[0]
					# print(' track_size:', track_size)
					# track_data = f.read(track_size)
					self.track_size = struct.unpack('>L', f.read(4))[0]
					self.track_data = f.read(self.track_size)
					self.pointer = 0
					# print(track_data[0])
					# print(track_data[1])
					self.tracks.append(Track())

					ec = 0 # Event counter
					end_of_track = False
					status_byte = None
					last_status_byte = None
					while not end_of_track:

						# Add a new event to the track's event list
						self.tracks[t].events.append(Event())
						self.tracks[t].events[ec].delta_time = self.read_vlv()
						print(self.tracks[t].events[ec].delta_time)

						# Get the event's status and compare it to the previous status
						
						# status_byte = track_data[pointer]
						# self.pointer += 1

						status_byte = self.read_data(1)

						if status_byte == '':
							break # EOF Reached
						elif status_byte >= 128:
							last_status_byte = status_byte # New status detected
						else:
							status_byte = last_status_byte # No new status, reset pointer
							self.pointer -= 1

						# META event detected
						if status_byte == 0xFF:
							self.tracks[t].events[ec].type = 0xFF
							
							# meta_type = track_data[self.pointer]
							# self.pointer += 1

							meta_type = self.read_data(1)
							
							self.tracks[t].events[ec].meta_type = meta_type
							meta_length = read_vlv()

							if 0x2F == meta_type:
								print(meta_type)

						


						ec += 1

						if ec == 100:
							end_of_track = True

					print('Events:', ec)


		except TypeError as err:
			print(err)

		return

if __name__ == '__main__':
	filename = sys.argv[1]
	midi = MIDI()
	midi.read_file(filename)
	print('FINISHED')