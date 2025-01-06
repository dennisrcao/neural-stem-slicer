import librosa
import os
import shutil
from deeprhythm import DeepRhythmPredictor

def detect_bpm(y, sr, file_path, start_bpm=None):
    """
    Detect BPM using DeepRhythm with fallback to librosa
    """
    print("Analyzing BPM...")
    
    try:
        predictor = DeepRhythmPredictor()
        bpm, confidence = predictor.predict_from_audio(y, sr, include_confidence=True)
        print(f"DeepRhythm detected BPM: {bpm:.2f} (confidence: {confidence:.2%})")
        return bpm, confidence
    except Exception as e:
        print(f"DeepRhythm error: {e}, falling back to librosa")
        
        # Convert to mono if needed
        if len(y.shape) > 1:
            y = y.mean(axis=1)
        
        # Use librosa's tempo detection
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.feature.tempo(
            onset_envelope=onset_env,
            sr=sr,
        )[0]
        
        print(f"Librosa detected BPM: {tempo:.2f}")
        return tempo, None

def load_and_analyze_bpm(file_path, manual_bpm=None):
    """
    Load audio file and analyze its BPM
    """
    if manual_bpm is not None:
        return manual_bpm
    
    y, sr = librosa.load(file_path)
    bpm, confidence = detect_bpm(y, sr, file_path)
    return bpm