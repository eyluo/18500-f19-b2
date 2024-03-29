%% Constant definitions
% load microphone info
% 16kHz sample rate for 10ms of audio --> 10e-3 * 16kHz = 160 samples
SAMPLE_RATE = 16e3; % 16 kHz
FRAME_LENGTH = 30e-3; 
NUM_SAMPLES = SAMPLE_RATE * FRAME_LENGTH;
NUM_WINDOW_FRAMES = 3;
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

%% Loop on audio prompt
audio_data = zeros(NUM_SAMPLES, NUM_WINDOW_FRAMES);
ref_coeffs_trans = ref_coeffs'; % for ease of using DTW
mfcc_vals = zeros(13, NUM_WINDOW_FRAMES);

i = 1;
while i < NUM_WINDOW_FRAMES
    audio_from_device = mic_in();
    coeffs = mfcc(audio_from_device, SAMPLE_RATE, "LogEnergy", "Ignore");
    mfcc_vals(:, i) = coeffs';
    audio_data(:,i) = audio_from_device;
    i = i + 1;
end

while true
    audio_from_device = mic_in();
    
    % Sample in a couple frames of audio and then perform dynamic time 
    % warping. Compare the MSE and play jamming sound if error threshold 
    % reached. Constantly poll in increments of FRAME_LENGTH seconds.
    % Keep the previous few frames in memory so that the coefficients from
    % NUM_LOOPS frames can be used to determine accuracy.
    % 
    % This allows for a sliding window over time to be achieved, which may
    % potentially offer better performance compared to polling several
    % frames only when a threshold is reached. 
    
    coeffs = mfcc(audio_from_device, SAMPLE_RATE, "LogEnergy", "Ignore");
    mfcc_vals(:, i) = coeffs';
    audio_data(:,i) = audio_from_device;
    
    lower_idx = i - NUM_WINDOW_FRAMES + 1;
    window_mfcc_vals = mfcc_vals(:, lower_idx:i);
    [dist, ix, iy] = dtw(ref_coeffs_trans, window_mfcc_vals);
    mfcc_warped = window_mfcc_vals(:, iy);

    err = mse(ref_coeffs_trans, mfcc_warped);
    disp(sprintf("Error (DTW + MSE): %d, Threshold: %d", err, MSE_THRESHOLD));   

    if (err < MSE_THRESHOLD)
        sound(output_sound, SAMPLE_RATE);
        return;
    end
    
    i = i + 1;
end