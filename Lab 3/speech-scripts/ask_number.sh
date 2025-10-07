#!/bin/bash
# Script to ask for a phone number and record the spoken response

# Ask the question out loud
espeak "Hello user, please say your phone number."

# Record audio from microphone (8 seconds max)
arecord -d 8 -f cd -t wav response.wav
espeak "Thank you. Your response has been recorded."
