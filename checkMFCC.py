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

SILENCE_LIMIT = 1  # Silence limit in seconds. The max ammount of seconds where
# only silence is recorded. When this time passes the
# recording finishes and the file is delivered.

COEFF_BOUND = 13


def checkMFCC(num_phrases=-1):
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

    if len(sys.argv) < 3:
        print('usage: python3 soundIO.py <.wav file> <.wav file>')
        return

    f1, f2 = sys.argv[1], sys.argv[2]

    # This is the reference audio.
    audio_data1 = librosa.core.audio.load(f1)
    coeffs1 = librosa.feature.mfcc(audio_data1[0])

    audio_data2 = librosa.core.audio.load(f2)
    coeffs2 = librosa.feature.mfcc(audio_data2[0])
    
    total_mse = 0
    for i in range(min(len(coeffs1), len(coeffs2))):
        mse = 0
        s1, s2 = coeffs1[i], coeffs2[i]
        num_coeffs = 0
        while num_coeffs < min(len(s1), len(s2), COEFF_BOUND):
            mse += (s1[num_coeffs] - s2[num_coeffs])**2
            num_coeffs += 1
        total_mse += (mse / num_coeffs)

    print(total_mse)


if(__name__ == '__main__'):
    checkMFCC()  # listen to mic.
