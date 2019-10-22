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

# Microphone stream config.
CHUNK = 128  # CHUNKS of bytes to read each time from mic
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
THRESHOLD = 1000  # The threshold intensity that defines silence
                  # and noise signal (an int. lower than THRESHOLD is silence).

SILENCE_LIMIT = 1  # Silence limit in seconds. The max ammount of seconds where
                   # only silence is recorded. When this time passes the
                   # recording finishes and the file is delivered.

def listen_for_speech(threshold=THRESHOLD, num_phrases=-1):
    '''
    Listens to Microphone, extracts phrases from it and sends it to 
    Google's TTS service and returns response. a 'phrase' is sound 
    surrounded by silence (according to threshold). num_phrases controls
    how many phrases to process before finishing the listening process 
    (-1 for infinite). 
    '''

    #Open stream
    p = pyaudio.PyAudio()

    streamIn = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    cur_data = ''  # current chunk  of audio data
    rel = RATE/CHUNK
    # slid_win = deque(maxlen=int(SILENCE_LIMIT * rel))
    started = False
    n = num_phrases
    response = []

    if len(sys.argv) < 2:
        print('usage: python3 soundIO.py <.wav file> <threshold>')
        return

    # open the file for reading.
    wf = wave.open(sys.argv[1], 'rb')
    if len(sys.argv) == 3:
        THRESHOLD = int(sys.argv[2])
    
    data = []
    temp = wf.readframes(CHUNK)

    while temp:
        data.append(temp)
        temp = wf.readframes(CHUNK)

    data = bytes().join(data)
    
    # open stream based on the wave object which has been input.
    streamOut = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                       channels=wf.getnchannels(),
                       rate=wf.getframerate(),
                       output=True)

    while (num_phrases == -1 or n > 0):
        cur_data = streamIn.read(CHUNK, exception_on_overflow=False)
        # slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
        if (started is True):
            streamIn.stop_stream()
            print(time.time())

            streamOut.write(data)

            started = False
            streamIn.start_stream()

        # elif(sum([x > THRESHOLD for x in slid_win]) > 0):
        elif(math.sqrt(abs(audioop.avg(cur_data, 4))) > THRESHOLD):
            started = True

    streamIn.close()
    streamOut.close()
    p.terminate()

    return response

if(__name__ == '__main__'):
    listen_for_speech()  # listen to mic.
