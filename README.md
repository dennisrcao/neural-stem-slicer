> **Still in development**  - this has been an independent project of mine for months if you're interested in helping out - hit me up : )


# Split Stems
---

## Introduction
Imagine a folder on your Desktop where you drag any song in, then double click a command file and out comes stems segmented into 8 bar segments that are prefixed by BPM, key and can added to your custom loop library or be dragged into Ableton Session view to help producers generate new ideas.
![Summary](./README_Assets/algorithm-summary.png)


Drag in...
- Full songs you like
- Personal stems (breath life into old song stems)
- Vinyl rips


## Algorithm Architecture
![Algorithm](./README_Assets/algorithm-diagram-small.png)


#### Prerequisites
- Python 3.11 (recommended) or Python 3.8-3.11
- macOS (including Apple Silicon), Linux, or Windows

```bash
brew install python@3.11
```

Verify the installation:
```bash
python3.11 --version  # Should show Python 3.11.x
```

#### Set Up Virtual Environment
```bash
# Create virtual environment
python3.11 -m venv .venv
# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate  # On Windows
# Install dependencies
pip install -r requirements.txt
# Brew install the tkinter for 3.11
brew install python-tk@3.11
# Install drumsep model
python step3_0_Seperation_Models/drumsep/drumsepInstall.py
# Make it executable
chmod +x step3_0_Seperation_Models/drumsep/drumsep

```

```bash
python split_stems.py
```

### Troubleshooting
If you need to recreate the virtual environment:
```bash
deactivate
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
python step3_0_Seperation_Models/drumsep/drumsepInstall.py
```

