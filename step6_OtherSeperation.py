def separate_other(other_stem_path, output_folder, camelot_key, bpm, base_name):
    # For now, just copy the file without processing
    import shutil
    import os
    
    target_folder = os.path.dirname(other_stem_path)
    new_name = f"{camelot_key}_{bpm:.2f}BPM_{base_name}-other.mp3"
    new_path = os.path.join(target_folder, new_name)
    shutil.copy2(other_stem_path, new_path)
    return new_path 