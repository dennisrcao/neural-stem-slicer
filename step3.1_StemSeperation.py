import os
import subprocess
from pathlib import Path

def separate_stems(input_file, output_folder):
    """
    Separates audio into drums, bass, vocals, and other stems using Demucs v4
    """
    print(f"Separating stems for {input_file}...")
    
    # Create output directory
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        # Run Demucs with 4-stem model
        subprocess.run([
            'demucs', 
            '--two-stems=false',  # We want 4 stems
            '-n', 'htdemucs',     # Use the latest model
            '--mp3',              # Output as MP3
            '-o', output_folder,
            input_file
        ], check=True)
        
        # Get the base filename without extension
        base_name = Path(input_file).stem
        stem_folder = os.path.join(output_folder, 'htdemucs', base_name)
        
        # The stems we expect
        expected_stems = ['drums', 'bass', 'vocals', 'other']
        stem_paths = {}
        
        # Verify and collect stem paths
        for stem in expected_stems:
            stem_path = os.path.join(stem_folder, f"{stem}.mp3")
            if not os.path.exists(stem_path):
                raise FileNotFoundError(f"Expected stem {stem} not found")
            stem_paths[stem] = stem_path
            
        return stem_paths
        
    except subprocess.CalledProcessError as e:
        print(f"Error during stem separation: {e}")
        return None