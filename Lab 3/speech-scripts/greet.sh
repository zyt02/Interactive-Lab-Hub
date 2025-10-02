#!/bin/bash
NAME="Zoe"
MESSAGE="Hello $NAME, welcome back to your Raspberry Pi!"

espeak "$MESSAGE" -w greet.wav
aplay greet.wav
