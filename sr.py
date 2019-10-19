import time
import sys
import speech_recognition as sr

'''
Demonstrates the speed at which CMU Sphinx can recognize words.
It appears to be very slow and text transcription may not be the
best path forward.
'''

if __name__ == "__main__":

    if len(sys.argv) > 2:
        print("Usage: python sr.py <energy_threshold>")

    # obtain audio from the microphone
    r = sr.Recognizer()
    r.phrase_time_limit = 0 # secs

    try:
        while True:
            with sr.Microphone() as source:

                if len(sys.argv) == 2:
                    r.energy_threshold = int(sys.argv[1])
                else:
                    r.adjust_for_ambient_noise(source)

                print("Say something!")
                audio = r.listen(source)
                print("Processing audio")
                t0 = time.time()

            # recognize speech using Sphinx
            try:
                recognized = r.recognize_sphinx(audio)
                rec = True
            except sr.UnknownValueError:
                print("Sphinx could not understand audio")
            except sr.RequestError as e:
                print("Sphinx error; {0}".format(e))
            t1 = time.time()

            if rec:
                print("Sphinx thinks you said " + r.recognize_sphinx(audio))

            print("Audio Processing Time: {}".format(t1 - t0))

    except KeyboardInterrupt:
        pass
