import os
import subprocess
from pathlib import Path

def separate_stems(input_file, output_folder):
    """
    Separates audio into drums, bass, vocals, and other stems using Demucs v4
    """
    # Ensure paths are strings
    input_file = str(input_file)
    output_folder = str(output_folder)
    
    # Calculate estimated time based on file size
    file_size = os.path.getsize(input_file) / (1024 * 1024)  # Size in MB
    estimated_time = max(1, min(5, int(file_size / 10)))
    
    print("\nSeparating stems...")
    print(f"Input: {input_file}")
    print(f"Output folder: {output_folder}")
    print(f"\nThis process typically takes {estimated_time}-{estimated_time + 1} minutes for this file size.")
    
    # Create output directory
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        # Run Demucs with fine-tuned model
        process = subprocess.run([
            'demucs',
            '-n', 'mdx_extra_q',         # Higher quality model
            '--mp3',
            '--segments', '10',          # Process in 10-second segments
            '--overlap', '10',           # 10% overlap between segments
            '--shifts', '2',             # Apply 2 shifts for better quality
            '--split-mode', 'overlap',   # Use overlap mode for splitting
            '-o', output_folder,
            input_file
        ], capture_output=True, text=True, check=True)
        
        # Get the base filename without extension
        base_name = Path(input_file).stem
        stem_folder = str(Path(output_folder) / 'htdemucs' / base_name)
        
        # The stems we expect
        expected_stems = {
            'drums': 'DRUMS',
            'bass': 'BASS',
            'vocals': 'VOX',
            'other': 'OTHER'
        }
        
        stem_paths = {}
        for stem, prefix in expected_stems.items():
            stem_path = str(Path(stem_folder) / f"{stem}.mp3")
            if not os.path.exists(stem_path):
                raise FileNotFoundError(f"Expected stem {stem} not found")
            stem_paths[prefix] = stem_path
            
        print("\nStem separation completed successfully!")
        return stem_paths
        
    except subprocess.CalledProcessError as e:
        print(f"\nError during stem separation: {e}")
        print(f"stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"\nUnexpected error during stem separation: {e}")
        return None