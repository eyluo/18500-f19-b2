import librosa
import sys, os
import time
import numpy as np
from os import listdir
from os.path import isfile, join

'''
MFCC batched, returns output coeffs for all files in {mypath}
'''

if __name__ == "__main__":
    mypath = "samples"
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    mfcc_vals = []
    for fp in files:
        fp = "{}/{}".format(mypath,fp)
        print("File: {}".format(fp))
        t1 = time.time()
        audio_data = librosa.core.audio.load(fp)
        t2 = time.time()
        print("Loading data:", t2 - t1)
        #print(type(audio_data[0]))

        t3 = time.time()
        mfcc = librosa.feature.mfcc(audio_data[0])
        t4 = time.time()
        print("Calculating mfcc: ", t4 - t3)
        mfcc_vals.append(np.array2string(mfcc))

    for (i, fp) in enumerate(files):
        outfile = "{}.txt".format(fp)
        with open(outfile, "w") as fd:
            fd.write(mfcc_vals[i])
            fd.write("\n")
