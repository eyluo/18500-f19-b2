% load response sound file

% load microphone info
% 16kHz sample rate for 10ms of audio --> 10e-3 * 16kHz = 160 samples
SAMPLE_RATE = 16e3;
FRAME_LENGTH = 35e-3;
NUM_SAMPLES = SAMPLE_RATE * FRAME_LENGTH;

mic_in = audioDeviceReader(SAMPLE_RATE, NUM_SAMPLES);

mic_in();
mfcc_vals = zeros(1,13);
% loop on audio samples, begin logging values when volume threshold
% surpassed
i = 1;
while true
    close all;
    tic;
    audioFromDevice = mic_in();
    win = hann(NUM_SAMPLES,"periodic");
    S = stft(audioFromDevice,"Window",win,"OverlapLength",512,"Centered",false);
    coeffs = mfcc(S, SAMPLE_RATE, "LogEnergy","Ignore");
    mfcc_vals(i, :) = coeffs;
    i = i + 1;
    mfcc_vals
    toc;
    subplot(2,1,1)
    spectrogram(audioFromDevice, SAMPLE_RATE);
    subplot(2,1,2);
    pause;
end