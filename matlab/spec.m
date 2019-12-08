clear all; clc;; close all

SAMPLE_RATE = 16e3; % 16 kHz
FRAME_LENGTH = 1000e-3; 
NUM_SAMPLES = SAMPLE_RATE * FRAME_LENGTH;
NUM_WINDOW_FRAMES = 3;

mic_in = audioDeviceReader(SAMPLE_RATE, NUM_SAMPLES);
mic_audio = mic_in();
[ref_coeffs_mic,ref_delta_mic,ref_deltaDelta_mic,ref_loc_mic] = mfcc(mic_audio, SAMPLE_RATE, "LogEnergy","Ignore");
mic_coeffs_padded = padarray(ref_coeffs_mic, [0 27], 'post'); % zero padded to 40 cepstral coeffs
dct_row_mic = flip(idct(mic_coeffs_padded'), 1);

REF_FILE = "spencer_hey.wav";
[ref_sound, fs_ref_sound] = audioread(REF_FILE);
ref_resampled = resample(ref_sound, SAMPLE_RATE, fs_ref_sound);
[ref_coeffs,ref_delta,ref_deltaDelta,ref_loc] = mfcc(ref_resampled, SAMPLE_RATE, "LogEnergy","Ignore");
% sound(ref_resampled, SAMPLE_RATE, 8);

ref_coeffs_padded = padarray(ref_coeffs, [0 27], 'post'); % zero padded to 40 cepstral coeffs
dct_row = flip(idct(ref_coeffs_padded'), 1);

% figure
% colormap jet
% subplot(2,1,1)
% imagesc(dct_row);
% title(sprintf("MFCC of %s (zero padded)", "spencer\_hey.wav"));
% subplot(2,1,2)
% imagesc(dct_row_mic);
% title(sprintf("MFCC of %s (zero padded)", "mic input"));
% 
% pause
% figure;

REF_FILE = "spencer_hey.wav";
[ref_sound, fs_ref_sound] = audioread(REF_FILE);
ref_resampled = resample(ref_sound, SAMPLE_RATE, fs_ref_sound);
ref_coeffs = mfcc(ref_resampled, SAMPLE_RATE, "LogEnergy","Ignore");
ref_coeffs_trans = ref_coeffs';
ref_coeffs_padded = padarray(ref_coeffs, [0 27], 'post'); % zero padded to 40 cepstral coeffs

INPUT_SOUND_1 = "spencer_hey3.m4a";
[input_sound_1, fs_input_sound_1] = audioread(INPUT_SOUND_1);
input_sound_1_resampled = resample(input_sound_1, SAMPLE_RATE, fs_ref_sound);
input_coeffs_1 = mfcc(input_sound_1_resampled, SAMPLE_RATE, "LogEnergy","Ignore");

input_coeffs_padded_1 = padarray(input_coeffs_1, [0 27], 'post'); % zero padded to 40 cepstral coeffs
input_coeffs_1_trans = input_coeffs_1';
[dist, ix, iy] = dtw(ref_coeffs_trans, input_coeffs_1_trans);
mfcc_warped_1 = ref_coeffs_trans(:,ix);
mfcc_padded_warped_1 = padarray(mfcc_warped_1', [0 27], 'post'); % zero padded to 40 cepstral coeffs

subplot(3,1,1)
imagesc(flip(idct(ref_coeffs_padded'), 1));
title(sprintf("MFCC of %s (zero padded)", "reference sample (spencer\_hey.wav)"));
subplot(3,1,2);
imagesc(flip(idct(input_coeffs_padded_1'), 1));
title(sprintf("MFCC of %s (zero padded)", "original input"));
subplot(3,1,3);
imagesc(flip(idct(mfcc_padded_warped_1'), 1));
title(sprintf("MFCC of %s (zero padded)", "warped input"));