def separate_drums(drum_stem_path, output_folder, camelot_key, bpm, base_name):
    """
    Further separates a drum stem into its component parts using drumsep model.
    """
    drums_output = os.path.join(output_folder, 'drum_parts')
    os.makedirs(drums_output, exist_ok=True)
    
    # Get absolute path to the drumsep directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    drumsep_dir = os.path.join(current_dir, 'drumsep')
    drumsep_script = os.path.join(drumsep_dir, 'drumsep')
    
    # Make sure script is executable
    os.chmod(drumsep_script, 0o755)
    
    # Make sure we're in the drumsep directory when running the script
    original_dir = os.getcwd()
    os.chdir(drumsep_dir)
    
    # Run the separation
    try:
        subprocess.run([
            'bash',
            drumsep_script,
            drum_stem_path,
            drums_output
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running drumsep: {e}")
        os.chdir(original_dir)
        return
        
    # Change back to original directory
    os.chdir(original_dir)

    # Get parent folder of the drum_stem_path
    target_folder = os.path.dirname(drum_stem_path)

    # Define name translations
    drum_name_translations = {
        'bombo': 'kick',
        'redoblante': 'snare',
        'platillos': 'cymbals',
        'toms': 'toms'  # This one stays the same
    }

    # Process the separated drum parts
    model_output_folder = os.path.join(drums_output, '49469ca8')
    drum_parts_folder = os.path.join(model_output_folder, os.path.splitext(os.path.basename(drum_stem_path))[0])
    
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