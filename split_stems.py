import os
import subprocess
import essentia.standard as es
import librosa
import numpy
import soundfile as sf
import pywt
from scipy import signal
import math

def detect_bpm(y, sr):
    print("Analyzing BPM...")
    
    # Convert to mono and downsample if needed
    if len(y.shape) > 1:
        y = y.mean(axis=1)
    
    # Reduce audio length if it's too long (e.g., analyze first 60 seconds)
    max_length = 60 * sr  # 60 seconds
    if len(y) > max_length:
        print("Using first 60 seconds for BPM detection...")
        y = y[:max_length]
    
    levels = 4
    max_decimation = 2 ** (levels - 1)
    min_ndx = math.floor(60.0 / 220 * (sr / max_decimation))
    max_ndx = math.floor(60.0 / 40 * (sr / max_decimation))
    
    cA = y
    cD_sum = numpy.zeros(math.floor(len(y) / max_decimation + 1))
    
    for loop in range(0, levels):
        print(f"Processing wavelet level {loop + 1}/{levels}...")
        cA, cD = pywt.dwt(cA, "db4")
        cD = signal.lfilter([0.01], [1 - 0.99], cD)
        cD = abs(cD[:: (2 ** (levels - loop - 1))])
        cD = cD - numpy.mean(cD)
        cD_sum[:len(cD)] += cD
    
    print("Calculating final BPM...")
    correl = numpy.correlate(cD_sum, cD_sum, "full")
    midpoint = len(correl) // 2
    correl_midpoint = correl[midpoint:]
    peak_ndx = numpy.argmax(correl_midpoint[min_ndx:max_ndx]) + min_ndx
    bpm = 60.0 / peak_ndx * (sr / max_decimation)
    
    return round(bpm, 2)

def detect_first_onset(y, sr):
    tempo = detect_bpm(y, sr)
    beat_frames = librosa.beat.beat_track(y=y, sr=sr, start_bpm=tempo)[1]
    
    onset_env = librosa.onset.onset_strength(
        y=y, 
        sr=sr,
        hop_length=512,
        aggregate=numpy.median
    )
    
    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=512,
        backtrack=True
    )
    
    if len(onset_frames) > 0 and len(beat_frames) > 0:
        for onset in onset_frames:
            if any(abs(onset - beat) < 2 for beat in beat_frames):
                first_onset_time = librosa.frames_to_time(onset, sr=sr)
                buffer_time = 0.05
                return max(0, first_onset_time - buffer_time)
    
    if len(onset_frames) > 0:
        return librosa.frames_to_time(onset_frames[0], sr=sr)
    return 0

def trim_audio(file_path):
    y, sr = librosa.load(file_path)
    first_onset = detect_first_onset(y, sr)
    start_sample = int(first_onset * sr)
    y_trimmed = y[start_sample:]
    trimmed_path = file_path.rsplit('.', 1)[0] + '_trimmed.' + file_path.rsplit('.', 1)[1]
    sf.write(trimmed_path, y_trimmed, sr)
    return trimmed_path

def detect_bpm_and_key(file_path):
    y, sr = librosa.load(file_path)
    tempo = detect_bpm(y, sr)
    
    audio_loader = es.MonoLoader(filename=file_path)
    audio = audio_loader()
    key_extractor = es.KeyExtractor()
    key_data = key_extractor(audio)
    key = key_data[0]
    scale = key_data[1]
    camelot_key = convert_to_camelot(key, scale)

    print(f"Detected key: {camelot_key}")
    print(f"Detected BPM: {tempo:.2f}")
    return camelot_key, tempo

def convert_to_camelot(key, scale):
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
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith('.mp3') or filename.endswith('.wav'):
            input_path = os.path.join(input_folder, filename)
            camelot_key, bpm = detect_bpm_and_key(input_path)
            trimmed_path = trim_audio(input_path)
            subprocess.run(['demucs', trimmed_path, '-o', output_folder, '--mp3'])
            
            base_name = filename.split('.')[0]
            stem_folder = os.path.join(output_folder, 'htdemucs', base_name + '_trimmed')
            for stem_file in os.listdir(stem_folder):
                stem_name = stem_file.split('.')[0]
                new_name = f"{camelot_key}_{bpm:.2f}BPM_{base_name}-{stem_name}.mp3"
                os.rename(os.path.join(stem_folder, stem_file), 
                         os.path.join(stem_folder, new_name))

            print(f"Processed {filename}")
            os.remove(input_path)
            os.remove(trimmed_path)
            print(f"Deleted original and trimmed files")

if __name__ == "__main__":
    input_folder = os.path.dirname(os.path.abspath(__file__))
    output_folder = os.path.join(input_folder, 'output')
    separate_stems(input_folder, output_folder)