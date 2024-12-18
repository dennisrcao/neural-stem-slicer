import os
import subprocess

def separate_stems(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(input_folder):
        if filename.endswith(('.mp3', '.wav', '.m4a')):
            input_path = os.path.join(input_folder, filename)
            
            # Convert m4a to wav if needed
            if filename.endswith('.m4a'):
                print(f"Converting {filename} from m4a to wav...")
                wav_path = os.path.join(input_folder, f"{os.path.splitext(filename)[0]}.wav")
                subprocess.run(['ffmpeg', '-i', input_path, wav_path], check=True)
                input_path = wav_path
            
            base_name = filename.split('.')[0]
            print(f"Separating stems for {filename}...")
            
            try:
                # Initial stem separation
                subprocess.run(
                    ['demucs', input_path, '-o', output_folder, '--mp3'],
                    check=True
                )
                
                stem_folder = os.path.join(output_folder, 'htdemucs', base_name)
                if not os.path.exists(stem_folder):
                    print(f"Error: Stem folder not created for {filename}")
                    continue
                
                return stem_folder, base_name
                
            except subprocess.CalledProcessError as e:
                print(f"Error processing {filename}: {e}")
                return None, None