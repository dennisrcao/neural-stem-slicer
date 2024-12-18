import essentia.standard as es
import numpy as np

def detect_key(file_path):
    print("Analyzing Key...")
    audio_loader = es.MonoLoader(filename=file_path)
    audio = audio_loader()
    
    # Get multiple key estimates with confidence scores
    tonal = es.TonalExtractor()
    tonal_data = tonal(audio)
    
    # Convert numpy arrays to Python floats for comparison
    key_estimates = [(
        str(tonal_data[4]),      # key
        str(tonal_data[5]),      # scale
        float(np.mean(tonal_data[6]))  # confidence - take mean of array
    )]
    
    # Also get alternative key using KeyExtractor
    key_extractor = es.KeyExtractor()
    key_data = key_extractor(audio)
    key_estimates.append((
        str(key_data[0]),        # key
        str(key_data[1]),        # scale
        float(key_data[2])       # confidence
    ))
    
    # Sort by confidence score
    key_estimates.sort(key=lambda x: x[2], reverse=True)
    
    # Convert top 2 keys to Camelot notation
    results = []
    for key, scale, confidence in key_estimates[:2]:
        if scale == 'major':
            camelot, full_key = major_wheel.get(key, ('Unknown', f'{key} major'))
        else:  # minor
            camelot, full_key = minor_wheel.get(key, ('Unknown', f'{key} minor'))
            
        if camelot != 'Unknown':
            results.append((camelot, full_key, confidence * 100))
        else:
            results.append((camelot, full_key, None))
            
        print(f"Possible key: {full_key} ({camelot}) - {confidence*100:.2f}% confidence")
    
    return results

def update_gui_labels(key_results):
    labels = []
    for camelot, full_key, confidence in key_results:
        if confidence is not None:
            label = f"{camelot} - {full_key} ({confidence:.1f}% confidence)"
        else:
            label = f"{camelot} - {full_key}"
        labels.append(label)
    return labels

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
    'Am': ('8A', 'A minor'),   'Em': ('7A', 'E minor'),   'Bm': ('6A', 'B minor'),
    'F#m': ('5A', 'F# minor'), 'C#m': ('4A', 'C# minor'), 'G#m': ('3A', 'G# minor'),
    'D#m': ('2A', 'D# minor'), 'A#m': ('1A', 'A# minor'), 'Fm': ('12A', 'F minor'),
    'Cm': ('11A', 'C minor'),  'Gm': ('10A', 'G minor'),  'Dm': ('9A', 'D minor'),
    # Alternative notations
    'Ebm': ('2A', 'D# minor'), 'Bbm': ('1A', 'A# minor'), 'Abm': ('3A', 'G# minor')
}