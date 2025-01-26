import os
from pathlib import Path
from mutagen.wave import WAVE

def get_wav_metadata(wav_file):
    """Extract metadata from a WAV file."""
    try:
        # Open with mutagen
        audio = WAVE(wav_file)
        
        # Get basic WAV info
        print(f"Channels: {audio.info.channels}")
        print(f"Sample Rate: {audio.info.sample_rate} Hz")
        print(f"Length: {audio.info.length:.2f} seconds")
        
        # Try to get BPM from tags
        if audio.tags:
            if 'TBPM' in audio.tags:
                print(f"BPM: {audio.tags['TBPM'].text[0]}")
            else:
                print("No BPM metadata found")
        else:
            print("No metadata tags found")
                    
    except Exception as e:
        print(f"Error reading {wav_file}: {str(e)}")
        return None

def main():
    # Get the current directory where the script is located
    current_dir = Path(__file__).parent
    
    # Find all WAV files in the directory
    wav_files = list(current_dir.glob('*.wav'))
    
    if not wav_files:
        print("No WAV files found in the directory.")
        return
    
    print("WAV File Metadata:")
    print("-" * 50)
    
    for wav_file in wav_files:
        print(f"\nFile: {wav_file.name}")
        get_wav_metadata(wav_file)

if __name__ == "__main__":
    main() 