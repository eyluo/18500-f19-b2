#!/bin/bash

# demo script to synchronize before executing python script

TIME_SERVER=time.apple.com

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <threshold>" >&2
  exit 1
fi

THRESHOLD=$1

sudo sntp -sS $TIME_SERVER
python3 ./demo-midpoint/soundOutput.py ./samples/cyrus.wav $THRESHOLD