# Audio Stem Chopper

A Python script for automatically chopping audio stems into synchronized 8-bar segments and organizing them systematically.

Stems must be 0 aligned in Ableton.

## Features

- Chops audio stems into 8-bar segments based on BPM
- Maintains synchronization across all stems
- Automatically organizes output files with consistent naming
- Supports MP3 format (expandable to other formats)

## Prerequisites

- Python 3.7 or higher
- FFmpeg (required for audio processing)

## Setup / Run
`python -m venv venv` 
`source venv/bin/activate `
`pip install -r requirements.txt`
`python chop_stems.py <BPM>` #for example `python chop_stems.py 126`