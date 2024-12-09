import os
import subprocess
import essentia.standard as es
import librosa

def detect_bpm_and_key(file_path):
    # Load audio file using essentia for key detection
    audio_loader = es.MonoLoader(filename=file_path)
    audio = audio_loader()
    
    # Load audio file using librosa for BPM detection
    y, sr = librosa.load(file_path)
    tempo = librosa.beat.tempo(y=y, sr=sr)[0]
    
    # Detect key using essentia
    key_extractor = es.KeyExtractor()
    key_data = key_extractor(audio)
    key = key_data[0]  # Assuming the first value is the key
    scale = key_data[1]  # Assuming the second value is the scale
    camelot_key = convert_to_camelot(key, scale)

    print(f"Detected key: {camelot_key}")
    print(f"Detected BPM: {tempo:.2f}")  # Keep two decimal places
    return camelot_key, tempo

def convert_to_camelot(key, scale):
    # Correct Camelot wheel mapping
    camelot_wheel = {
        'C': '8B', 'C#': '3B', 'D': '10B', 'D#': '5B', 'E': '12B', 'F': '7B',
        'F#': '2B', 'G': '9B', 'G#': '4B', 'A': '11B', 'A#': '6B', 'B': '1B',
        'C minor': '5A', 'C# minor': '12A', 'D minor': '7A', 'D# minor': '2A',
        'E minor': '9A', 'F minor': '4A', 'F# minor': '11A', 'G minor': '6A',
        'G# minor': '1A', 'A minor': '8A', 'A# minor': '3A', 'B minor': '10A'
    }
    key_name = f"{key} {scale}" if scale == 'minor' else key
    return camelot_wheel.get(key_name, 'Unknown')

def separate_stems(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.mp3') or filename.endswith('.wav'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.split('.')[0])

            # Detect key and BPM
            camelot_key, bpm = detect_bpm_and_key(input_path)

            # Run the demucs command
            subprocess.run(['demucs', input_path, '-o', output_folder, '--mp3'])

            # Rename output files
            stem_folder = os.path.join(output_folder, 'htdemucs', filename.split('.')[0])
            for stem_file in os.listdir(stem_folder):
                stem_name = stem_file.split('.')[0]
                new_name = f"{camelot_key}_{bpm:.2f}BPM_{filename.split('.')[0]}-{stem_name}.mp3"
                os.rename(os.path.join(stem_folder, stem_file), os.path.join(stem_folder, new_name))

            print(f"Processed {filename}")
            
            # Delete the original file
            # os.remove(input_path)
            print(f"Deleted original file: {filename}")

if __name__ == "__main__":
    input_folder = os.path.dirname(os.path.abspath(__file__))  # Current directory
    output_folder = os.path.join(input_folder, 'output')  # Output folder in the current directory
    separate_stems(input_folder, output_folder)