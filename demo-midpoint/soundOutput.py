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
SAMPLES = "samples" # Folder to read reference data for error comparison from

def listen_for_speech(threshold=THRESHOLD, num_phrases=-1):
    '''
    Listens to Microphone, extracts audio sample of size CHUNK. If the audio amplitude
    is greater than THRESHOLD, then processes audio sample into MFCC data.
    num_phrases controls how many phrases to process before finishing the listening process (-1 for infinite). 

    Sample usage: [:~/18500-f19-b2] $ python3 demo-midpoint/soundOutput.py samples/cyrus.wav 1000
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
    mfcc_vals = []
    for fp in files:
        fp = "{}/{}".format(SAMPLES,fp)
        print("File: {}".format(fp))
        t1 = time.time()
        audio_data = librosa.core.audio.load(fp)
        t2 = time.time()
        print("Loading data:", t2 - t1)

        t3 = time.time()
        mfcc = librosa.feature.mfcc(audio_data[0])
        t4 = time.time()
        print("Calculating mfcc: ", t4 - t3)
        mfcc_vals.append(mfcc)
    t1 = time.time()
    print("Loaded reference MFCC data in {}...".format(t1 - t0))

    lowest_mfcc_error = float('inf')
    while (num_phrases == -1 or n > 0):
        cur_data = streamIn.read(CHUNK, exception_on_overflow=False)
        t0 = time.time()
        np_data = np.array(list(cur_data), dtype=np.float32)

        if (started is True):
            streamIn.stop_stream()
            mfcc = librosa.feature.mfcc(np_data)
            t1 = time.time()
            print("Processed & converted chunk MFCC data in {}...".format(t1 - t0))

            # Calculate lowest MFCC error from sample data
            for ref_mfcc in mfcc_vals:
                # Mean squared error
                mfcc_error = np.square((ref_mfcc - mfcc).mean(axis=None))
                if (mfcc_error < lowest_mfcc_error):
                    lowest_mfcc_error = mfcc_error

            print("Lowest MFCC error: {}".format(lowest_mfcc_error))
            
            if (lowest_mfcc_error < THRESHOLD_MSE_MFCC):
                streamOut.write(data)
                lowest_mfcc_error = float('inf')
                # Prevent infinite loop where speaker continues to detect itself
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
