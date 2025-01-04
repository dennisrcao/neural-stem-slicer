# Installation


### Prerequisites
- Python 3.8-3.11 (3.13 is not supported yet)
- macOS, Linux, or Windows

Install Python 3.11 
`brew install python@3.11`

Verify the version 
` python --version  # Should show Python 3.11.x `
`python -m venv .venv`
`source .venv/bin/activate`  # On macOS/Linux
`pip install -r requirements.txt`

`cd drumsep`
`bash drumsepInstall`

`cd synthsep`
`bash synthsepInstall`

`python split_stems.py`

### Algorithm
https://github.com/bleugreen/deeprhythm