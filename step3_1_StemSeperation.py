import os
import subprocess
from pathlib import Path

def separate_stems(input_file, output_folder):
    """
    Separates audio into drums, bass, vocals, and other stems using Demucs v4
    """
    # Calculate estimated time based on file size
    file_size = os.path.getsize(input_file) / (1024 * 1024)  # Size in MB
    estimated_time = max(1, min(5, int(file_size / 10)))  # Rough estimate: 10MB per minute
    
    print("\nSeparating stems...")
    print(f"Input: {input_file}")
    print(f"Output folder: {output_folder}")
    print(f"\nThis process typically takes {estimated_time}-{estimated_time + 1} minutes for this file size.")
    print("Progress indicators:")
    print("1. Loading model... (10%)")
    print("2. Processing audio... (30%)")
    print("3. Separating stems... (50%)")
    print("4. Saving files... (90%)")
    print("\nCurrent status: Loading model...\n")
    
    # Create output directory
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        # Run Demucs with 4-stem model and progress bar
        process = subprocess.Popen([
            'demucs', 
            '--two-stems=false',
            '-n', 'htdemucs',
            '--mp3',
            '-o', output_folder,
            input_file
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        # Track progress stages
        stages = {
            'Loading model': 10,
            'Processing audio': 30,
            'Separating stems': 50,
            'Saving files': 90
        }
        current_stage = 'Loading model'
        
        # Print progress
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                output = output.strip()
                print(output)
                
                # Update progress based on output content
                for stage in stages:
                    if stage.lower() in output.lower():
                        if stage != current_stage:
                            current_stage = stage
                            print(f"\nCurrent status: {current_stage} ({stages[stage]}%)")
                
        print("\nFinalizing...")
        
        # Get the base filename without extension
        base_name = Path(input_file).stem
        stem_folder = os.path.join(output_folder, 'htdemucs', base_name)
        
        # The stems we expect
        expected_stems = {
            'drums': 'Drums',
            'bass': 'Bass',
            'vocals': 'Vox',
            'other': 'Other'
        }
        
        stem_paths = {}
        for stem, prefix in expected_stems.items():
            stem_path = os.path.join(stem_folder, f"{stem}.mp3")
            if not os.path.exists(stem_path):
                raise FileNotFoundError(f"Expected stem {stem} not found")
            stem_paths[prefix] = stem_path
            
        print("\nStem separation completed successfully!")
        return stem_paths
        
    except subprocess.CalledProcessError as e:
        print(f"\nError during stem separation: {e}")
        return None