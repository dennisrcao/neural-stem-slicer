import os
import tkinter as tk
from tkinter import ttk
from step1_BPMAnalysis import load_and_analyze_bpm
from deeprhythm import DeepRhythmPredictor
import librosa

class BPMAnalysisGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Audio Analysis")
        
        # Initialize variables
        self.deeprhythm_bpm = tk.StringVar()
        self.deeprhythm_confidence = tk.StringVar()
        self.librosa_bpm = tk.StringVar()
        self.librosa_confidence = tk.StringVar()
        self.manual_bpm = tk.StringVar()
        self.current_file = tk.StringVar()
        
        self.setup_gui()
        
    def setup_gui(self):
        # Current file at the top with right alignment
        file_frame = ttk.Frame(self.root)
        file_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        file_frame.grid_columnconfigure(1, weight=1)  # Make second column expandable
        
        ttk.Label(file_frame, text="Current File:").grid(row=0, column=0, sticky="w")
        ttk.Label(file_frame, textvariable=self.current_file).grid(row=0, column=1, sticky="e")
        
        # Main frame
        frame = ttk.LabelFrame(self.root, text="Step 1: BPM Analysis", padding="10")
        frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # Analysis section using grid layout
        # Deeprhythm
        ttk.Label(frame, text="Deeprhythm").grid(row=0, column=0, padx=5)
        ttk.Entry(frame, textvariable=self.deeprhythm_bpm, width=8).grid(row=1, column=0, padx=5)
        ttk.Entry(frame, textvariable=self.deeprhythm_confidence, width=8).grid(row=1, column=1, padx=5)
        
        # Librosa
        ttk.Label(frame, text="Librosa").grid(row=0, column=2, padx=5)
        ttk.Entry(frame, textvariable=self.librosa_bpm, width=8).grid(row=1, column=2, padx=5)
        ttk.Entry(frame, textvariable=self.librosa_confidence, width=8).grid(row=1, column=3, padx=5)
        
        # Manual Override
        ttk.Label(frame, text="Manual Override").grid(row=0, column=6, padx=5)
        ttk.Entry(frame, textvariable=self.manual_bpm, width=8).grid(row=1, column=6, padx=5)
        
        # Labels for BPM and %
        ttk.Label(frame, text="BPM").grid(row=2, column=0, padx=5)
        ttk.Label(frame, text="%").grid(row=2, column=1, padx=5)
        ttk.Label(frame, text="BPM").grid(row=2, column=2, padx=5)
        ttk.Label(frame, text="%").grid(row=2, column=3, padx=5)
        ttk.Label(frame, text="BPM").grid(row=2, column=4, padx=5)
        ttk.Label(frame, text="%").grid(row=2, column=5, padx=5)
        ttk.Label(frame, text="BPM").grid(row=2, column=6, padx=5)
        
        # Process Button
        ttk.Button(frame, text="Process", command=self.process_current_file).grid(row=3, column=0, columnspan=7, pady=10)
        
        # Status Label
        self.status_label = ttk.Label(frame, text="")
        self.status_label.grid(row=4, column=0, columnspan=7, pady=5)
        
    def analyze_file(self, file_path):
        try:
            y, sr = librosa.load(file_path)
            
            # DeepRhythm analysis
            predictor = DeepRhythmPredictor()
            bpm, confidence = predictor.predict_from_audio(y, sr, include_confidence=True)
            self.deeprhythm_bpm.set(f"{bpm:.2f}")
            self.deeprhythm_confidence.set(f"{confidence:.2%}")
            
            # Librosa analysis
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=sr)[0]
            self.librosa_bpm.set(f"{tempo:.2f}")
            self.librosa_confidence.set("N/A")
            
            self.current_file.set(os.path.basename(file_path))
            self.status_label.config(text="Analysis complete")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
    
    def process_current_file(self):
        if not self.current_file.get():
            self.status_label.config(text="No file to process")
            return
            
        try:
            current_file = os.path.join(os.getcwd(), self.current_file.get())
            
            # Use manual BPM if provided, otherwise use DeepRhythm result
            if self.manual_bpm.get():
                bpm = float(self.manual_bpm.get())
                load_and_analyze_bpm(current_file, manual_bpm=bpm)
            else:
                bpm = float(self.deeprhythm_bpm.get())
                load_and_analyze_bpm(current_file, manual_bpm=None)
            
            self.status_label.config(text="Processing complete!")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
    
    def process_directory(self):
        current_dir = os.getcwd()
        audio_files = [f for f in os.listdir(current_dir) 
                      if f.lower().endswith(('.mp3', '.wav', '.m4a', '.flac'))]
        
        if not audio_files:
            self.status_label.config(text="No audio files found")
            return
            
        for filename in audio_files:
            file_path = os.path.join(current_dir, filename)
            self.analyze_file(file_path)
            self.root.update()
    
    def run(self):
        self.process_directory()
        self.root.mainloop()

def main():
    gui = BPMAnalysisGUI()
    gui.run()

if __name__ == "__main__":
    main()