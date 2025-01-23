from deeprhythm import DeepRhythmPredictor
import librosa

def detect_bpm(y, sr, file_path, start_bpm=None):
    """
    Detect BPM using DeepRhythm
    """
    print("Analyzing BPM...")
    
    predictor = DeepRhythmPredictor()
    bpm, confidence = predictor.predict_from_audio(y, sr, include_confidence=True)
    print(f"DeepRhythm detected BPM: {bpm:.2f} (confidence: {confidence:.2%})")
    return bpm, confidence

def load_and_analyze_bpm(file_path, manual_bpm=None):
    """
    Load audio file and analyze its BPM
    """
    if manual_bpm is not None:
        return manual_bpm
    
    y, sr = librosa.load(file_path)
    bpm, confidence = detect_bpm(y, sr, file_path)
    return bpm