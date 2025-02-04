# Neural Stem Slicer


> **Note:** For development details and contribution guidelines, see [Developer README](README_Dev.md)

<a href="https://buymeacoffee.com/dennisrcao" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-black.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>



## Directory
- [Overview](#overview)
- [Low Level Architecture](#low-level-architecture)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [macOS Installation](#macos-installation)
  - [Windows Installation](#windows-installation)
- [Usage](#usage)


## Overview
![Overview](./README_Assets/overview.png)

A music production utility tool that converts any song into perfectly organized, production-ready stems and 8 bar segments.

Just drag in any audio file (`.mp3/.wav`) and Neural Stem Slicer intelligently processes and automatically:

- Splits tracks into 8 high-quality stems using Demucs Hybrid Transformers
  - Bass, Vocals, Melody, Drums
  - Drums → Kick, Snare, Toms, Cymbals
- Detects and labels all files with BPM and key using deep learning analysis (with manual override)
- Segments each stem into precise 8-bar loops ready for Ableton Complex warping
<br>

Perfect for:

**Music Production & Sampling/Hardware**
- Create custom loops for Ableton Session view
- Extract clean stems for remixing and sampling
- Build your own custom loop collections labeled by BPM/Key
- Extract usable stems from vinyl rips
- Load stems into hardware (samplers, drum machines, groove boxes)
- Study arrangements by analyzing each 8 bar segment

**Live Performance & DJing**
- Generate clean acapellas and instrumentals
- Create perfectly-timed drum loops for live layering
- Build custom DJ tools and transition elements
- Study arrangement and mixing techniques
- Extract vocals and music beds for content creation


## Low Level Architecture
![Algorithm](./README_Assets/algorithm-diagram-small.png)


## Installation
### Prerequisites
- Git ([Download Git](https://git-scm.com/downloads))
  - macOS: `brew install git`
  - Windows: Download installer from git-scm.com
- Python 3.11 ([Download Python](https://www.python.org/downloads/))
  - macOS: `brew install python@3.11`
  - Windows: Download installer from python.org
- macOS (including Apple Silicon), Linux, or Windows

### Setup
```bash
# Clone repository
git clone https://github.com/yourusername/neural-stem-slicer.git
cd neural-stem-slicer
```

### macOS Installation
```bash
# Verify Python installation
python3.11 --version  # Should show Python 3.11.x

# Create virtual environment
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install tkinter for Python 3.11
brew install python-tk@3.11

# Install drumsep model
python step3_0_Seperation_Models/drumsep/drumsepInstall.py

# Make it executable
chmod +x step3_0_Seperation_Models/drumsep/drumsep
```

### Windows Installation
```bash
# Install Python 3.11 from python.org

# Verify installation
python --version  # Should show Python 3.11.x

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install drumsep model
python step3_0_Seperation_Models/drumsep/drumsepInstall.py
```

---

## Usage
```bash
python split_stems.py
```

![gui](./README_Assets/algorithm-diagram-small.png)



