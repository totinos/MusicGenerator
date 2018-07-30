import sys
import struct


DEFAULT_MIDI_HEADER_SIZE = 14


class Pattern:
	def __init__(self, tracks=[], resolution=220, file_format):
		self.file_format = file_format
		self.resolution = resolution
		self.tracks = tracks
		print('P')


class Track:
	def __init__(self):
		print('T')


class Event:
	def __init__(self):
		print('E')


class MIDI:	
	
	def __init__(self):
		return

	def read_file(self, midi_file):
		try:
			with open(midi_file, 'rb') as f:	
				##### PARSE FILE HEADER #####
				chunk_id = f.read(4)
				if chunk_id != b'MThd':
					raise TypeError('\"{}\": Invalid MIDI file.'.format(midi_file))
				data = struct.unpack('>LHHH', f.read(10))
				header_size = data[0]
				file_format = data[1]
				num_tracks = data[2]
				print('Num tracks:', num_tracks)
				tracks = [Track() for x in range(num_tracks)]
				resolution = data[3]
				if header_size > DEFAULT_MIDI_HEADER_SIZE:
					f.read(header_size - DEFAULT_MIDI_HEADER_SIZE)
				pattern = Pattern(tracks, resolution, file_format)
				##### PARSE TRACKS #####
				for tracks in pattern.tracks:
					chunk_id = f.read(4)
					if chunk_id != b'MTrk':
						raise TypeError('\"{}\": Bad track header.'.format(chunk_id))
					track_size = struct.unpack('>L', f.read(4))[0]
					track_data = f.read(track_size)
		except TypeError as err:
			print(err)
		return

if __name__ == '__main__':
	filename = sys.argv[1]
	midi = MIDI()
	midi.read_file(name)
	print('FINISHED')