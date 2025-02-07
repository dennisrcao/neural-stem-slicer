# Neural Stem Slicer (For Developers)


> **Still in development**  - this has been an independent project of mine for months if you're interested in helping out - hit me up : )
--- 
## Directory
- [TODO List](#todo-list)
- [Development Setup](#development-setup)
- [Research Links](#research-links)
  - [Audio Processing Resources](#audio-processing-resources)
  - [Development Tools](#development-tools)
  - [Training Resources](#training-resources)

--- 
## TODO List
- Onset detection of the "1" beat - maybe include GUI with waveform at top with spacebar control (playpause) + waveform zoom in/out, we store timestamp, so user can decide on the "1" 
- Type check for manual override must be a number BPM and a camelot wheel string 
- Total Processing Time: 314.87 seconds

## Development Setup
### Reset Environment
If you need to reset your development environment:
```bash
# Deactivate current environment if active
deactivate
# Remove existing environment
rm -rf .venv
rm -rf output/  # Remove any test outputs
# Create fresh environment
python3.11 -m venv .venv

# Activate
source .venv/bin/activate  # On macOS/Linux
.venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Reinstall models
python step3_0_Seperation_Models/drumsep/drumsepInstall.py

# Make executable (macOS/Linux only)
chmod +x step3_0_Seperation_Models/drumsep/drumsep
```

---

## Research Links

### Audio Processing Resources

- [Instrumental and Vocal & Stems Separation & Mastering Guide](https://docs.google.com/document/d/1LXXd0Hjx6L53BDgms1cVEsqZ7G1cds4ilgX9V4FOW4o/edit?tab=t.0#heading=h.roiuj54hzww3)

- [Guide to Training Audio Source Separation Models](https://docs.google.com/document/d/12KzNIojKSWLA7uvHhhxydXvBLZgussewc1aRzWxqGwY/edit?tab=t.0)

- [Mixxx - Open Source DJ Mixing Software](https://github.com/mixxxdj/mixxx)
  > Best BPM detection implementation reference

### Development Tools
- [UV](https://github.com/astral-sh/uv)
  > Fast Python package manager written in Rust

### Training Resources
- [Music Source Separation Training](https://github.com/ZFTurbo/Music-Source-Separation-Training)

