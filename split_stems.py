from step3_1_StemSeperation import separate_stems
import tqdm
import os
import tkinter as tk
from tkinter import ttk
from step1_BPMAnalysis import load_and_analyze_bpm
from deeprhythm import DeepRhythmPredictor
import librosa
from step2_KeyAnalysis import detect_key, detect_key_and_rename
import soundfile as sf
import shutil
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime

class AudioAnalysisGUI:
    def __init__(self):
        self.start_time = time.time()  # Add start time tracking
        self.root = tk.Tk()
        self.root.title("Audio Analysis")
        
        # Initialize variables
        self.files_to_process = []
        self.current_file_index = 0
        self.deeprhythm_bpm = tk.StringVar()
        self.deeprhythm_confidence = tk.StringVar()
        self.manual_bpm = tk.StringVar()
        
        # Key Analysis variables
        self.camelot_key = tk.StringVar()
        self.actual_key = tk.StringVar()
        self.key_confidence = tk.StringVar()
        self.combined_key = tk.StringVar()
        self.manual_key = tk.StringVar()
        
        self.temp_wav_path = None  # Add this to track temporary WAV files
        
        # Add checkbox variables
        self.module1_enabled = tk.BooleanVar(value=True)
        self.module2_enabled = tk.BooleanVar(value=True)
        self.module3_enabled = tk.BooleanVar(value=True)
        
        # Add progress tracking variable
        self.current_progress = 0
        
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
            ttk.Label(file_frame, text=self.files_to_process[0]).grid(row=0, column=0, sticky="w")
        else:
            ttk.Label(file_frame, text="No audio files found").grid(row=0, column=0, sticky="w")
        
        # Set consistent column widths
        column_widths = [15, 8, 15]  # Width for each column
        
        # Module 1: Analysis Frame
        module1_frame = ttk.LabelFrame(self.root, padding="10")
        module1_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # Checkbox and label in a separate frame
        module1_header = ttk.Frame(module1_frame)
        module1_header.grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Checkbutton(module1_header, variable=self.module1_enabled).grid(row=0, column=0, padx=(0,5))
        ttk.Label(module1_header, text="Module 1: BPM and Key Analysis").grid(row=0, column=1, sticky="w")
        
        # BPM Analysis section
        ttk.Label(module1_frame, text="DeepRhythm").grid(row=1, column=0, padx=5)
        ttk.Label(module1_frame, text="Confidence").grid(row=1, column=1, padx=5)
        ttk.Label(module1_frame, text="Manual Override").grid(row=1, column=2, padx=5)
        
        ttk.Entry(module1_frame, textvariable=self.deeprhythm_bpm, width=column_widths[0]).grid(row=2, column=0, padx=5)
        ttk.Entry(module1_frame, textvariable=self.deeprhythm_confidence, width=column_widths[1]).grid(row=2, column=1, padx=5)
        ttk.Entry(module1_frame, textvariable=self.manual_bpm, width=column_widths[2]).grid(row=2, column=2, padx=5)
        
        # Separator between BPM and Key
        ttk.Separator(module1_frame, orient='horizontal').grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)
        
        # Key Analysis section
        ttk.Label(module1_frame, text="Camelot/Key").grid(row=4, column=0, padx=5)
        ttk.Label(module1_frame, text="Confidence").grid(row=4, column=1, padx=5)
        ttk.Label(module1_frame, text="Manual Override").grid(row=4, column=2, padx=5)
        
        ttk.Entry(module1_frame, textvariable=self.combined_key, width=column_widths[0]).grid(row=5, column=0, padx=5)
        ttk.Entry(module1_frame, textvariable=self.key_confidence, width=column_widths[1]).grid(row=5, column=1, padx=5)
        ttk.Entry(module1_frame, textvariable=self.manual_key, width=column_widths[2]).grid(row=5, column=2, padx=5)
        
        # Module 2: Stem Separation Frame - reduce height
        module2_frame = ttk.LabelFrame(self.root, padding="5")  # reduced padding
        module2_frame.grid(row=2, column=0, padx=10, pady=2, sticky="nsew")  # reduced pady
        
        # Module 2 header with checkbox
        module2_header = ttk.Frame(module2_frame)
        module2_header.grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(module2_header, variable=self.module2_enabled).grid(row=0, column=0, padx=(0,5))
        ttk.Label(module2_header, text="Module 2: Stem Separation").grid(row=0, column=1, sticky="w")
        
        # Progress section - reduced vertical spacing
        progress_frame = ttk.Frame(module2_frame)
        progress_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")  # reduced pady
        
        # Configure progress frame to expand
        module2_frame.columnconfigure(0, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="determinate"
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=5)
        
        # Status labels
        self.status_label = ttk.Label(progress_frame, text="")
        self.status_label.grid(row=1, column=0, padx=5)
        
        self.progress_label = ttk.Label(progress_frame, text="")
        self.progress_label.grid(row=2, column=0, padx=5)
        
        # Module 3: Chop Segments Frame
        module3_frame = ttk.LabelFrame(self.root, padding="5")
        module3_frame.grid(row=3, column=0, padx=10, pady=2, sticky="nsew")
        
        # Module 3 header with checkbox
        module3_header = ttk.Frame(module3_frame)
        module3_header.grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(module3_header, variable=self.module3_enabled).grid(row=0, column=0, padx=(0,5))
        ttk.Label(module3_header, text="Module 3: Chop Segments 8 Bars").grid(row=0, column=1, sticky="w")
        
        # Process button - move to row 4 (after Module 3)
        self.process_button = ttk.Button(self.root, text="Process", command=self.process_current_file)
        self.process_button.grid(row=4, column=0, pady=10, sticky="s")
        
        # Configure root window to expand properly
        self.root.columnconfigure(0, weight=1)

    def analyze_file(self, filename):
        try:
            file_path = os.path.join(os.getcwd(), filename)
            
            # BPM Analysis - only DeepRhythm
            y, sr = librosa.load(file_path)
            predictor = DeepRhythmPredictor()
            bpm, confidence = predictor.predict_from_audio(y, sr, include_confidence=True)
            self.deeprhythm_bpm.set(f"{bpm:.2f}")
            self.deeprhythm_confidence.set(f"{confidence:.2%}")
            
            # Key Analysis
            key_results = detect_key(file_path)
            camelot, full_key, key_conf = key_results[0]
            
            # Set combined Camelot/Key format
            self.combined_key.set(f"{camelot}/{full_key}")
            self.key_confidence.set(f"{key_conf:.2f}%")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

    def process_current_file(self):
        try:
            # Start timing when process button is clicked
            start_time = time.time()
            
            current_file = self.files_to_process[self.current_file_index]
            file_path = os.path.join(os.getcwd(), current_file)
            
            # Get BPM and key info
            bpm = float(self.manual_bpm.get()) if self.manual_bpm.get() else float(self.deeprhythm_bpm.get())
            camelot_key = self.manual_key.get() if self.manual_key.get() else self.combined_key.get().split('/')[0]
            
            # Create the key/BPM prefix
            prefix = f"{camelot_key}_{bpm:.2f}BPM_"
            
            # Only perform stem separation if Module 2 is enabled
            if self.module2_enabled.get():
                self.status_label.config(text="Starting stem separation...")
                self.root.update()
                
                output_folder = os.path.join(os.getcwd(), 'output', 'stems')
                os.makedirs(output_folder, exist_ok=True)
                
                stem_paths = separate_stems(file_path, output_folder, 
                                         progress_callback=self.update_progress,
                                         prefix=prefix)
                
                if stem_paths and 'DRUMS' in stem_paths:
                    self.status_label.config(text="Separating drum components...")
                    self.root.update()
                    
                    base_name = f"{camelot_key}_{bpm:.2f}BPM_{os.path.splitext(current_file)[0]}"
                    
                    from step3_2_DrumSeperation import separate_drums
                    success = separate_drums(stem_paths['DRUMS'], output_folder, camelot_key, bpm, base_name)
                    
                    if not success:
                        self.status_label.config(text="Drum separation failed")
                        return
                
                # Only perform segment chopping if Module 3 is enabled
                if self.module3_enabled.get():
                    self.status_label.config(text="Chopping stems into 8-bar segments...")
                    self.root.update()
                    
                    from step4_ChopSegments8Bars import process_stems_to_segments
                    if process_stems_to_segments(output_folder, self.update_progress):
                        self.status_label.config(text="Successfully created 8-bar segments!")
                    else:
                        self.status_label.config(text="Failed to create segments")
                        return
                
                # After all processing is complete (just before the "Move to next file" section)
                self.status_label.config(text=f"Completed processing {current_file}")
            
            # Calculate and display elapsed time
            end_time = time.time()
            elapsed_time = end_time - start_time
            timing_msg = f"\nTotal Processing Time: {elapsed_time:.2f} seconds"
            print("\n" + "=" * 30)
            print(timing_msg)
            print("=" * 30)
            
            self.status_label.config(text=f"Complete! Took {elapsed_time:.2f} seconds")
            
            # Move to next file if available
            self.current_file_index += 1
            if self.current_file_index < len(self.files_to_process):
                self.analyze_file(self.files_to_process[self.current_file_index])
            else:
                self.status_label.config(text="All files processed!")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

    def update_progress(self, progress, status_message=None):
        """
        Update the progress bar and progress label
        progress: float or string representing progress
        status_message: optional status message to display
        """
        try:
            # Convert progress to percentage (0-100)
            if isinstance(progress, str):
                try:
                    # Try to extract number from string like "45.5%"
                    percentage = float(progress.strip('%'))
                except ValueError:
                    percentage = 0
            else:
                percentage = float(progress)
            
            # Ensure percentage is between 0 and 100
            percentage = max(0, min(100, percentage))
            
            # Update progress bar
            self.progress_bar['value'] = percentage
            
            # Update progress label
            self.progress_label.config(text=f"{percentage:.1f}%")
            
            # Update status message if provided
            if status_message:
                self.status_label.config(text=status_message)
            
            # Force GUI update
            self.root.update()
            
        except Exception as e:
            print(f"Error updating progress: {str(e)}")
            # Don't let progress errors stop the process
            pass

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    print("\n" + "=" * 30)
    print(f"Starting processing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 30 + "\n")
    
    gui = AudioAnalysisGUI()
    gui.run()