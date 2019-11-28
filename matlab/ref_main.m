% load microphone info
% 16kHz sample rate for 10ms of audio --> 10e-3 * 16kHz = 160 samples
SAMPLE_RATE = 16e3; % 16 kHz
FRAME_LENGTH = 30e-3; 
NUM_SAMPLES = SAMPLE_RATE * FRAME_LENGTH;
LOOP = 10;
VOLUME_THRESHOLD = 1e-4;

% load response sound file
[ref_sound, fs_ref_sound] = audioread("spencer_hey.wav");
ref_coeffs = mfcc(ref_sound, fs_ref_sound, "LogEnergy","Ignore");

% Initialize the audio IO stream
mic_in = audioDeviceReader(SAMPLE_RATE, NUM_SAMPLES);

mic_in();
mfcc_vals = zeros(1,13);
% loop on audio samples, begin logging values when volume threshold
% surpassed

audio_data = zeros(NUM_SAMPLES, LOOP);
while true
    audioFromDevice = mic_in();
    power = sum(audioFromDevice.^2) / length(audioFromDevice);
    
    if power > VOLUME_THRESHOLD
        tic;
        coeffs = mfcc(audioFromDevice, SAMPLE_RATE, "LogEnergy","Ignore");
        mfcc_vals(i, :) = coeffs;
        audio_data(:,i) = audioFromDevice;
        
        for i=1:LOOP
            audioFromDevice = mic_in();
            coeffs = mfcc(audioFromDevice, SAMPLE_RATE, "LogEnergy","Ignore");
            mfcc_vals(i, :) = coeffs;
            audio_data(:,i) = audioFromDevice;
        end
        
        toc;
        sound(ref_sound, fs_ref_sound);
        audio_data = zeros(NUM_SAMPLES, LOOP);
    end
end