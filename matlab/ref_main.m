%% Constant definitions
% load microphone info
% 16kHz sample rate for 10ms of audio --> 10e-3 * 16kHz = 160 samples
SAMPLE_RATE = 16e3; % 16 kHz
FRAME_LENGTH = 30e-3; 
NUM_SAMPLES = SAMPLE_RATE * FRAME_LENGTH;
LOOP = 5;
VOLUME_THRESHOLD = 1e-3;
MSE_THRESHOLD = 10;

%% Load output and reference sound files
% load response sound file
[output, fs_out_sound] = audioread("spencer_cyrus.wav");
output_sound = resample(output, SAMPLE_RATE, fs_out_sound);

[ref_in, fs_ref_sound] = audioread("spencer_hey.wav");
ref_sound = resample(ref_in, SAMPLE_RATE, fs_out_sound);
ref_coeffs = mfcc(ref_sound, SAMPLE_RATE, "LogEnergy","Ignore");

%% Initialize other values
% Initialize the audio IO stream
mic_in = audioDeviceReader(SAMPLE_RATE, NUM_SAMPLES);

mic_in();
mfcc_vals = zeros(LOOP,13);
% loop on audio samples, begin logging values when volume threshold
% surpassed

%% Loop on audio prompt
% audio_data = zeros(NUM_SAMPLES, LOOP);
while true
    audio_from_device = mic_in();
    power = sum(audio_from_device.^2) / length(audio_from_device);
    
    errs = zeros(1, LOOP);
    if power > VOLUME_THRESHOLD
        for i=1:LOOP
            if i ~= 1
                audio_from_device = mic_in();
            end
            coeffs = mfcc(audio_from_device, SAMPLE_RATE, "LogEnergy","Ignore");
            mfcc_vals(i, :) = coeffs;
%             audio_data(:,i) = audio_from_device;

            err = mse(ref_coeffs(1:i,:), mfcc_vals(1:i,:));

            if err < 0
                sound(output_sound, SAMPLE_RATE);
                return;
            end
            
            mfcc_vals = zeros(LOOP,13);
        end
    end
end