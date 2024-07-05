import io
import pygame
from pretty_midi import note_name_to_number
from midiutil.MidiFile import MIDIFile
import wave
from .constants import KEYS, INSTRUMENTS, PERCUSSION


def make_first_number_match_key(y_values, notes_in_key):
    first_note_in_key = notes_in_key[0]
    transpose_value = first_note_in_key - y_values[0]
    new_y = []
    for y in y_values:
        new_y.append(y + transpose_value)
    return new_y

def convert_to_key(data, key, number_of_octaves=4,
                   octave_start=1,
                   minmaxvalue=None):
    instrument, instrument_type = None, None
    if type(data[0]) != tuple:
        instrument = data.pop(0)
        _, instrument_type = get_instrument(instrument)

    x, y = zip(*data)

    if instrument_type == 'percussion':
        new_y = y
    else:
        # Finding the index of the note closest to all the notes in the options list
        notes_in_key = key_name_to_notes(key, number_of_octaves=number_of_octaves)

        # FBB July 17 2022
        if minmaxvalue is not None:
            if minmaxvalue[1] <= -1:
                notes_in_key = notes_in_key[minmaxvalue[0]:minmaxvalue[1]]
            else:
                notes_in_key = notes_in_key[minmaxvalue[0]:]


        transposed_y = make_first_number_match_key(y, notes_in_key)
        scaled_y = scale_list_to_range(transposed_y, new_min=min(notes_in_key), new_max=max(notes_in_key))

        new_y = []
        for note in scaled_y:
            new_y.append(get_closest_midi_value(note, notes_in_key))

    processed_data = list(zip(x, new_y))

    if instrument:
        processed_data = [instrument] + processed_data

    return processed_data

def key_name_to_notes(key, octave_start=1, number_of_octaves=4):
    """ Convert a key name to notes, using C3=60

    :param key: String matching one of the values in pre-defined KEY dict
    :param octave_start: octave for the first note, as defined by C3=60
    :param number_of_octaves: The number of octaves to include in the list
    :return:
    """
    key = KEYS.get(key)
    if not key:
        raise ValueError('No key by that name found')

    notes = []
    octave = octave_start + 1
    while len(notes) < number_of_octaves * 7:
        for note in key:
            note_with_octave = note + str(octave)
            note_number = note_name_to_number(note_with_octave)
            if note_number % 12 == 0 and len(notes) != 0:
                octave += 1
                note_with_octave = note + str(octave)
                note_number = note_name_to_number(note_with_octave)
            notes.append(note_number)

    return notes


def get_closest_midi_value(value, possible_values):
    return sorted(possible_values, key=lambda i: abs(i - value))[0]


def scale_y_to_midi_range(data, new_min=0, new_max=127):
    """
    midi notes have a range of 0 - 127. Make sure the data is in that range
    data: list of tuples of x, y coordinates for pitch and timing
    min: min data value, defaults to 0
    max: max data value, defaults to 127
    return: data, but y normalized to the range specified by min and max
    """
    if new_min < 0 or new_max > 127:
        raise ValueError('Midi notes must be in a range from 0 - 127')

    x, y = zip(*data)
    new_y = scale_list_to_range(y, new_min, new_max)

    return list(zip(x, new_y))


def scale_list_to_range(list_to_scale, new_min, new_max):
    old_min = min(list_to_scale)
    old_max = max(list_to_scale)
    return [get_scaled_value(value, old_min, old_max, new_min, new_max)
            for value in list_to_scale]


def get_scaled_value(old_value, old_min, old_max, new_min, new_max):
    return ((old_value - old_min)/(old_max - old_min)) * (new_max - new_min) + new_min


def quantize_x_value(list_to_quantize, steps=0.5):
    # Restrict the x range to something that's a  multiple of the number of steps given!
    quantized_x = []
    for x in list_to_quantize:
        quantized_x.append(round(steps * round(float(x) / steps), 2))
    return quantized_x


def get_instrument(instrument_name):
    instrument_type = 'melodic'
    program_number = INSTRUMENTS.get(instrument_name.lower())
    if not program_number:
        program_number = PERCUSSION.get(instrument_name.lower())
        instrument_type = 'percussion'
        if not program_number:
            raise AttributeError('No instrument or percussion could be found by that name')
    return program_number - 1, instrument_type


