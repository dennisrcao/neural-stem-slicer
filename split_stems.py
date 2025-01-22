from step3_1_StemSeperation import separate_stems
import tqdm
import os
import tkinter as tk
from tkinter import ttk
from step1_BPMAnalysis import load_and_analyze_bpm
from deeprhythm import DeepRhythmPredictor
import librosa
from step2_KeyAnalysis import detect_key, detect_key_and_rename

class AudioAnalysisGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Audio Analysis")
        
        # Initialize variables
        self.files_to_process = []
        self.current_file_index = 0
        self.deeprhythm_bpm = tk.StringVar()
        self.deeprhythm_confidence = tk.StringVar()
        self.librosa_bpm = tk.StringVar()
        self.manual_bpm = tk.StringVar()
        
        # Key Analysis variables
        self.camelot_key = tk.StringVar()
        self.actual_key = tk.StringVar()
        self.key_confidence = tk.StringVar()
        
        # Find audio files in current directory
        self.scan_directory()
        self.setup_gui()

    def scan_directory(self):
        current_dir = os.getcwd()
        self.files_to_process = [f for f in os.listdir(current_dir) 
                               if f.lower().endswith(('.mp3', '.wav', '.m4a', '.flac'))]
        if self.files_to_process:
            self.analyze_file(self.files_to_process[0])

    def setup_gui(self):
        # Current file frame
        file_frame = ttk.LabelFrame(self.root, text="Current File", padding="10")
        file_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        if self.files_to_process:
            ttk.Label(file_frame, text=self.files_to_process[0]).grid(row=0, column=0)
        else:
            ttk.Label(file_frame, text="No audio files found").grid(row=0, column=0)
        
        # BPM Analysis frame
        bpm_frame = ttk.LabelFrame(self.root, text="Step 1: BPM Analysis", padding="10")
        bpm_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        ttk.Label(bpm_frame, text="DeepRhythm").grid(row=0, column=0, padx=5)
        ttk.Entry(bpm_frame, textvariable=self.deeprhythm_bpm, width=8).grid(row=1, column=0, padx=5)
        ttk.Entry(bpm_frame, textvariable=self.deeprhythm_confidence, width=8).grid(row=1, column=1, padx=5)
        
        ttk.Label(bpm_frame, text="Librosa").grid(row=0, column=2, padx=5)
        ttk.Entry(bpm_frame, textvariable=self.librosa_bpm, width=8).grid(row=1, column=2, padx=5)
        
        ttk.Label(bpm_frame, text="Manual Override").grid(row=0, column=3, padx=5)
        ttk.Entry(bpm_frame, textvariable=self.manual_bpm, width=8).grid(row=1, column=3, padx=5)
        
        # Key Analysis frame
        key_frame = ttk.LabelFrame(self.root, text="Step 2: Key Analysis", padding="10")
        key_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        
        ttk.Label(key_frame, text="Camelot").grid(row=0, column=0, padx=5)
        ttk.Entry(key_frame, textvariable=self.camelot_key, width=8).grid(row=1, column=0, padx=5)
        
        ttk.Label(key_frame, text="Key").grid(row=0, column=1, padx=5)
        ttk.Entry(key_frame, textvariable=self.actual_key, width=12).grid(row=1, column=1, padx=5)
        
        ttk.Label(key_frame, text="Confidence").grid(row=0, column=2, padx=5)
        ttk.Entry(key_frame, textvariable=self.key_confidence, width=8).grid(row=1, column=2, padx=5)
        
        # Add Process button with new text
        self.process_button = ttk.Button(self.root, text="Split Stems", command=self.process_current_file)
        self.process_button.grid(row=4, column=0, pady=10)
        
        # Add progress bar
        self.progress_frame = ttk.LabelFrame(self.root, text="Progress", padding="10")
        self.progress_frame.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            orient="horizontal", 
            length=300, 
            mode="determinate"
        )
        self.progress_bar.grid(row=0, column=0, padx=5, pady=5)
        
        # Add status label
        self.status_label = ttk.Label(self.progress_frame, text="")
        self.status_label.grid(row=1, column=0, padx=5)
        
        # Add progress label
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.grid(row=2, column=0, padx=5)

    def analyze_file(self, filename):
        try:
            file_path = os.path.join(os.getcwd(), filename)
            
            # BPM Analysis
            y, sr = librosa.load(file_path)
            predictor = DeepRhythmPredictor()
            bpm, confidence = predictor.predict_from_audio(y, sr, include_confidence=True)
            self.deeprhythm_bpm.set(f"{bpm:.2f}")
            self.deeprhythm_confidence.set(f"{confidence:.2%}")
            
            # Librosa BPM
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=sr)[0]
            self.librosa_bpm.set(f"{tempo:.2f}")
            
            # Key Analysis
            key_results = detect_key(file_path)
            camelot, full_key, key_conf = key_results[0]
            self.camelot_key.set(camelot)
            self.actual_key.set(full_key)
            self.key_confidence.set(f"{key_conf:.2f}%")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

    def process_current_file(self):
        if not self.files_to_process:
            self.status_label.config(text="No files to process")
            return
        
        def update_progress(progress, status_text):
            self.progress_bar['value'] = progress
            self.progress_label.config(text=status_text)
            self.root.update()
        
        try:
            current_file = self.files_to_process[self.current_file_index]
            file_path = os.path.join(os.getcwd(), current_file)
            
            # Use manual BPM if provided
            bpm = float(self.manual_bpm.get()) if self.manual_bpm.get() else float(self.deeprhythm_bpm.get())
            
            # Process file with key and BPM
            output_file = detect_key_and_rename(file_path, bpm)
            
            # Update status
            self.status_label.config(text="Separating stems (this will take 3-5 minutes)...")
            self.root.update()  # Force GUI update
            
            # Perform stem separation with progress callback
            output_folder = os.path.join(os.getcwd(), 'output', 'stems')
            stem_paths = separate_stems(output_file, output_folder, progress_callback=update_progress)
            
            if stem_paths:
                # Rename stems with original key and BPM
                base_name = os.path.splitext(os.path.basename(output_file))[0]
                drum_stem_path = None
                
                # First pass: find and store drum stem path
                for stem_type, path in stem_paths.items():
                    if stem_type.lower() == 'drums':
                        drum_stem_path = path
                    new_name = f"{base_name}_{stem_type.lower()}.mp3"
                    new_path = os.path.join(output_folder, new_name)
                    os.rename(path, new_path)
                    
                    # Update drum_stem_path to new location if it's the drum stem
                    if path == drum_stem_path:
                        drum_stem_path = new_path
                
                # If we found drums, separate them further
                if drum_stem_path:
                    self.status_label.config(text="Separating drum components (this may take a few minutes)...")
                    self.root.update()
                    
                    from step3_2_DrumSeperation import separate_drums
                    camelot_key = self.camelot_key.get()
                    bpm = float(self.manual_bpm.get()) if self.manual_bpm.get() else float(self.deeprhythm_bpm.get())
                    
                    success = separate_drums(drum_stem_path, output_folder, camelot_key, bpm, base_name)
                    if success:
                        self.status_label.config(text=f"Processed {current_file} and separated all stems including drums")
                    else:
                        self.status_label.config(text=f"Processed {current_file}, but drum separation failed")
                    self.root.update()
                else:
                    self.status_label.config(text=f"Processed {current_file} and separated stems")
                
            else:
                self.status_label.config(text="Stem separation failed")
                
            # Move to next file if available
            self.current_file_index += 1
            if self.current_file_index < len(self.files_to_process):
                self.analyze_file(self.files_to_process[self.current_file_index])
            else:
                self.status_label.config(text="All files processed!")
                
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = AudioAnalysisGUI()
    gui.run()