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
import numpy as np
import librosa
from fastdtw import fastdtw

# Microphone stream config.
CHUNK = 128  # CHUNKS of bytes to read each time from mic
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
THRESHOLD = 1000  # Cutoff for whether the sound is interpreted as noise or silence
SILENCE_LIMIT = 1  # Silence limit in seconds. The max ammount of seconds where
                   # only silence is recorded. When this time passes the
                   # recording finishes and the file is delivered.
THRESHOLD_MSE_MFCC = 1400
SAMPLES = "hey" # Folder to read reference data for error comparison from

def listen_for_speech(threshold=THRESHOLD, num_phrases=-1):
    '''
    Listens to Microphone, extracts audio sample of size CHUNK. If the audio amplitude
    is greater than THRESHOLD, then processes audio sample into MFCC data.
    num_phrases controls how many phrases to process before finishing the listening process (-1 for infinite). 

    Sample usage: [:~/18500-f19-b2] $ python3 demo-midpoint/soundOutput.py samples/cyrus.wav 1000
    python3 demo-midpoint/__pycache__/soundOutput.cpython-37.pyc cyrus/spencer_cyrus.wav 1000
    '''

    # Open stream
    p = pyaudio.PyAudio()

    streamIn = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    cur_data = ''  # current chunk of audio data
    rel = RATE/CHUNK
    started = False
    n = num_phrases
    response = []

    if len(sys.argv) < 2:
        print('usage: python3 soundIO.py <output.wav file> <threshold>')
        return

    # Open the output file for our jammer
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

    # Load all ref audio in samples/
    t0 = time.time()
    files = [f for f in os.listdir(SAMPLES) if os.path.isfile(os.path.join(SAMPLES, f))]
    ref_data = []
    
    for fp in files:
        fp = "{}/{}".format(SAMPLES,fp)
        print("File: {}".format(fp))
        t1 = time.time()
        audio_data = librosa.core.audio.load(fp)
        # a = type(audio_data[0])
        # print(type(audio_data[0]))
        t2 = time.time()
        ref_data.append(audio_data[0])
        # print(len(ref_data))
        # print("\n\n\n\n\n\n\n\n\n\n\n\n")
        print("Loading data:", t2 - t1)

    print(ref_data)
    # ref_data = np.array(ref_data, dtype=np.float32)

    t1 = time.time()
    print("Loaded reference data in {}...".format(t1 - t0))

    while (num_phrases == -1 or n > 0):
        cur_data = streamIn.read(CHUNK, exception_on_overflow=False)
        t0 = time.time()
        np_data = np.array(list(cur_data), dtype=np.float32)

        if (started is True):
            streamIn.stop_stream()

            # print(np_data)

            # Calculate lowest MFCC error from sample data
            # print(ref_data.shape)
            # for dt in np.nditer(ref_data):
                # print("YOOOOO = %d" % (dt))

            # i = 0
            # for dt in ref_data:
            dt = ref_data[0]
            # print("YOOOOO={}".format(dt))
            distance, path = fastdtw(np_data, dt)
            print("Path:", path[:50])
            print("End Path:", path[-50:])

            print("===")

            dt2 = ref_data[2]
            distance1, path1 = fastdtw(dt, dt2)
            print("Path1: ", path1[:50])
            print("End Path1: ", path1[-50:])

            return
                # i += 1

                # if (i == 2):
                #     return

            
            # if (lowest_mfcc_error < THRESHOLD_MSE_MFCC):
            #     streamOut.write(data)
            #     lowest_mfcc_error = float('inf')
            #     # Prevent infinite loop where speaker continues to detect itself
            #     time.sleep(1)

            started = False
            streamIn.start_stream()

        elif(math.sqrt(abs(audioop.avg(cur_data, 4))) > THRESHOLD):
            started = True

    streamIn.close()
    streamOut.close()
    p.terminate()

    return response

if(__name__ == '__main__'):
    listen_for_speech()  # listen to mic.
