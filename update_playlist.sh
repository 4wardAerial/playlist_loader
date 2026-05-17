#!/bin/bash
DIR=/home/aerial/Coding/Python/playlist_loader
VENV=/home/aerial/Coding/Python/playlist_loader/.venv/bin/activate
CODE=/home/aerial/Coding/Python/playlist_loader/main.py

cd $DIR
source $VENV
python3 $CODE

echo ""
read -p "Press [Enter] to close terminal."