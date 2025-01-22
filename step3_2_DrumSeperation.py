import os
import subprocess
from pathlib import Path
import soundfile as sf
import librosa
import numpy as np
import shutil
import time

def separate_drums(drum_stem_path, output_folder, camelot_key, bpm, base_name):
    """
    Separates a drum stem into kick, snare, cymbals, and toms
    Returns True if successful, False otherwise
    """
    try:
        print("\n=== Starting Drum Separation Process ===")
        print(f"Input drum stem: {drum_stem_path}")
        print(f"Output folder: {output_folder}")
        
        # Create temporary output directory for drum separation
        drums_output = os.path.join(output_folder, 'drum_parts_temp')
        os.makedirs(drums_output, exist_ok=True)
        
        # Debug prints for path resolution
        current_dir = os.path.dirname(os.path.abspath(__file__))
        drumsep_dir = os.path.join(current_dir, 'step3_0_Seperation_Models', 'drumsep')
        drumsep_script = os.path.join(drumsep_dir, 'drumsep')
        
        print(f"\nPath Configuration:")
        print(f"Current directory: {current_dir}")
        print(f"Drumsep directory: {drumsep_dir}")
        print(f"Drumsep script: {drumsep_script}")
        
        if not os.path.exists(drumsep_script):
            raise FileNotFoundError(f"Drumsep script not found at {drumsep_script}")
            
        # Make script executable
        os.chmod(drumsep_script, 0o755)
        
        # Get original audio info before processing
        y_orig, sr_orig = librosa.load(drum_stem_path, sr=None)
        orig_len = len(y_orig)
        orig_duration = librosa.get_duration(y=y_orig, sr=sr_orig)
        
        print(f"\nOriginal Audio Properties:")
        print(f"Sample rate: {sr_orig} Hz")
        print(f"Duration: {orig_duration:.2f} seconds")
        print(f"Total samples: {orig_len}")
        
        # Store original directory and change to drumsep directory
        original_dir = os.getcwd()
        os.chdir(drumsep_dir)
        
        try:
            print("\nStarting drum separation subprocess...")
            start_time = time.time()
            
            # Run the separation using the bash script directly on the drum stem
            process = subprocess.run([
                'bash',
                drumsep_script,
                drum_stem_path,
                drums_output
            ], check=True, capture_output=True, text=True)
            
            print(f"Separation completed in {time.time() - start_time:.2f} seconds")
            if process.stderr:
                print("Subprocess stderr output:")
                print(process.stderr)
            
        finally:
            os.chdir(original_dir)
        
        # Find the output directory (should be under the model name)
        model_output = os.path.join(drums_output, '49469ca8')
        input_name = Path(drum_stem_path).stem
        parts_folder = os.path.join(model_output, input_name)
        
        if not os.path.exists(parts_folder):
            print(f"Parts folder not found at: {parts_folder}")
            return False
            
        print(f"\nFound separated parts in: {parts_folder}")
        print("Contents:", os.listdir(parts_folder))
        
        # Define the drum components mapping
        drum_parts = {
            'bombo': 'kick',
            'redoblante': 'snare',
            'platillos': 'cymbals',
            'toms': 'toms'
        }
        
        print("\nProcessing individual components:")
        # Process each component
        for old_name, new_type in drum_parts.items():
            old_path = os.path.join(parts_folder, f"{old_name}.wav")
            if os.path.exists(old_path):
                print(f"\nProcessing {new_type}:")
                # Load at original sample rate
                y, sr = librosa.load(old_path, sr=sr_orig)
                
                print(f"- Loaded {new_type} component:")
                print(f"  Sample rate: {sr} Hz")
                print(f"  Duration: {librosa.get_duration(y=y, sr=sr):.2f} seconds")
                print(f"  Samples: {len(y)}")
                
                # Ensure exact length match
                if len(y) != orig_len:
                    print(f"- Length mismatch for {new_type}:")
                    print(f"  Original: {orig_len} samples")
                    print(f"  Component: {len(y)} samples")
                    print(f"  Difference: {abs(len(y) - orig_len)} samples")
                    
                    # Trim or pad to match original exactly
                    if len(y) > orig_len:
                        print(f"  Trimming {len(y) - orig_len} samples")
                        y = y[:orig_len]
                    else:
                        print(f"  Padding {orig_len - len(y)} samples")
                        y = np.pad(y, (0, orig_len - len(y)))
                
                new_name = f"{base_name}_drum_{new_type}.wav"
                new_path = os.path.join(output_folder, new_name)
                
                # Use soundfile to write WAV directly instead of ffmpeg MP3 conversion
                sf.write(new_path, y, sr, subtype='PCM_24')
                print(f"  Saved WAV file: {new_path}")
        
        # Clean up temporary files
        print("\nCleaning up temporary files...")
        shutil.rmtree(drums_output)
        print("Cleanup complete")
        return True
        
    except Exception as e:
        print(f"\nError during drum separation: {e}")
        import traceback
        traceback.print_exc()
        return False