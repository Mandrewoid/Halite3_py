#!/bin/sh

rm replays/*
./halite --replay-directory replays/ -vvv --width 32 --height 32 "python3 MyBot.py" "python3 picklebot.py"
