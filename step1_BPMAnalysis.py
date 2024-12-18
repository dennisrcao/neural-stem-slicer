import librosa
import scipy
from scipy import stats
import numpy as np

def detect_bpm(y, sr, start_bpm=None):
    print("Analyzing BPM...")
    
    # Convert to mono if needed
    if len(y.shape) > 1:
        y = y.mean(axis=1)
    
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo = librosa.feature.rhythm.tempo(
        onset_envelope=onset_env,
        sr=sr,
    )[0]
    
    return round(tempo, 2)

def load_and_analyze_bpm(file_path, start_bpm=None):
    y, sr = librosa.load(file_path)
    return detect_bpm(y, sr, start_bpm)