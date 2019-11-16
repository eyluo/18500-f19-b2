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
THRESHOLD_MSE = 1400
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
        t2 = time.time()
        ref_data.append(audio_data[0])
        print("Loading data:", t2 - t1)

    print(ref_data)

    t1 = time.time()
    print("Loaded reference data in {}...".format(t1 - t0))

    lowest_dtw_dist = float('inf')
    while (num_phrases == -1 or n > 0):
        cur_data = streamIn.read(CHUNK, exception_on_overflow=False)
        t0 = time.time()
        np_data = np.array(list(cur_data), dtype=np.float32)

        if (started is True):
            streamIn.stop_stream()

            clip_mfcc = librosa.feature.mfcc(np_data)
            for dt in ref_data[1:]:
                # do mfcc before DTW
                ref_mfcc = librosa.feature.mfcc(dt)
                ref_resized = np.resize(ref_mfcc[:, 0], (20, 1))
                distance, path = fastdtw(ref_resized, clip_mfcc)
                # print("ref_mfcc {} {}".format(type(ref_mfcc), ref_mfcc.shape))
                # print("clip_mfcc {} {}".format(type(clip_mfcc), clip_mfcc.shape))
                # print("ref_mfcc_resized {} {}".format(type(ref_resized), ref_resized.shape))
                # print('DISTANCE {}'.format(distance))

                if (distance < lowest_dtw_dist):
                    lowest_dtw_dist = distance
            
            print("lowest dtw dist {}, threshold {}".format(lowest_dtw_dist, THRESHOLD_MSE))
            if (lowest_dtw_dist < THRESHOLD_MSE):
                streamOut.write(data)
                lowest_dtw_dist = float('inf')
                # Prevent infinite loop where speaker continues to detect itself
                print("hi")
                time.sleep(1)

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
