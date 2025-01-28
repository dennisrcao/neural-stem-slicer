from deeprhythm import DeepRhythmPredictor
import librosa
import numpy as np
from typing import Tuple, List, Dict

"""
BPM and Downbeat Analysis Module

This module provides comprehensive analysis of audio files to detect:
1. BPM (Beats Per Minute)
2. Musical downbeats (first beat of each bar)
3. Music type classification
4. Audio feature analysis
"""

def analyze_audio_features(y: np.ndarray, sr: int) -> Dict:
    """
    Analyzes multiple aspects of the audio to understand its characteristics.
    
    Algorithm:
    1. Calculates onset envelope (detects note/hit starts)
    2. Generates tempogram (rhythm patterns over time)
    3. Splits audio into frequency bands:
       - sub_bass (20-60 Hz)
       - bass (60-250 Hz)
       - low_mid (250-500 Hz)
       - mid (500-2000 Hz)
       - high_mid (2000-4000 Hz)
       - high (4000-20000 Hz)
    4. Measures energy in each frequency band
    
    Returns dictionary of all analyzed features
    """
    print("Analyzing audio features...")
    
    # Get onset envelope and tempogram
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)
    
    # Analyze different frequency bands
    spec = librosa.stft(y)
    spec_db = librosa.amplitude_to_db(abs(spec))
    
    # Frequency band ranges (in Hz)
    bands = {
        'sub_bass': (20, 60),
        'bass': (60, 250),
        'low_mid': (250, 500),
        'mid': (500, 2000),
        'high_mid': (2000, 4000),
        'high': (4000, 20000)
    }
    
    # Analyze energy in each band
    band_energies = {}
    freqs = librosa.fft_frequencies(sr=sr)
    for band_name, (low, high) in bands.items():
        band_mask = (freqs >= low) & (freqs <= high)
        band_energies[band_name] = np.mean(spec_db[band_mask], axis=0)
    
    return {
        'onset_env': onset_env,
        'tempogram': tempogram,
        'band_energies': band_energies,
        'spec': spec_db
    }

def detect_bpm_and_downbeats(y: np.ndarray, sr: int, file_path: str) -> Tuple[float, float, List[float], str]:
    """
    Main analysis function that combines multiple detection methods.
    
    Algorithm:
    1. Uses DeepRhythm ML model for initial BPM detection
    2. Analyzes audio features for context
    3. Classifies music type based on:
       - Rhythm strength
       - Bass presence
       - High frequency content
    4. Chooses appropriate downbeat detection method:
       - Ambient: Uses harmonic changes
       - Rhythmic: Uses kick drum detection
    
    Returns BPM, confidence score, downbeat timestamps, and music type
    """
    print("Starting comprehensive BPM analysis...")
    
    # 1. Get DeepRhythm BPM (good baseline for rhythmic music)
    predictor = DeepRhythmPredictor()
    bpm, confidence = predictor.predict_from_audio(y, sr, include_confidence=True)
    
    # 2. Get detailed audio analysis
    features = analyze_audio_features(y, sr)
    onset_env = features['onset_env']
    band_energies = features['band_energies']
    
    # 3. Determine music type based on features
    rhythm_strength = np.mean(onset_env)
    bass_presence = np.mean(band_energies['bass'])
    high_freq_content = np.mean(band_energies['high'])
    
    if rhythm_strength < 0.1:
        music_type = "ambient/atmospheric"
    elif bass_presence > np.mean(list(band_energies.values())):
        music_type = "bass-heavy/electronic"
    elif high_freq_content > np.mean(list(band_energies.values())):
        music_type = "bright/acoustic"
    else:
        music_type = "balanced/mixed"
    
    print(f"Detected music type: {music_type}")
    
    # 4. Find downbeats using appropriate method for the music type
    if music_type == "ambient/atmospheric":
        # Use harmonic changes for ambient music
        downbeats = detect_ambient_downbeats(y, sr, features)
    else:
        # Use rhythm-based detection for other types
        downbeats = detect_rhythmic_downbeats(y, sr, features)
    
    # Convert downbeat frames to timestamps
    downbeat_times = librosa.frames_to_time(downbeats, sr=sr).tolist()
    
    print(f"DeepRhythm BPM: {bpm:.2f} (confidence: {confidence:.2%})")
    print(f"Found {len(downbeat_times)} downbeats")
    for i, time in enumerate(downbeat_times[:5], 1):
        print(f"Downbeat {i}: {time:.3f}s")
    if len(downbeat_times) > 5:
        print("...")
    
    return bpm, confidence, downbeat_times, music_type

