import os
from pydub import AudioSegment
import re
import librosa
import soundfile as sf

def calculate_bar_length_ms(bpm):
    """Calculate length of one bar in milliseconds"""
    beats_per_bar = 4  # assuming 4/4 time
    ms_per_minute = 60000
    return (beats_per_bar * ms_per_minute) / bpm

def extract_bpm_from_filename(filename):
    """Extract BPM from filename like '10A_121.00BPM_...'"""
    match = re.search(r'(\d+\.?\d*)BPM', filename)
    if match:
        return float(match.group(1))
    raise ValueError(f"Could not extract BPM from filename: {filename}")

def calculate_samples_per_bar(bpm, sample_rate):
    """Calculate exact number of samples for one bar"""
    beats_per_bar = 4  # 4/4 time
    samples_per_beat = (60.0 / bpm) * sample_rate
    samples_per_bar = samples_per_beat * beats_per_bar
    # Use round instead of int for better accuracy
    return round(samples_per_bar)

def chop_stems_to_segments(stems_folder, crossfade_samples=0):
    """
    Chop stems into precise 8-bar segments based on sample count
    Returns: Total number of segments created
    """
    segments_folder = os.path.join(stems_folder, 'segments')
    os.makedirs(segments_folder, exist_ok=True)
    
    stem_files = [f for f in os.listdir(stems_folder) 
                 if f.endswith('.wav') and os.path.isfile(os.path.join(stems_folder, f))]
    
    if not stem_files:
        print("No WAV files found in stems folder")
        return 0
    
    total_segments = 0  # Track total segments across all files
    
    # Get original audio info from first file to ensure consistency
    first_file = os.path.join(stems_folder, stem_files[0])
    info = sf.info(first_file)
    bpm = extract_bpm_from_filename(stem_files[0])
    
    print(f"\nReference audio properties:")
    print(f"Sample rate: {info.samplerate} Hz")
    print(f"Subtype: {info.subtype}")
    print(f"BPM: {bpm}")
    
    # Calculate exact sample counts
    samples_per_bar = calculate_samples_per_bar(bpm, info.samplerate)
    samples_per_8bars = samples_per_bar * 8
    
    print(f"Samples per bar: {samples_per_bar}")
    print(f"Samples per 8 bars: {samples_per_8bars}")
    
    for stem_file in stem_files:
        try:
            input_path = os.path.join(stems_folder, stem_file)
            # Load audio maintaining ALL original properties
            y, sr = sf.read(input_path)
            
            # Verify sample rate matches reference
            if sr != info.samplerate:
                print(f"Warning: Sample rate mismatch in {stem_file}")
                continue
            
            num_segments = len(y) // samples_per_8bars
            file_segments = 0  # Track segments for this file
            
            for i in range(num_segments):
                start_sample = i * samples_per_8bars
                end_sample = start_sample + samples_per_8bars
                
                segment = y[start_sample:end_sample]
                
                # Calculate actual starting bar number (1, 9, 17, etc.)
                starting_bar = (i * 8) + 1
                
                # Save with bar number indicating actual starting position
                output_path = os.path.join(segments_folder, f"B{starting_bar}_{stem_file}")
                sf.write(output_path, segment, sr, 
                        subtype=info.subtype,
                        format=info.format)
                
                file_segments += 1
                total_segments += 1
                
            print(f"Created {file_segments} segments for {stem_file}")
            
        except Exception as e:
            print(f"Error processing {stem_file}: {e}")
            continue
    
    print(f"\nTotal segments created across all files: {total_segments}")
    return total_segments  # Return the total count

def process_stems_to_segments(stems_dir, progress_callback=None):
    """
    Main function to process stems into segments
    Returns: True if successful, False otherwise
    """
    try:
        print("\nStarting stem segmentation...")
        num_segments = chop_stems_to_segments(stems_dir)
        if num_segments > 0:
            print(f"\nSuccessfully created {num_segments} segments!")
            return True
        else:
            print("\nNo segments were created.")
            return False
    except Exception as e:
        print(f"Error in stem segmentation: {e}")
        import traceback
        traceback.print_exc()
        return False 