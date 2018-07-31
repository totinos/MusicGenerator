import os
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
# TODO --> MODIFY
# CLASS to read a MIDI file into memory
#
class MIDI:	
	
	def __init__(self):
		self.tracks = []
		self.track_size = 0

		self.file_size = 0
		self.file_data = None
		self.pointer = 0

		print('Constructing MIDI object...')
		return

	# TODO --> Add error checking to this function
	def read_str(self, num_bytes):
		start = self.pointer
		end = self.pointer + num_bytes
		data = self.file_data[start:end]
		self.pointer += num_bytes
		return data.decode('ASCII')

	# TODO --> Add error checking to this function
	def read_int(self, num_bytes):
		start = self.pointer
		end = self.pointer + num_bytes
		data = self.file_data[start:end]
		self.pointer += num_bytes
		return int.from_bytes(data, byteorder='big')

	# TODO --> MODIFY
	# FUNCTION to read a variable length value
	def read_vlv(self):
		value = 0
		cont = True # Value continues to next byte
		while cont:
			# char = track_data[self.pointer]
			char = self.read_int(1)
			# self.pointer += 1
			if not (char & 0x80):
				cont = False
			char = char & 0x7F
			value = value << 7
			value += char
		return value

	#
	# TODO --> MODIFY
	# FUNCTION to read a MIDI file
	#
	def read_file(self, midi_file):
		try:

			self.file_size = os.path.getsize(midi_file)
			print(self.file_size)
			with open(midi_file, 'rb') as f:

				self.file_data = f.read(self.file_size)
				chunk_id = self.read_str(4)
				if chunk_id != 'MThd':
					raise TypeError('\"{}\": MThd chunk not found.'.format(midi_file))
				header_size = self.read_int(4)
				# print(header_size)
				file_format = self.read_int(2)
				# print(file_format)
				num_tracks = self.read_int(2)
				# print(num_tracks)
				resolution = self.read_int(2)
				# print(resolution)

				if header_size > DEFAULT_MIDI_HEADER_SIZE:
					self.read_int(header_size - DEFAULT_MIDI_HEADER_SIZE) # Read misc bytes

				#
				# Go through all tracks and add events
				#
				for t in range(num_tracks):
					chunk_id = self.read_str(4)
					print(chunk_id)
					if chunk_id != 'MTrk':
						raise TypeError('\"{}\": MTrk chunk corrupted.'.format(midi_file))
					self.track_size = self.read_int(4)
					print(self.track_size)
					self.tracks.append(Track())

					ec = 0
					end_of_track = False
					status_byte = None
					last_status_byte = None
					while not end_of_track:

						# Add a new event to the track's event list
						self.tracks[t].events.append(Event())
						self.tracks[t].events[ec].delta_time = self.read_vlv()
						# print(self.tracks[t].events[ec].delta_time)

						status_byte = self.read_int(1)
						if status_byte >= 128:
							last_status_byte = status_byte
						else:
							status_byte = last_status_byte
							self.pointer -= 1

						ec += 1
						if ec == 100:
							end_of_track = True

					# self.read_int(self.track_size) # Read the whole track to get it out of the way
				
				exit(1)

				
				##### OLD FILE MATERIAL #####


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