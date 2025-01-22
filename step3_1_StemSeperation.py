import os
import subprocess
from pathlib import Path

def separate_stems(input_file, output_folder, progress_callback=None):
    """
    Separates audio into drums, bass, vocals, and other stems using Demucs v4
    progress_callback: function(progress_percent, status_text)
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
        
        # Use subprocess.Popen instead of run to capture output in real-time
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
        
        # Get the base name of the input file
        base_name = Path(input_file).stem
        
        # The stems will be in a subdirectory named after the model and input file
        stem_folder = os.path.join(output_folder, 'htdemucs', base_name)
        
        # Collect paths of generated stems
        stem_paths = {}
        if os.path.exists(stem_folder):
            for stem_file in os.listdir(stem_folder):
                if stem_file.endswith('.wav'):
                    stem_name = stem_file.split('.')[0].upper()
                    stem_path = os.path.join(stem_folder, stem_file)
                    stem_paths[stem_name] = stem_path
                    print(f"Found {stem_name} stem at {stem_path}")
        
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