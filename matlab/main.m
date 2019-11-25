close all; clear; clc

% load microphone info
% 16kHz sample rate for 10ms of audio --> 10e-3 * 16kHz = 160 samples
SAMPLE_RATE = 16e3; % 16 kHz
FRAME_LENGTH = 30e-3; 
NUM_SAMPLES = SAMPLE_RATE * FRAME_LENGTH;

% load response sound file
[ref_sound, fs_ref_sound] = audioread("dsp1.m4a");
ref_resampled = resample(ref_sound, SAMPLE_RATE, fs_ref_sound);
% [ref_sound, fs_ref_sound] = audioread("spencer_hey.wav");
[ref_coeffs,ref_delta,ref_deltaDelta,ref_loc] = mfcc(ref_resampled, SAMPLE_RATE, "LogEnergy","Ignore");
% sound(ref_resampled, SAMPLE_RATE, 8);

dct_row = flip(idct(ref_coeffs'), 1);

figure
subplot(2,1,1)
spectrogram(ref_sound,'yaxis');
subplot(2,1,2)
imagesc(dct_row);


% Nx = length(ref_sound);
% nsc = floor(Nx/4.5);
% nov = floor(nsc*.9);
% nff = max(256,2^nextpow2(nsc));

% subplot(2,1,1)
% spectrogram(ref_sound,hamming(nsc),nov,nff, 'yaxis');
% title('spectrogram() on the reference sound');
% subplot(2,1,2);
% imagesc(dct2(ref_coeffs));
% title('dct2() on the MFCC coefficients');

% Initialize the audio IO stream
mic_in = audioDeviceReader(SAMPLE_RATE, NUM_SAMPLES);

% NUM_LOOP = 50;
% audio_data = zeros(NUM_LOOP, NUM_SAMPLES);
% for i=1:NUM_LOOP
%     temp = mic_in();
%     audio_data(i, :) = temp;
% end
% 
% a = audio_data';
% a = a(:);
% 
% sound(a, SAMPLE_RATE, 8);

mic_in();
mfcc_vals = zeros(1,13);
% loop on audio samples, begin logging values when volume threshold
% surpassed
NUM_LOOPS = 100;
audio_data = zeros(NUM_LOOPS,NUM_SAMPLES);

for i = 1:NUM_LOOPS
    tic;
    audioFromDevice = mic_in();
    audio_data(i, :) = audioFromDevice;
%     win = hann(NUM_SAMPLES,"periodic");
%     S = stft(audioFromDevice,"Window",win,"OverlapLength",512,"Centered",false);
    coeffs = mfcc(audioFromDevice, SAMPLE_RATE, "LogEnergy","Ignore");
    mfcc_vals(i, :) = coeffs;
    
    toc;
    
%     subplot(2,1,1)
%     spectrogram(audioFromDevice, SAMPLE_RATE);
%     subplot(2,1,2);
%     plot(dct(coeffs));
%     drawnow 

%     tic;
%     [dist, ix, iy] = dtw(ref_coeffs, coeffs);
%     toc;
% TODO: perform the time warping across the MFCCs
% TODO: verify that the spectrogram of DCT(warped_mfccs) matches
    
%     pause;
end

a = audio_data';
a = a(:);

release(mic_in);
sound(a, SAMPLE_RATE, 8);