#RWC 7/22 - added notebook kwarg to write_to_midifile
def write_to_midifile(data, track_type='single', volume=90, tempo=120, duration=1, colab=False):
    """
    data: list of tuples of x, y coordinates for pitch and timing
          Optional: add a string to the start of the data list to specify instrument!
    type: the type of data passed to create tracks. Either 'single' or 'multiple'
    """
    if track_type not in ['single', 'multiple']:
        raise ValueError('Track type must be single or multiple')

    if track_type == 'single':
        data = [data]

    memfile = io.BytesIO()
    midifile = MIDIFile(numTracks=len(data), adjust_origin=False)

    track = 0
    time = 0
    program = 0
    channel = 0
    #duration = 1
    #volume = 90
    #print(len(volume[0]))
    for i,data_list in enumerate(data): #loop over tracks
        midifile.addTrackName(track, time, 'Track {}'.format(track))
        midifile.addTempo(track, time, tempo)

        instrument_type = 'melodic'
        if type(data_list[0]) != tuple:
            program, instrument_type = get_instrument(data_list.pop(0))

        if instrument_type == 'percussion':
            #print("now")
            #FBB 7/18/22 removed volume=100 so drums can be at different volume
            # volume = 100
            channel = 9
            
        # Write the notes we want to appear in the file
        for j,point in enumerate(data_list): #loop over note
            time = point[0]
            pitch = int(point[1]) if instrument_type == 'melodic' else program
            if isinstance(volume, int):
                midifile.addNote(track, channel, pitch, time, duration, volume)
            else:
                midifile.addNote(track, channel, pitch, time,
                                 duration, volume[i][j])                
            midifile.addProgramChange(track, channel, time, program)

        track += 1
        channel = 0

    midifile.writeFile(memfile)

    ###RWC edit 7/22 to save midi file to working dir
    #if colab:
    print("Saving to midi file")
    with open("midioutput.mid", 'wb') as binfile:
        midifile.writeFile(binfile)

    return memfile

#RWC 7/22 - added verbose kwarg
def play_memfile_as_midi(memfile, verbose=False):
    # https://stackoverflow.com/questions/27279864/generate-midi-file-and-play-it-without-saving-it-to-disk
    #RWC 7/22 - moved pyaudio import here - it is not compatible with colab
    import pyaudio
    pygame.init()
    pygame.mixer.init()
    memfile.seek(0)
    pygame.mixer.music.load(memfile)
    pygame.mixer.music.play()

    sample_rate = 44100         # Sample rate used for WAV/MP3
    channels = 1             # Audio channels (1 = mono, 2 = stereo)
    buffer = 2048               # Audio buffer size
    input_device = 0     

    format = pyaudio.paInt16
    audio = pyaudio.PyAudio()

    stream = audio.open(format=format, channels=channels,
                        rate=sample_rate, input=True, 
                        input_device_index=input_device, frames_per_buffer=buffer)
    frames = []

    while pygame.mixer.music.get_busy():
        frames.append(stream.read(buffer,exception_on_overflow=False))
        #sleep(1)
    
    if verbose: # FBB added July 22
        print("Done recording")
    stream.stop_stream()
    stream.close()
    # Configure wave file settings
    wave_file = wave.open("soundclip.wav", 'wb')
    wave_file.setnchannels(channels)
    wave_file.setsampwidth(audio.get_sample_size(format))
    wave_file.setframerate(sample_rate)
    if verbose:  # FBB added July 22
        print("Saving")
    
    # Write the frames to the wave file
    wave_file.writeframes(b''.join(frames))
    wave_file.close()
    audio.terminate()
    if verbose:  # FBB added July 22
        print('Done playing!')

# FBB add colab argument in input for colab compatibility
def play_midi_from_data(input_data, key=None, number_of_octaves=4,
                        track_type='single', octave_start=1,
                        volume=100, tempo=120, duration=1, colab=False, verbose=False):
    """
    input_data: a list of tuples, or a list of lists of tuples to add as separate tracks
    eg:
    input_data = [(1, 5), (5, 7)] OR
    input_data = [
        [(1, 5), (5, 7)],
        [(4, 7), (2, 10)]
    ]

    key: key to play back the graph -- see constants.py for current choices
    number_of_octaves: number of octaves used to restrict the music playback
     when converting to a key

    optional -- append an instrument name to the start of each data list
                to play back using that program number!
    """
    if key:
        if track_type == 'multiple':
            data = []
            if  isinstance(number_of_octaves, int):
                number_of_octaves = [number_of_octaves] * len(input_data)
            if  isinstance(octave_start, int):
                octave_start = [octave_start] * len(input_data)
            for i,data_list in enumerate(input_data):
                #print(number_of_octaves)

                data.append(convert_to_key(data_list, key,
                                           number_of_octaves[i],
                                           octave_start[i]))
        else:
            data = convert_to_key(input_data, key, number_of_octaves)
    else:
        data = input_data

    ### FBB change 07/22 to enable running on colab platform
    memfile = write_to_midifile(data, track_type, volume=volume, tempo=tempo,
                                duration=duration, colab=colab)
    if colab:
        return
    play_memfile_as_midi(memfile, verbose=verbose)

