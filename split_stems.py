import os
import subprocess
import essentia.standard as es
import librosa
import numpy
import soundfile as sf
import pywt
import scipy
from scipy import signal, stats
import math
import shutil
import tkinter as tk
from tkinter import ttk, filedialog

def detect_bpm(y, sr, start_bpm=None):
    print("Analyzing BPM...")
    
    # Convert to mono if needed
    if len(y.shape) > 1:
        y = y.mean(axis=1)
    
    # Use librosa's tempo detection with prior if provided
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo = librosa.beat.tempo(
        onset_envelope=onset_env, 
        sr=sr,
        start_bpm=start_bpm if start_bpm else 120.0,
        prior=None if start_bpm is None else scipy.stats.norm(loc=start_bpm, scale=1.0)
    )[0]
    
    return round(tempo, 2)

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

def separate_drums(drum_stem_path, output_folder, camelot_key, bpm, base_name):
    """
    Further separates a drum stem into its component parts using drumsep model.
    """
    # Ensure we have absolute paths
    drum_stem_path = os.path.abspath(drum_stem_path)
    output_folder = os.path.abspath(output_folder)
    
    # Create a temporary directory for drum parts
    drums_output = os.path.join(output_folder, 'drum_parts_temp')
    os.makedirs(drums_output, exist_ok=True)
    
    # Get absolute path to the drumsep directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    drumsep_dir = os.path.join(current_dir, 'drumsep')
    drumsep_script = os.path.join(drumsep_dir, 'drumsep')
    
    # Make sure script is executable
    os.chmod(drumsep_script, 0o755)
    
    # Store original directory and change to drumsep directory
    original_dir = os.getcwd()
    os.chdir(drumsep_dir)
    
    print(f"Processing drum stem: {drum_stem_path}")
    print(f"Temporary output directory: {drums_output}")
    
    try:
        # Verify the drum stem exists before processing
        if not os.path.exists(drum_stem_path):
            print(f"Error: Drum stem file not found at {drum_stem_path}")
            return
            
        # Run the separation
        subprocess.run([
            'bash',
            drumsep_script,
            drum_stem_path,
            drums_output
        ], check=True)
        
        # Get the directory where the original drum stem is located
        target_folder = os.path.dirname(drum_stem_path)
        
        # Process the separated drum parts
        model_output_folder = os.path.join(drums_output, '49469ca8')
        drum_parts_folder = os.path.join(model_output_folder, os.path.splitext(os.path.basename(drum_stem_path))[0])
        
        # Define name translations
        drum_name_translations = {
            'bombo': 'kick',
            'redoblante': 'snare',
            'platillos': 'cymbals',
            'toms': 'toms'
        }
        
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
            
    except subprocess.CalledProcessError as e:
        print(f"Error running drumsep: {e}")
    except Exception as e:
        print(f"Error processing drum parts: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always change back to original directory
        os.chdir(original_dir)

def separate_other(other_stem_path, output_folder, camelot_key, bpm, base_name):
    """
    Further separates the 'other' stem into instrumental components using synthsep
    """
    other_stem_path = os.path.abspath(other_stem_path)
    output_folder = os.path.abspath(output_folder)
    
    # Get absolute path to the synthsep directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    synthsep_dir = os.path.join(current_dir, 'synthsep')
    synthsep_script = os.path.join(synthsep_dir, 'synthsep')
    
    # Make sure script is executable
    os.chmod(synthsep_script, 0o755)
    
    # Store original directory and change to synthsep directory
    original_dir = os.getcwd()
    os.chdir(synthsep_dir)
    
    try:
        # Create temporary output directory
        other_output = os.path.join(output_folder, 'synth_parts_temp')
        os.makedirs(other_output, exist_ok=True)
        
        # Verify the other stem exists before processing
        if not os.path.exists(other_stem_path):
            print(f"Error: Other stem file not found at {other_stem_path}")
            return
            
        # Run the separation
        subprocess.run([
            'bash',
            synthsep_script,
            other_stem_path,
            other_output
        ], check=True)
        
        # Get the directory where the original other stem is located
        target_folder = os.path.dirname(other_stem_path)
        
        # Process and rename the separated parts
        # Note: Update these paths based on your synthsep output structure
        for component in ['piano', 'synth']:
            output_name = f"{camelot_key}_{bpm:.2f}BPM_{base_name}-other-{component}.mp3"
            # Update this path based on your synthsep output structure
            component_path = os.path.join(other_output, component + '.mp3')
            if os.path.exists(component_path):
                os.rename(
                    component_path,
                    os.path.join(target_folder, output_name)
                )
        
        # Clean up
        shutil.rmtree(other_output)
        
    except subprocess.CalledProcessError as e:
        print(f"Error running synthsep: {e}")
    except Exception as e:
        print(f"Error processing other parts: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always change back to original directory
        os.chdir(original_dir)

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
                input_path = wav_path  # Use the converted wav file
            
            # Step 1: Analyze original song ONCE
            camelot_key, bpm = detect_bpm_and_key(input_path)
            base_name = filename.split('.')[0]
            print(f"Separating stems for {filename}...")
            
            try:
                # Step 2: Initial stem separation
                subprocess.run(
                    ['demucs', input_path, '-o', output_folder, '--mp3'],
                    check=True
                )
                
                stem_folder = os.path.join(output_folder, 'htdemucs', base_name)
                if not os.path.exists(stem_folder):
                    print(f"Error: Stem folder not created for {filename}")
                    continue
                
                # Debugging: List files in the stem folder
                print(f"Files in stem folder: {os.listdir(stem_folder)}")
                
                # Step 3: Rename all stems with consistent naming
                drum_stem_path = None
                other_stem_path = None
                for stem_file in os.listdir(stem_folder):
                    stem_name = stem_file.split('.')[0]
                    new_name = f"{camelot_key}_{bpm:.2f}BPM_{base_name}-{stem_name}.mp3"
                    full_stem_path = os.path.join(stem_folder, stem_file)
                    new_stem_path = os.path.join(stem_folder, new_name)
                    os.rename(full_stem_path, new_stem_path)
                    
                    # Store paths for further processing
                    if "drums" in stem_name.lower():
                        drum_stem_path = new_stem_path
                    elif "other" in stem_name.lower():
                        other_stem_path = new_stem_path

                # Step 4: Process drums separately if found
                if drum_stem_path:
                    separate_drums(drum_stem_path, stem_folder, camelot_key, bpm, base_name)
                
                # Step 5: Process other stem if found
                # if other_stem_path:
                    # separate_other(other_stem_path, stem_folder, camelot_key, bpm, base_name)

                # Clean up temporary wav file if we converted from m4a
                if filename.endswith('.m4a') and os.path.exists(wav_path):
                    os.remove(wav_path)

            except subprocess.CalledProcessError as e:
                print(f"Error processing {filename}: {e}")
            except Exception as e:
                print(f"Unexpected error processing {filename}: {e}")
                import traceback
                traceback.print_exc()
            print(f"Successfully processed {filename}")

def gui_process_file():
    # Create the main window
    root = tk.Tk()
    root.title("Audio Analysis")
    
    # Create and configure main frame
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # File selection variables and widgets
    file_path = tk.StringVar()
    detected_bpm = tk.StringVar(value="---")
    detected_key = tk.StringVar(value="---")
    bpm_override = tk.StringVar()
    key_override = tk.StringVar()
    
    def browse_file():
        filename = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.flac")]
        )
        if filename:
            file_path.set(filename)
            # Analyze the selected file
            key, bpm = detect_bpm_and_key(filename)
            detected_bpm.set(f"{bpm}")
            detected_key.set(key)
    
    def start_processing():
        input_file = file_path.get()
        if not input_file:
            status_label.config(text="Please select a file first")
            return
            
        # Use override values if provided
        final_bpm = bpm_override.get() if bpm_override.get() else detected_bpm.get()
        final_key = key_override.get() if key_override.get() else detected_key.get()
        
        # Process with the final values
        input_folder = os.path.dirname(input_file)
        output_folder = os.path.join(input_folder, "output")
        separate_stems(input_folder, output_folder)
        status_label.config(text="Processing complete!")
        root.destroy()  # Close the window after processing
    
    # Create widgets
    ttk.Button(frame, text="Select File", command=browse_file).grid(row=0, column=0, columnspan=2, pady=5)
    
    ttk.Label(frame, text="Detected BPM:").grid(row=1, column=0, sticky=tk.W, pady=2)
    ttk.Label(frame, textvariable=detected_bpm).grid(row=1, column=1, sticky=tk.W, pady=2)
    
    ttk.Label(frame, text="Override BPM:").grid(row=2, column=0, sticky=tk.W, pady=2)
    ttk.Entry(frame, textvariable=bpm_override).grid(row=2, column=1, sticky=tk.W, pady=2)
    
    ttk.Label(frame, text="Detected Key:").grid(row=3, column=0, sticky=tk.W, pady=2)
    ttk.Label(frame, textvariable=detected_key).grid(row=3, column=1, sticky=tk.W, pady=2)
    
    ttk.Label(frame, text="Override Key:").grid(row=4, column=0, sticky=tk.W, pady=2)
    ttk.Entry(frame, textvariable=key_override).grid(row=4, column=1, sticky=tk.W, pady=2)
    
    ttk.Button(frame, text="Process", command=start_processing).grid(row=5, column=0, columnspan=2, pady=10)
    
    status_label = ttk.Label(frame, text="")
    status_label.grid(row=6, column=0, columnspan=2)
    
    root.mainloop()

if __name__ == "__main__":
    gui_process_file()  # Replace the direct separate_stems() call with the GUI