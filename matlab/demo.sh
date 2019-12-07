#!/bin/bash

# demo script to synchronize before executing python script

TIME_SERVER=time.apple.com

#if [ "$#" -ne 1 ]; then
#  echo "Usage: $0 <threshold>" >&2
#  exit 1
#fi


sudo sntp -sS $TIME_SERVER
/Applications/MATLAB_R2018b.app/bin/matlab -nodisplay -nodesktop -r "run dtw2.m"
