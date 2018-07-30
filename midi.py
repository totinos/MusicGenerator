import sys
import struct


DEFAULT_MIDI_HEADER_SIZE = 14


# This implementation assumes that there are only
# MThd and MTrk chunks in the file -- All other
# chunk IDs will cause the program to exit with
# a TypeError exception


class MIDI:	
	
	def __init__(self):
		print('Constructing MIDI object...')

		return

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
				for track in range(num_tracks):
					chunk_id = f.read(4)
					if chunk_id != b'MTrk':
						raise TypeError('\"{}\": Bad track header.'.format(chunk_id))
					track_size = struct.unpack('>L', f.read(4))[0]
					print(' track_size:', track_size)
					track_data = f.read(track_size)

		except TypeError as err:
			print(err)

		return

if __name__ == '__main__':
	filename = sys.argv[1]
	midi = MIDI()
	midi.read_file(filename)
	print('FINISHED')