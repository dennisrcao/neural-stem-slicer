#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Activate virtual environment
source .venv/bin/activate

# Run the script
python split_stems.py

# Keep terminal window open
read -p "Press enter to close..." 