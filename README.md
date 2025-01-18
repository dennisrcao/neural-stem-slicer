> **Still in development**  - this has been an independent project of mine for months if you're interested in helping out - hit me up : )
> **TODO:** 
> - Seperate modules 1, 2, 3

# Split Stems


---

### 🎵 High Level Concept
Imagine a folder on your Desktop where you drag any song into it, then double click a command file and out comes stems segmented into 8 bar segments that are prefixed by BPM, key and can then be dragged into Ableton Session view to help producers generate new ideas.

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
```

```bash
# Install drum separator
cd drumsep
bash drumsepInstall

# Install synth separator
cd ../synthsep
bash synthsepInstall
```

### Step 4: Run the Splitter
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
```

### Algorithm
Based on [DeepRhythm](https://github.com/bleugreen/deeprhythm)
