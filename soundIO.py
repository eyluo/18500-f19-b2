import pyaudio
import wave
import audioop
from collections import deque
import os
import urllib
import time
import math
import sys

import time

LANG_CODE = 'en-US'  # Language to use

GOOGLE_SPEECH_URL = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=%s&maxresults=6' % (LANG_CODE)

FLAC_CONV = 'flac -f'  # We need a WAV to FLAC converter. flac is available
                       # on Linux

# Microphone stream config.
CHUNK = 1024  # CHUNKS of bytes to read each time from mic
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
THRESHOLD = 1000  # The threshold intensity that defines silence
                  # and noise signal (an int. lower than THRESHOLD is silence).

SILENCE_LIMIT = 1  # Silence limit in seconds. The max ammount of seconds where
                   # only silence is recorded. When this time passes the
                   # recording finishes and the file is delivered.

PREV_AUDIO = 0.5  # Previous audio (in seconds) to prepend. When noise
                  # is detected, how much of previously recorded audio is
                  # prepended. This helps to prevent chopping the beggining
                  # of the phrase.


def audio_int(num_samples=50):
    """ Gets average audio intensity of your mic sound. You can use it to get
        average intensities while you're talking and/or silent. The average
        is the avg of the 20% largest intensities recorded.
    """

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    values = [math.sqrt(abs(audioop.avg(stream.read(CHUNK), 4))) 
              for x in range(num_samples)] 
    values = sorted(values, reverse=True)
    r = sum(values[:int(num_samples * 0.2)]) / int(num_samples * 0.2)
    stream.close()
    p.terminate()
    return r


def listen_for_speech(threshold=THRESHOLD, num_phrases=-1):
    """
    Listens to Microphone, extracts phrases from it and sends it to 
    Google's TTS service and returns response. a "phrase" is sound 
    surrounded by silence (according to threshold). num_phrases controls
    how many phrases to process before finishing the listening process 
    (-1 for infinite). 
    """

    #Open stream
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    audio2send = []
    cur_data = ''  # current chunk  of audio data
    rel = RATE/CHUNK
    slid_win = deque(maxlen=int(SILENCE_LIMIT * rel))
    #Prepend audio from 0.5 seconds before noise was detected
    prev_audio = deque(maxlen=int(PREV_AUDIO * rel))
    started = False
    n = num_phrases
    response = []

    if len(sys.argv) < 2:
        print("usage: python3 soundIO.py <.wav file>")
        return

    # open the file for reading.
    wf = wave.open(sys.argv[1], 'rb')

    while (num_phrases == -1 or n > 0):
        cur_data = stream.read(CHUNK)
        slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
        if (started is True):
            later = time.time()
            print(later - now)

            # create an audio object
            p = pyaudio.PyAudio()

            # open stream based on the wave object which has been input.
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            # read data (based on the chunk size)
            data = wf.readframes(CHUNK)

            # play stream (looping from beginning of file to the end)
            while data != '':
                # writing to the stream is what *actually* plays the sound.
                stream.write(data)
                data = wf.readframes(CHUNK)

            # cleanup stuff.
            stream.close()
            p.terminate()

            return
        elif(sum([x > THRESHOLD for x in slid_win]) > 0):
            print("starting to listen")
            now = time.time()
            if(not started):
                started = True
            audio2send.append(cur_data)
        else:
            prev_audio.append(cur_data)

    stream.close()
    p.terminate()

    return response


def save_speech(data, p):
    """ Saves mic data to temporary WAV file. Returns filename of saved 
        file """

    filename = 'output_'+str(int(time.time()))
    # writes data to WAV file
    data = ''.join(data)
    wf = wave.open(filename + '.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)  # TODO make this value a function parameter?
    wf.writeframes(data)
    wf.close()
    return filename + '.wav'


if(__name__ == '__main__'):
    listen_for_speech()  # listen to mic.
    #print stt_google_wav('hello.flac')  # translate audio file
    #audio_int()  # To measure your mic levels
