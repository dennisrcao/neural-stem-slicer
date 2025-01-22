import os
import subprocess
from pathlib import Path

def separate_stems(input_file, output_folder):
    """
    Separates audio into drums, bass, vocals, and other stems using Demucs v4
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
        
        # Run demucs CLI command - removed the --two-stems flag to get all stems
        subprocess.run([
            'demucs',
            '--mp3',
            '-n', 'htdemucs',  # Use hybrid transformer model
            '--out', output_folder,
            input_file
        ], check=True)
        
        # Get the base name of the input file
        base_name = Path(input_file).stem
        
        # The stems will be in a subdirectory named after the model and input file
        stem_folder = os.path.join(output_folder, 'htdemucs', base_name)
        
        # Collect paths of generated stems
        stem_paths = {}
        if os.path.exists(stem_folder):
            for stem_file in os.listdir(stem_folder):
                if stem_file.endswith('.mp3'):
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