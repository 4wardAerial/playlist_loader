#!/bin/bash
PATH=/home/aerial/Coding/Python/playlist_loader
VENV=/home/aerial/Coding/Python/playlist_loader/.venv/bin/activate
CODE=/home/aerial/Coding/Python/playlist_loader/main.py

cd $PATH
source $VENV
python3 $CODE
