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
        float(np.mean(tonal_data[6])) # confidence - take mean of array
    )]
    
    # Also get alternative keys using KeyExtractor
    key_extractor = es.KeyExtractor()
    key_data = key_extractor(audio)
    key_estimates.append((
        str(key_data[0]),        # key
        str(key_data[1]),        # scale
        float(key_data[2])       # confidence
    ))
    
    # Now sorting will work with Python native types
    key_estimates.sort(key=lambda x: x[2], reverse=True)
    
    # Convert top 2 keys to Camelot notation (we only have 2 estimates)
    results = []
    for key, scale, confidence in key_estimates:
        camelot_key, full_key = convert_to_camelot(key, scale)
        results.append((camelot_key, full_key, confidence))
        print(f"Possible key: {full_key} ({camelot_key}) - {confidence:.2%} confidence")
    
    # If we need exactly 3 results, duplicate the highest confidence one
    while len(results) < 3:
        results.append(results[0])
    
    return results

def convert_to_camelot(key, scale):
    # Outer ring (Major keys - B notation)
    major_wheel = {
        'B': ('1B', 'B major'),   'F#': ('2B', 'F# major'),  'Db': ('3B', 'Db major'),
        'Ab': ('4B', 'Ab major'), 'Eb': ('5B', 'Eb major'),  'Bb': ('6B', 'Bb major'),
        'F': ('7B', 'F major'),   'C': ('8B', 'C major'),    'G': ('9B', 'G major'),
        'D': ('10B', 'D major'),  'A': ('11B', 'A major'),   'E': ('12B', 'E major'),
        # Alternative notations
        'C#': ('3B', 'Db major'), 'Gb': ('2B', 'F# major'),  'D#': ('5B', 'Eb major'),
        'G#': ('4B', 'Ab major'), 'A#': ('6B', 'Bb major')
    }
    
    # Inner ring (Minor keys - A notation)
    minor_wheel = {
        'G#': ('1A', 'G# minor'), 'D#': ('2A', 'D# minor'), 'Bb': ('3A', 'Bb minor'),
        'F': ('4A', 'F minor'),   'C': ('5A', 'C minor'),   'G': ('6A', 'G minor'),
        'D': ('7A', 'D minor'),   'A': ('8A', 'A minor'),   'E': ('9A', 'E minor'),
        'B': ('10A', 'B minor'),  'F#': ('11A', 'F# minor'),'C#': ('12A', 'C# minor'),
        # Alternative notations
        'Ab': ('1A', 'G# minor'), 'Eb': ('2A', 'D# minor'), 'A#': ('3A', 'Bb minor'),
        'Gb': ('11A', 'F# minor')
    }
    
    if scale == 'major':
        return major_wheel.get(key, ('Unknown', f'{key} major'))
    else:  # minor
        return minor_wheel.get(key, ('Unknown', f'{key} minor')) 

def update_gui_labels(detected_key, detected_key_confidence):
    # Only display the final key determination
    key_text = f"{detected_key} - {detected_key_confidence:.2f}% confidence"
    return key_text