def detect_ambient_downbeats(y: np.ndarray, sr: int, features: Dict) -> np.ndarray:
    """
    Specialized downbeat detection for ambient/atmospheric music.
    
    Algorithm:
    1. Extracts harmonic content (removes percussion)
    2. Analyzes tonal changes using tonnetz transform
    3. Finds significant harmonic changes as potential phrase starts
    4. Returns frame numbers where phrases likely begin
    """
    # Use harmonic changes and energy distribution
    harmonic = librosa.effects.harmonic(y)
    tonnetz = librosa.feature.tonnetz(y=harmonic, sr=sr)
    changes = np.sum(np.diff(tonnetz, axis=1) ** 2, axis=0)
    peaks = librosa.util.peak_pick(changes, pre_max=30, post_max=30, 
                                 pre_avg=30, post_avg=30, delta=0.1, wait=30)
    return peaks

def detect_rhythmic_downbeats(y: np.ndarray, sr: int, features: Dict) -> np.ndarray:
    """
    Specialized downbeat detection for rhythm-based music.
    
    Algorithm:
    1. Separates percussive content from harmonic
    2. Detects basic beat grid using onset strength
    3. Focuses on kick drum frequency range (20-150 Hz)
    4. Finds strong kick drum hits
    5. Aligns kicks with beat grid to find phrase starts
    6. Uses tempo to validate phrase lengths (typically 4 beats)
    7. Falls back to regular beat detection if no clear phrases found
    
    Returns frame numbers of detected downbeats
    """
    onset_env = features['onset_env']
    
    # Separate percussive content more aggressively
    y_harmonic, y_percussive = librosa.effects.hpss(y, margin=3.0)
    
    # Get regular beats first to establish tempo
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, units='time')
    beat_times = librosa.frames_to_time(librosa.time_to_frames(beats, sr=sr), sr=sr)
    
    # Calculate beat duration and expected phrase length
    beat_duration = 60.0 / tempo
    phrase_duration = 4 * beat_duration  # Assuming 4 beats per phrase
    
    # Get onset envelope focused on kick drum range with proper timing
    hop_length = 512  # Standard hop length for librosa
    onset_kick = librosa.onset.onset_strength(
        y=y_percussive, 
        sr=sr,
        feature=librosa.feature.melspectrogram,
        fmin=20,
        fmax=150,
        hop_length=hop_length
    )
    
    # Find kick drum hits
    kick_peaks_frames = librosa.util.peak_pick(
        onset_kick,
        pre_max=30,
        post_max=30,
        pre_avg=30,
        post_avg=30,
        delta=0.5,
        wait=int(sr * beat_duration / (4 * hop_length))  # Wait time based on quarter beats
    )
    
    # Convert frames to time
    kick_times = librosa.frames_to_time(kick_peaks_frames, sr=sr, hop_length=hop_length)
    
    # Find phrase starts by looking for strong kicks near expected phrase boundaries
    phrase_starts = []
    current_time = 0
    
    while current_time < librosa.get_duration(y=y, sr=sr):
        # Look for kicks near the expected phrase start
        window_start = max(0, current_time - 0.1)  # 100ms before
        window_end = min(librosa.get_duration(y=y, sr=sr), current_time + 0.1)  # 100ms after
        
        # Find kicks in this window
        kicks_in_window = [t for t in kick_times if window_start <= t <= window_end]
        
        if kicks_in_window:
            # Use the earliest strong kick in the window as phrase start
            phrase_starts.append(kicks_in_window[0])
        
        # Move to next expected phrase start
        current_time += phrase_duration
    
    if not phrase_starts:
        # Fallback to regular beats if no clear phrases found
        return librosa.time_to_frames(beat_times[::4], sr=sr)  # Every 4th beat
    
    # Convert time back to frames for return value
    return librosa.time_to_frames(np.array(phrase_starts), sr=sr)

def load_and_analyze_bpm(file_path: str, manual_bpm: float = None) -> Tuple[float, List[float], str]:
    """
    Entry point function for BPM analysis.
    
    Algorithm:
    1. Handles manual BPM override if provided
    2. Loads audio file
    3. Runs comprehensive BPM and downbeat detection
    4. Returns results in format needed by GUI
    """
    if manual_bpm is not None:
        return manual_bpm, [], "manual"
    
    y, sr = librosa.load(file_path)
    bpm, confidence, downbeat_times, music_type = detect_bpm_and_downbeats(y, sr, file_path)
    return bpm, downbeat_times, music_type