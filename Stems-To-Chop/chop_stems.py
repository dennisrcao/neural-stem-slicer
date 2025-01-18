import os
import argparse
from pydub import AudioSegment

def calculate_bar_length_ms(bpm):
    """Calculate length of one bar in milliseconds"""
    beats_per_bar = 4  # assuming 4/4 time
    ms_per_minute = 60000
    return (beats_per_bar * ms_per_minute) / bpm

def chop_and_organize_stems(input_dir, bpm, crossfade_ms=10):
    # Calculate length of 8 bars in milliseconds
    eight_bar_length = calculate_bar_length_ms(bpm) * 8
    
    # Get all mp3 files
    audio_files = [f for f in os.listdir(input_dir) if f.endswith('.mp3')]
    if not audio_files:
        print("No audio files found in the directory.")
        return
    
    print(f"Found {len(audio_files)} audio files.")
    
    # Create output directory in the root
    output_dir = 'song_stems_chopped'
    os.makedirs(output_dir, exist_ok=True)
    
    for audio_file in audio_files:
        try:
            # Load audio file
            audio_path = os.path.join(input_dir, audio_file)
            audio = AudioSegment.from_mp3(audio_path)
            
            # Calculate number of 8-bar segments
            num_segments = int(len(audio) // eight_bar_length)
            
            # Chop and save segments
            for i in range(num_segments):
                start_time = i * eight_bar_length
                end_time = start_time + eight_bar_length
                segment = audio[start_time:end_time]
                
                # Apply crossfade
                if i > 0:
                    segment = segment.fade_in(crossfade_ms)
                
                # Create new filename with 8Bar_X_ prefix
                new_filename = f"8Bar_{i+1}_{audio_file}"
                output_path = os.path.join(output_dir, new_filename)
                
                # Export segment
                segment.export(output_path, format="mp3")
            
            print(f"✔ 8 Bar segments created for {audio_file}")
        
        except Exception as e:
            print(f"Error processing {audio_file}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Chop audio stems into 8-bar segments')
    parser.add_argument('bpm', type=int, help='Tempo in BPM')
    parser.add_argument('--input_dir', default='song_stems_full',
                      help='Directory containing audio stems')
    
    args = parser.parse_args()
    
    chop_and_organize_stems(args.input_dir, args.bpm)

if __name__ == "__main__":
    main() 