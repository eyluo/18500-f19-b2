%% Constant definitions
% load microphone info
% 16kHz sample rate for 10ms of audio --> 10e-3 * 16kHz = 160 samples
SAMPLE_RATE = 16e3; % 16 kHz
FRAME_LENGTH = 30e-3; 
NUM_SAMPLES = SAMPLE_RATE * FRAME_LENGTH;
NUM_LOOPS = 3;
VOLUME_THRESHOLD = 1e-5;
MSE_THRESHOLD = 2.75;

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
mic_in(); % Pull one value from the buffer in case there's a slow start
mfcc_vals = zeros(NUM_LOOPS, 13);

%% Loop on audio prompt
audio_data = zeros(NUM_SAMPLES, NUM_LOOPS);
ref_coeffs_trans = ref_coeffs'; % for ease of using DTW

while true
    audio_from_device = mic_in();
    power = sum(audio_from_device.^2) / length(audio_from_device);
    
    % If threshold reached, sample in a couple frames of audio and then
    % perform dynamic time warping. Compare the MSE and play jamming sound
    % if error threshold reached.
    if power > VOLUME_THRESHOLD
        mfcc_vals = zeros(13, NUM_LOOPS);
        for i=1:NUM_LOOPS
            if i ~= 1
                audio_from_device = mic_in();
            end
            coeffs = mfcc(audio_from_device, SAMPLE_RATE, "LogEnergy", "Ignore");
            mfcc_vals(:, i) = coeffs';
            audio_data(:,i) = audio_from_device;
        end
        
        [dist, ix, iy] = dtw(ref_coeffs_trans, mfcc_vals);
        mfcc_warped = mfcc_vals(:, iy);

        err = mse(ref_coeffs_trans, mfcc_warped);
        disp(sprintf("Error (DTW + MSE): %d, Threshold: %d", err, MSE_THRESHOLD));   

        if (err < MSE_THRESHOLD)
            sound(output_sound, SAMPLE_RATE);
            return;
        end
    end
end