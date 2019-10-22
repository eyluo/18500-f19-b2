import librosa
import sys
import time
import numpy as np

'''
Timing on how fast to calculate MFCC
'''

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python3 mfcc.py <filepath>")

    if len(sys.argv) == 2:
        fp = sys.argv[1]
        t1 = time.time()
        audio_data = librosa.core.audio.load(fp)
        t2 = time.time()
        print("Loading data:", t2 - t1)
        print(type(audio_data[0]))

        t3 = time.time()
        mfcc = librosa.feature.mfcc(audio_data[0])
        t4 = time.time()
        print("Calculating mfcc: ", t4 - t3)


