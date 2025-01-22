import os
import subprocess
from pathlib import Path

def separate_drums(drum_stem_path, output_folder, camelot_key, bpm, base_name):
    """
    Separates a drum stem into kick, snare, cymbals, and toms
    Returns True if successful, False otherwise
    """
    try:
        # Create temporary output directory for drum separation
        drums_output = os.path.join(output_folder, 'drum_parts_temp')
        os.makedirs(drums_output, exist_ok=True)
        
        # Debug prints for path resolution
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"\nPath Resolution Debug:")
        print(f"1. Current directory: {current_dir}")
        
        drumsep_dir = os.path.join(current_dir, 'step3_0_Seperation_Models', 'drumsep')
        print(f"2. Drumsep directory: {drumsep_dir}")
        
        drumsep_script = os.path.join(drumsep_dir, 'drumsep')
        print(f"3. Drumsep script: {drumsep_script}")
        print(f"   Script exists? {os.path.exists(drumsep_script)}")
        
        model_dir = os.path.join(drumsep_dir, "model")
        model_path = os.path.join(model_dir, "49469ca8.th")
        print(f"4. Model directory: {model_dir}")
        print(f"   Model exists? {os.path.exists(model_path)}")
        print(f"   Model path: {model_path}")
        
        if not os.path.exists(drumsep_script):
            raise FileNotFoundError(f"Drumsep script not found at {drumsep_script}")
            
        # Make sure script is executable
        os.chmod(drumsep_script, 0o755)
        
        # Make sure model directory exists
        if not os.path.exists(model_dir):
            raise FileNotFoundError(f"Model directory not found at {model_dir}. Please run drumsepInstall.py first")
            
        # Store original directory and change to drumsep directory
        original_dir = os.getcwd()
        os.chdir(drumsep_dir)
        
        try:
            print("\nStarting drum separation subprocess...")
            # Run the separation using the bash script
            subprocess.run([
                'bash',
                drumsep_script,
                drum_stem_path,
                drums_output
            ], check=True)
            print("Drum separation subprocess completed")
            
        finally:
            print(f"Changing back to original directory: {original_dir}")
            os.chdir(original_dir)
        
        print("\nChecking for separated drum parts...")
        model_output = os.path.join(drums_output, '49469ca8')
        input_name = Path(drum_stem_path).stem
        parts_folder = os.path.join(model_output, input_name)
        print(f"Looking for parts in: {parts_folder}")
        
        if not os.path.exists(parts_folder):
            print(f"Parts folder not found at: {parts_folder}")
            print(f"Contents of {drums_output}:")
            if os.path.exists(drums_output):
                print(os.listdir(drums_output))
            return False
            
        print(f"Contents of parts folder:")
        print(os.listdir(parts_folder))
        
        # Define the drum components mapping (updated to match actual output)
        drum_parts = {
            'bombo': 'kick',
            'redoblante': 'snare',
            'platillos': 'cymbals',
            'toms': 'toms'
        }
        
        # Rename and move each drum component
        for old_name, new_type in drum_parts.items():
            # Look for .wav files instead of .mp3
            old_path = os.path.join(parts_folder, f"{old_name}.wav")
            print(f"\nChecking for {old_name}...")
            print(f"Looking at: {old_path}")
            if os.path.exists(old_path):
                new_name = f"{base_name}_drum_{new_type}.mp3"
                new_path = os.path.join(output_folder, new_name)
                print(f"Converting and moving to: {new_path}")
                
                # Convert wav to mp3 using ffmpeg
                import ffmpeg
                try:
                    stream = ffmpeg.input(old_path)
                    stream = ffmpeg.output(stream, new_path, acodec='libmp3lame', q=0)
                    ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
                    print(f"Converted and moved {old_name} to {new_type}")
                except ffmpeg.Error as e:
                    print(f"Error converting {old_name}: {e.stderr.decode()}")
            else:
                print(f"File not found: {old_path}")
        
        # Clean up temporary files
        print("\nCleaning up temporary files...")
        import shutil
        if os.path.exists(drums_output):
            shutil.rmtree(drums_output)
            print("Cleanup complete")
            
        return True
        
    except Exception as e:
        print(f"Error during drum separation: {e}")
        import traceback
        traceback.print_exc()
        return False