import os
import subprocess
from pathlib import Path
import shutil
import re

def separate_stems(input_file, output_folder, progress_callback=None, prefix=''):
    """
    Separates audio into drums, bass, vocals, and other stems using Demucs v4
    progress_callback: function(progress_percent, status_text)
    prefix: string to prepend to output filenames (e.g. "11A_120.00BPM_")
    """
    # Ensure paths are strings and absolute
    input_file = str(Path(input_file).absolute())
    output_folder = str(Path(output_folder).absolute())
    
    print("\nSeparating stems...")
    print(f"Input: {input_file}")
    print(f"Output folder: {output_folder}")
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Use subprocess.Popen for demucs
        process = subprocess.Popen(
            [
                'demucs',
                '-n', 'htdemucs',
                '--out', output_folder,
                input_file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Monitor the output
        while True:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
                
            # Parse progress from demucs output
            if "%" in line:
                try:
                    progress = float(line.split("%")[0].strip())
                    if progress_callback:
                        progress_callback(progress, f"Separating stems: {progress:.1f}%")
                except ValueError:
                    pass
        
        # Get the base name without any existing prefix
        input_filename = Path(input_file).stem
        base_name = input_filename
        
        # The stems will be in a subdirectory named after the model and input file
        temp_stem_folder = os.path.join(output_folder, 'htdemucs', Path(input_file).stem)
        
        # Move and rename stems to the main output folder
        stem_paths = {}
        if os.path.exists(temp_stem_folder):
            for stem_file in os.listdir(temp_stem_folder):
                if stem_file.endswith('.wav'):
                    stem_type = stem_file.split('.')[0]  # drums, bass, vocals, other
                    old_path = os.path.join(temp_stem_folder, stem_file)
                    
                    # Use the provided prefix for the new filename
                    new_name = f"{prefix}{base_name}_{stem_type}.wav"
                    new_path = os.path.join(output_folder, new_name)
                    shutil.move(old_path, new_path)
                    stem_paths[stem_type.upper()] = new_path
                    print(f"Created {stem_type} stem at {new_path}")
            
            # Clean up the temporary folder structure
            shutil.rmtree(os.path.dirname(temp_stem_folder))
        
        if stem_paths:
            print("\nStem separation completed successfully!")
            return stem_paths
        else:
            print("\nNo stems were generated!")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"\nError during stem separation: {e}")
        return None
    except Exception as e:
        print(f"\nUnexpected error during stem separation: {e}")
        import traceback
        traceback.print_exc()
        return None