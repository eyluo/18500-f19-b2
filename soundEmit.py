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

SILENCE_LIMIT = 1  # Silence limit in seconds. The max ammount of seconds where
# only silence is recorded. When this time passes the
# recording finishes and the file is delivered.


def listen_for_speech(num_phrases=-1):
    """
    Listens to Microphone, extracts phrases from it and sends it to
    Google's TTS service and returns response. a "phrase" is sound
    surrounded by silence (according to threshold). num_phrases controls
    how many phrases to process before finishing the listening process
    (-1 for infinite).
    """

    #Open stream
    p = pyaudio.PyAudio()

    cur_data = ''  # current chunk  of audio data
    rel = RATE/CHUNK
    slid_win = deque(maxlen=int(SILENCE_LIMIT * rel))
    started = False
    n = num_phrases
    response = []

    if len(sys.argv) < 3:
        print("usage: python3 soundIO.py <.wav file> <sleep_time>")
        return

    # open the file for reading.
    wf = wave.open(sys.argv[1], 'rb')
    if len(sys.argv) == 3:
        #THRESHOLD = int(sys.argv[2])
        SLEEP_TIME = int(sys.argv[2])

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

    input("press any key to start playing")

    while True:
        print(time.time())
        streamOut.write(data)
        time.sleep(SLEEP_TIME)

    streamOut.close()
    p.terminate()

    return response


if(__name__ == '__main__'):
    listen_for_speech()  # listen to mic.
