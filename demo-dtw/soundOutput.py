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
import pdb

# Microphone stream config.
OUTPUT_CHUNK_SIZE = 128 # CHUNK for jamming sound
MIC_CHUNK_SIZE = 1024 # CHUNKS of bytes to read each time from mic
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
    Listens to Microphone, extracts audio sample of size OUTPUT_CHUNK_SIZE. If the audio amplitude
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
                    frames_per_buffer=OUTPUT_CHUNK_SIZE)

    cur_data = ''  # current chunk of audio data
    rel = RATE/OUTPUT_CHUNK_SIZE
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
    temp = wf.readframes(OUTPUT_CHUNK_SIZE)

    while temp:
        data.append(temp)
        temp = wf.readframes(OUTPUT_CHUNK_SIZE)

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
        audio_data = librosa.core.audio.load(fp, sr=16000) # TODO: figure how to switch to hamming window
        t2 = time.time()
        ref_data.append(audio_data[0])
        print("Loading data:", t2 - t1)

    print(ref_data)

    t1 = time.time()
    print("Loaded reference data in {}...".format(t1 - t0))

    lowest_dtw_dist = float('inf')
    while (num_phrases == -1 or n > 0):
        cur_data = streamIn.read(MIC_CHUNK_SIZE, exception_on_overflow=False)
        t0 = time.time()
        np_data = np.array(list(cur_data), dtype=np.float32)

        if (started is True):
            streamIn.stop_stream()

            clip_mfcc = librosa.feature.mfcc(np_data, sr=16000, n_mfcc=13) # Return shape: [n_mfcc, t]
            clip_resized = clip_mfcc[1:, :] # Discard intensity vector. Shape: [n_mfcc - 1, t]
            # for dt in ref_data[1:]:
            dt = ref_data[0] # 0th data sample for testing purposes
            # do mfcc before DTW
            ref_mfcc = librosa.feature.mfcc(dt, sr=16000, n_mfcc=13) # Return shape: [n_mfcc, t]
            ref_resized = ref_mfcc[1:, :] # Discard intensity vector. Shape: [n_mfcc - 1, t]
            distance, path = fastdtw(np.transpose(ref_resized), np.transpose(clip_resized))
            pdb.set_trace()

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
