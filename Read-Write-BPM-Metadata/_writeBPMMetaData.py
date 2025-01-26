import os
from pathlib import Path
from mutagen.wave import WAVE
from mutagen.id3 import ID3, TBPM
import subprocess
import plistlib

# Global BPM value (change this value as needed)
GLOBAL_BPM = 63.00  # Set your desired BPM here

def write_bpm_metadata(wav_file):
    """Write BPM metadata to a WAV file using multiple formats."""
    try:
        # First write using mutagen for ID3 tags
        audio = WAVE(wav_file)
        if audio.tags is None:
            audio.add_tags()
            
        bpm_frame = TBPM(encoding=3, text=str(GLOBAL_BPM))
        audio.tags['TBPM'] = bpm_frame
        audio.save()
        
        # Write Apple-specific metadata using xattr
        metadata = {
            'com.apple.iTunes.BPM': str(GLOBAL_BPM),
            'bpm': str(GLOBAL_BPM)
        }
        
        for key, value in metadata.items():
            try:
                cmd = ['xattr', '-w', key, value, str(wav_file)]
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                print(f"Warning: Could not write {key} metadata")
        
        print(f"Successfully wrote BPM {GLOBAL_BPM} to {wav_file}")
        
    except Exception as e:
        print(f"Error writing to {wav_file}: {str(e)}")
        return None

def main():
    # Get the current directory where the script is located
    current_dir = Path(__file__).parent
    
    # Find all WAV files in the directory
    wav_files = list(current_dir.glob('*.wav'))
    
    if not wav_files:
        print("No WAV files found in the directory.")
        return
    
    print(f"\nWriting BPM metadata ({GLOBAL_BPM}) to all WAV files...")
    print("-" * 50)
    
    # Write BPM to all files
    for wav_file in wav_files:
        write_bpm_metadata(wav_file)
        
    print("\nDone! The BPM should now be visible in Apple Music/iTunes.")
    print("Note: You may need to refresh Apple Music or re-add the files.")

if __name__ == "__main__":
    main()