close all; clear; clc

%% Setup procedures
% load microphone info
% 16kHz sample rate for 10ms of audio --> 10e-3 * 16kHz = 160 samples
SAMPLE_RATE = 16e3; % 16 kHz
FRAME_LENGTH = 30e-3; 
NUM_SAMPLES = SAMPLE_RATE * FRAME_LENGTH;

% load response sound file
REF_FILE = "welcome16k.wav";
[ref_sound, fs_ref_sound] = audioread(REF_FILE);
ref_resampled = resample(ref_sound, SAMPLE_RATE, fs_ref_sound);
% [ref_sound, fs_ref_sound] = audioread("spencer_hey.wav");
[ref_coeffs,ref_delta,ref_deltaDelta,ref_loc] = mfcc(ref_resampled, SAMPLE_RATE, "LogEnergy","Ignore");
% sound(ref_resampled, SAMPLE_RATE, 8);

ref_coeffs_padded = padarray(ref_coeffs, [0 27], 'post'); % zero padded to 40 cepstral coeffs
dct_row = flip(idct(ref_coeffs_padded'), 1);

figure
colormap jet
subplot(2,1,1)
% spectrogram(ref_sound,'yaxis');
imagesc(flip(idct(ref_coeffs'), 1));
title(sprintf("MFCC of %s (not zero padded)", REF_FILE));
subplot(2,1,2)
imagesc(dct_row);
title(sprintf("MFCC of %s (zero padded)", REF_FILE));

% Initialize the audio IO stream
mic_in = audioDeviceReader(SAMPLE_RATE, NUM_SAMPLES);

mic_in();

% loop on audio samples
NUM_LOOPS = 100;
NUM_CEP_COEFFS = 40;

%% WIP - Verification for DTW accuracy - load another clip of "Welcome to DSP1"
% Comment out this section for actual usage, since it corrupts the
% microphone reading routine.

% [audio_data, fs_audio_data] = audioread("dsp1.m4a");
% audio_data = resample(audio_data, SAMPLE_RATE, fs_audio_data);
% mfcc_vals = zeros(1, 40);
% for i = 1:size(audio_data, 1)
%     coeffs = mfcc(audio_data(i, :), SAMPLE_RATE, "LogEnergy", "Ignore");
%     mfcc_vals(i, 1:numel(coeffs)) = coeffs; % zero padded to 40 cepstral coeffs
% end

%% Core microphone loop routine
mfcc_vals = zeros(1, NUM_CEP_COEFFS);
audio_data = zeros(NUM_LOOPS, NUM_SAMPLES);

for i = 1:NUM_LOOPS
    tic;
    audioFromDevice = mic_in();
    % TODO: begin logging values when volume threshold surpassed
    % ( maybe do this using norm() )?
    audio_data(i, :) = audioFromDevice;
    % MFCC returns (time x num_coeffs) dimensioned results
    coeffs = mfcc(audioFromDevice, SAMPLE_RATE, "LogEnergy","Ignore");
    mfcc_vals(i, 1:numel(coeffs)) = coeffs; % zero padded to 40 cepstral coeffs
    
    toc;
end

%% DTW routine
% For Matlab's DTW algorithm, the number of rows must match. ie 
% same number of coefficients per time stamp (where one column is 
% one time stamp). Transpose the MFCC coefficients to match this.
ref_transposed = ref_coeffs_padded';
micin_transposed = mfcc_vals';

[dist, ix, iy] = dtw(ref_transposed, micin_transposed);
ref_transposed_warp = ref_transposed(:, ix);
micin_transposed_warp = micin_transposed(:, iy);

% Plot the results for verification purposes
dct_micin = flip(idct(micin_transposed_warp), 1);
size(dct_micin)

figure
colormap jet
imagesc(dct_micin);
title(sprintf("MFCC of %s (zero padded)", "dct\_micin"));

a = audio_data';
a = a(:);

release(mic_in);
sound(a, SAMPLE_RATE, 8);