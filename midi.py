
#####################################################################
#                                                                   #
#  FILENAME -- midi.py                                              #
#                                                                   #
#  CREATED  -- July 30, 2018                                        #
#                                                                   #
#  AUTHOR   -- Sam Brown                                            #
#                                                                   #
#  ACKNOWLEDGEMENTS -- This work draws upon the works of both       #
#                      Giles F. Hall (which is protected under the  #
#                      MIT License, 2013), and of colxi (which is   #
#                      protected under the GNU General Public       #
#                      License, v3.0).                              #
#                                                                   #
#####################################################################


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

  ########################
  #
  # Need to check for EOF every time one of these reading functions is used
  #
  ########################

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

          #
          # Read events until the end of the current track is reached
          #
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

            # print('SB:', status_byte)


            #
            # Classify as meta event or other and read data accordingly
            #
            if status_byte == 0xFF:
              self.tracks[t].events[ec].type = 0xFF
              meta_type = self.read_int(1)
              meta_length = self.read_vlv()
              self.tracks[t].events[ec].meta_type = meta_type

              # print('. meta_type:', meta_type)
              # print('. meta_length:', meta_length)
              if meta_type == 0x2F:
                end_of_track = True
              elif (meta_type == 0x01 or meta_type == 0x02 or
                    meta_type == 0x03 or meta_type == 0x06):
                self.tracks[t].events[ec].data = self.read_str(meta_length)
              elif (meta_type == 0x21 or meta_type == 0x59 or
                    meta_type == 0x51):
                self.tracks[t].events[ec].data = self.read_int(meta_length)
              elif meta_type == 0x54:
                self.tracks[t].events[ec].data = []
                for i in range(0, 5):
                  self.tracks[t].events[ec].data.append(self.read_int(1))
              elif meta_type == 0x58:
                self.tracks[t].events[ec].data = []
                for i in range(0, 4):
                  self.tracks[t].events[ec].data.append(self.read_int(1))
              else:
                print('DEFAULT META CASE HANDLED.')

            #
            # NOT a meta event, treat as sysex or other event type
            #
            else:
              event_type = status_byte >> 4
              channel = status_byte & 0x0F
              # print('ET', event_type)
              # print('Ch', channel)
              self.tracks[t].events[ec].type = event_type
              self.tracks[t].events[ec].channel = channel ### Not defined but it still works?

              if event_type == 0xF:
                print('Sysex event.')
              elif (event_type == 0xA or event_type == 0xB or
                    event_type == 0xE or event_type == 0x8 or
                    event_type == 0x9):
                self.tracks[t].events[ec].data = []
                for i in range(0, 2):
                  self.tracks[t].events[ec].data.append(self.read_int(1))
              elif (event_type == 0xC or event_type == 0xD):
                self.tracks[t].events[ec].data = self.read_int(1)
              else:
                print('DEFAULT REG CASE HANDLED')

            # Increment the number of events encountered thus far
            ec += 1

        
          print('Finished reading track.')
          # print(self.tracks[t].events)

        
    except TypeError as err:
      print(err)

    return

if __name__ == '__main__':
  filename = sys.argv[1]
  midi = MIDI()
  midi.read_file(filename)
  print('FINISHED')