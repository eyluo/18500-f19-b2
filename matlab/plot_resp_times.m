data = load('time_test.mat');

resp_times = data.resp_times;

histogram(resp_times, 0.44:0.01:0.48);
xlabel("response time (s)"); 
ylabel("count"); 
title("response time histogram");