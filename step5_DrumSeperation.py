import os
import subprocess

def separate_drums(drum_stem_path, output_folder, camelot_key, bpm, base_name):
    """
    Further separates a drum stem into its component parts using drumsep model.
    """
    # Ensure we have absolute paths
    drum_stem_path = os.path.abspath(drum_stem_path)
    output_folder = os.path.abspath(output_folder)
    drums_output = os.path.join(output_folder, 'drum_parts_temp')
    
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        drumsep_path = os.path.join(script_dir, 'drumsep', 'drumsep')
        
        # Run drumsep script
        subprocess.run([
            'bash',
            drumsep_path,
            drum_stem_path,
            drums_output
        ], check=True)
        
        # Rename the separated drum parts with the naming convention
        drum_parts = {
            'drums_49469ca8_Bombo': 'kick',
            'drums_49469ca8_Redoblante': 'snare',
            'drums_49469ca8_Platillos': 'cymbals',
            'drums_49469ca8_Toms': 'toms'
        }
        
        for old_name, new_type in drum_parts.items():
            old_path = os.path.join(drums_output, '49469ca8', base_name, f'{old_name}.wav')
            if os.path.exists(old_path):
                new_name = f"{camelot_key}_{bpm:.2f}BPM_{base_name}-{new_type}.mp3"
                new_path = os.path.join(output_folder, new_name)
                # Convert to mp3 and move to final location
                subprocess.run([
                    'ffmpeg', '-i', old_path,
                    '-codec:a', 'libmp3lame', '-qscale:a', '2',
                    new_path
                ], check=True)
        
        # Clean up temporary files
        if os.path.exists(drums_output):
            import shutil
            shutil.rmtree(drums_output)
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during drum separation: {e}")
        return False