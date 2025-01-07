import librosa
import numpy as np
import os
import shutil

def detect_key(file_path):
    """
    Detect musical key using librosa's key detection
    """
    print("Analyzing Key...")
    y, sr = librosa.load(file_path)
    
    # Compute chromagram
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    
    # Calculate key correlation with all possible keys
    key_correlations = []
    for key_chroma in get_key_profiles():
        correlation = np.sum(key_chroma.reshape(-1, 1) * chroma)
        key_correlations.append(correlation)
    
    # Get top 2 keys
    key_indexes = np.argsort(key_correlations)[-2:][::-1]
    
    # Normalize just against the top few correlations instead of all 24
    top_n_correlations = np.sort(key_correlations)[-5:]  # Use top 5 correlations
    normalized_confidence = key_correlations[key_indexes[0]] / np.sum(top_n_correlations) * 100
    
    results = []
    for idx in key_indexes:
        key_name = get_key_name(idx)
        confidence = key_correlations[idx] / np.sum(top_n_correlations) * 100  # Use new normalization
        
        # Convert to Camelot notation
        if idx < 12:  # Major keys
            camelot, full_key = major_wheel.get(key_name, ('Unknown', f'{key_name} major'))
        else:  # Minor keys
            key_name = key_name.replace('b', '')+'m'  # Convert to minor notation
            camelot, full_key = minor_wheel.get(key_name, ('Unknown', f'{key_name}'))
            
        results.append((camelot, full_key, confidence))
        print(f"Possible key: {full_key} ({camelot}) - {confidence:.2f}% confidence")
    
    return results

def get_key_profiles():
    # Major and minor key profiles (Krumhansl-Kessler profiles)
    major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    
    # Generate all rotations for all possible keys
    key_profiles = []
    for i in range(12):
        key_profiles.append(np.roll(major_profile, i))
    for i in range(12):
        key_profiles.append(np.roll(minor_profile, i))
    return np.array(key_profiles)

def get_key_name(index):
    keys = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
    if index < 12:
        return keys[index]
    else:
        return keys[index - 12]

def update_gui_labels(key_results):
    labels = []
    for camelot, full_key, confidence in key_results:
        if confidence is not None:
            label = f"{camelot} - {full_key} ({confidence:.1f}% confidence)"
        else:
            label = f"{camelot} - {full_key}"
        labels.append(label)
    return labels

def detect_key_and_rename(file_path, bpm):
    """
    Detect key and rename file with both key and BPM
    Returns the path to the renamed file
    """
    print("Analyzing Key...")
    key_results = detect_key(file_path)
    
    # Use the highest confidence key
    camelot, full_key, confidence = key_results[0]
    
    # Create output directory if it doesn't exist
    directory = os.path.dirname(file_path)
    output_dir = os.path.join(directory, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Create copy with Key and BPM prefix
    filename = os.path.basename(file_path)
    new_filename = f"{camelot}_{bpm:.2f}BPM_{filename}"
    new_path = os.path.join(output_dir, new_filename)
    
    shutil.copy2(file_path, new_path)
    print(f"Created file with Key and BPM prefix: {new_filename}")
    
    return new_path  # Return the path to the new file

# Outer ring (Major keys - B notation)
major_wheel = {
    'C': ('8B', 'C major'),   'G': ('7B', 'G major'),   'D': ('6B', 'D major'),
    'A': ('5B', 'A major'),   'E': ('4B', 'E major'),   'B': ('3B', 'B major'),
    'F#': ('2B', 'F# major'), 'C#': ('1B', 'C# major'), 'Ab': ('12B', 'Ab major'),
    'Eb': ('11B', 'Eb major'),'Bb': ('10B', 'Bb major'),'F': ('9B', 'F major'),
    # Alternative notations
    'Gb': ('2B', 'F# major'), 'Db': ('1B', 'C# major'), 'G#': ('12B', 'Ab major'),
    'A#': ('10B', 'Bb major')
}

# Inner ring (Minor keys - A notation)
minor_wheel = {
    'Am': ('8A', 'A minor'),   'Em': ('9A', 'E minor'),   'Bm': ('10A', 'B minor'),
    'F#m': ('11A', 'F# minor'), 'C#m': ('12A', 'C# minor'), 'G#m': ('1A', 'G# minor'),
    'D#m': ('2A', 'D# minor'), 'A#m': ('3A', 'A# minor'), 'Fm': ('4A', 'F minor'),
    'Cm': ('5A', 'C minor'),  'Gm': ('6A', 'G minor'),  'Dm': ('7A', 'D minor'),
    # Alternative notations
    'Ebm': ('2A', 'D# minor'), 'Bbm': ('3A', 'A# minor'), 'Abm': ('1A', 'G# minor')
}