# TO ADD: 
- naming convention change to - "Key - Title - BPM " 
- ✓ Drum Demux to kick, snare, cymbal, toms
- ✓ Synth separation from "other" stem
- [gonna use neuralnote] add midi layer parallel to the melody 
- make executable for drag and drop or double click


#Installation

`deactivate`
`rm -rf .venv`
`python -m venv .venv`
`source .venv/bin/activate`  # On macOS/Linux
`pip install -r requirements.txt`

`cd drumsep
bash drumsepInstall
cd ..`

`cd synthsep
bash synthsepInstall
cd ..`

`python split_stems.py`