#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$DIR/.venv/bin/activate"

# Change to the script directory
cd "$DIR"

# Run the Python script
python split_stems.py

# Keep the terminal window open to see any errors
echo "Press Enter to close..."
read