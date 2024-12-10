import os
import subprocess
import essentia.standard as es
import librosa
import numpy
import soundfile as sf
import pywt
import scipy
from scipy import signal, stats
import math

def detect_bpm(y, sr, start_bpm=None):
    print("Analyzing BPM...")
    
    # Convert to mono if needed
    if len(y.shape) > 1:
        y = y.mean(axis=1)
    
    # Use librosa's tempo detection with prior if provided
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo = librosa.beat.tempo(
        onset_envelope=onset_env, 
        sr=sr,
        start_bpm=start_bpm if start_bpm else 120.0,
        prior=None if start_bpm is None else scipy.stats.norm(loc=start_bpm, scale=1.0)
    )[0]
    
    return round(tempo, 2)

def detect_bpm_and_key(file_path):
    y, sr = librosa.load(file_path)
    tempo = detect_bpm(y, sr)
    
    audio_loader = es.MonoLoader(filename=file_path)
    audio = audio_loader()
    key_extractor = es.KeyExtractor()
    key_data = key_extractor(audio)
    key = key_data[0]
    scale = key_data[1]
    camelot_key = convert_to_camelot(key, scale)

    print(f"Detected key: {camelot_key}")
    print(f"Detected BPM: {tempo:.2f}")
    return camelot_key, tempo

def convert_to_camelot(key, scale):
    camelot_wheel = {
        'C': '8B', 'C#': '3B', 'D': '10B', 'D#': '5B', 'E': '12B', 'F': '7B',
        'F#': '2B', 'G': '9B', 'G#': '4B', 'A': '11B', 'A#': '6B', 'B': '1B',
        'C minor': '5A', 'C# minor': '12A', 'D minor': '7A', 'D# minor': '2A',
        'E minor': '9A', 'F minor': '4A', 'F# minor': '11A', 'G minor': '6A',
        'G# minor': '1A', 'A minor': '8A', 'A# minor': '3A', 'B minor': '10A'
    }
    key_name = f"{key} {scale}" if scale == 'minor' else key
    return camelot_wheel.get(key_name, 'Unknown')

def separate_drums(drum_stem_path, output_folder, camelot_key, bpm, base_name):
    """
    Further separates a drum stem into its component parts using drumsep model.
    """
    # Ensure we have absolute paths
    drum_stem_path = os.path.abspath(drum_stem_path)
    output_folder = os.path.abspath(output_folder)
    
    # Create a temporary directory for drum parts
    drums_output = os.path.join(output_folder, 'drum_parts_temp')
    os.makedirs(drums_output, exist_ok=True)
    
    # Get absolute path to the drumsep directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    drumsep_dir = os.path.join(current_dir, 'drumsep')
    drumsep_script = os.path.join(drumsep_dir, 'drumsep')
    
    # Make sure script is executable
    os.chmod(drumsep_script, 0o755)
    
    # Store original directory and change to drumsep directory
    original_dir = os.getcwd()
    os.chdir(drumsep_dir)
    
    print(f"Processing drum stem: {drum_stem_path}")
    print(f"Temporary output directory: {drums_output}")
    
    try:
        # Verify the drum stem exists before processing
        if not os.path.exists(drum_stem_path):
            print(f"Error: Drum stem file not found at {drum_stem_path}")
            return
            
        # Run the separation
        subprocess.run([
            'bash',
            drumsep_script,
            drum_stem_path,
            drums_output
        ], check=True)
        
        # Get the directory where the original drum stem is located
        target_folder = os.path.dirname(drum_stem_path)
        
        # Process the separated drum parts
        model_output_folder = os.path.join(drums_output, '49469ca8')
        drum_parts_folder = os.path.join(model_output_folder, os.path.splitext(os.path.basename(drum_stem_path))[0])
        
        # Define name translations
        drum_name_translations = {
            'bombo': 'kick',
            'redoblante': 'snare',
            'platillos': 'cymbals',
            'toms': 'toms'
        }
        
        if os.path.exists(drum_parts_folder):
            for drum_part in os.listdir(drum_parts_folder):
                if drum_part.endswith('.mp3') or drum_part.endswith('.wav'):
                    part_name = os.path.splitext(drum_part)[0]
                    # Translate the drum part name
                    for spanish, english in drum_name_translations.items():
                        if spanish in part_name.lower():
                            part_name = english
                            break
                    
                    new_part_name = f"{camelot_key}_{bpm:.2f}BPM_{base_name}-drums-{part_name}.mp3"
                    
                    # Move file directly to target folder
                    os.rename(
                        os.path.join(drum_parts_folder, drum_part),
                        os.path.join(target_folder, new_part_name)
                    )
            
            # Clean up temporary folders
            os.rmdir(drum_parts_folder)
            os.rmdir(model_output_folder)
            os.rmdir(drums_output)
            
    except subprocess.CalledProcessError as e:
        print(f"Error running drumsep: {e}")
    except Exception as e:
        print(f"Error processing drum parts: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always change back to original directory
        os.chdir(original_dir)

def separate_stems(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith('.mp3') or filename.endswith('.wav'):
            input_path = os.path.join(input_folder, filename)
            
            # Step 1: Analyze original song ONCE
            camelot_key, bpm = detect_bpm_and_key(input_path)
            base_name = filename.split('.')[0]
            print(f"Separating stems for {filename}...")
            
            try:
                # Step 2: Initial stem separation
                subprocess.run(
                    ['demucs', input_path, '-o', output_folder, '--mp3'],
                    check=True
                )
                
                stem_folder = os.path.join(output_folder, 'htdemucs', base_name)
                if not os.path.exists(stem_folder):
                    print(f"Error: Stem folder not created for {filename}")
                    continue
                
                # Step 3: Rename all stems with consistent naming
                drum_stem_path = None
                for stem_file in os.listdir(stem_folder):
                    stem_name = stem_file.split('.')[0]
                    new_name = f"{camelot_key}_{bpm:.2f}BPM_{base_name}-{stem_name}.mp3"
                    full_stem_path = os.path.join(stem_folder, stem_file)
                    new_stem_path = os.path.join(stem_folder, new_name)
                    os.rename(full_stem_path, new_stem_path)
                    
                    # Store drum stem path for later processing
                    if "drums" in stem_name.lower():
                        drum_stem_path = new_stem_path

                # Step 4: Process drums separately if found
                if drum_stem_path:
                    separate_drums(drum_stem_path, stem_folder, camelot_key, bpm, base_name)

            except subprocess.CalledProcessError as e:
                print(f"Error processing {filename}: {e}")
            except Exception as e:
                print(f"Unexpected error processing {filename}: {e}")
            print(f"Successfully processed {filename}")

if __name__ == "__main__":
    input_folder = "."
    output_folder = "output"
    separate_stems(input_folder, output_folder)