@echo off
title JennaProxy

echo Installing packages...
pip install -r requirements.txt

cls

title JennaProxy (CTRL+C to exit)
python -B main.py
python3 -B main.py