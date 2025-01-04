import tkinter as tk
from tkinter import ttk, filedialog
import os
from step1_BPMAnalysis import load_and_analyze_bpm
from step2_KeyAnalysis import detect_key
from step4_StemSeperation import separate_stems

try:
    from src.deeprhythm.model.infer import predict_global_bpm
except ImportError as e:
    print("Error: DeepRhythm dependencies not properly installed")
    print(f"Details: {e}")
    from step1_BPMAnalysis import load_and_analyze_bpm  # Fallback to librosa

class AudioProcessingGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Audio Analysis")
        
        # Initialize variables
        self.file_path = tk.StringVar()
        self.key_labels = [tk.StringVar() for _ in range(2)]  # Array for multiple key estimates
        self.detected_key = tk.StringVar()
        self.key_override = tk.StringVar()
        self.detected_bpm = tk.StringVar()
        self.bpm_override = tk.StringVar()
        
        self.setup_gui()
        print("GUI initialized and ready")

    def setup_gui(self):
        # File Selection
        ttk.Label(self.root, text="Selected File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.root, textvariable=self.file_path).grid(row=0, column=1, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Button(self.root, text="Browse", command=self.browse_file).grid(row=0, column=3, padx=5, pady=5)

        # Key Detection Results
        ttk.Label(self.root, text="Detected Keys:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        for i in range(2):
            ttk.Label(self.root, textvariable=self.key_labels[i]).grid(row=1+i, column=1, columnspan=2, sticky="w", padx=5)

        # Key Override
        ttk.Label(self.root, text="Override Key:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.root, textvariable=self.key_override).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # BPM Detection
        ttk.Label(self.root, text="Detected BPM:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.root, textvariable=self.detected_bpm).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # BPM Override
        ttk.Label(self.root, text="Override BPM:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.root, textvariable=self.bpm_override).grid(row=5, column=1, sticky="w", padx=5, pady=5)

        # Process Button
        ttk.Button(self.root, text="Process", command=self.start_processing).grid(row=6, column=0, columnspan=4, pady=20)

        # Status Label
        self.status_label = ttk.Label(self.root, text="")
        self.status_label.grid(row=7, column=0, columnspan=4, pady=5)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.flac")]
        )
        if filename:
            print(f"\nAnalyzing file: {filename}")
            self.file_path.set(filename)
            
            # Get key estimates (now returns top 2)
            key_results = detect_key(filename)
            
            # Update GUI with key results
            for i, (camelot, full_key, confidence) in enumerate(key_results):
                if confidence is not None:
                    self.key_labels[i].set(f"{camelot} - {full_key} ({confidence:.1f}%)")
                else:
                    self.key_labels[i].set(f"{camelot} - {full_key}")
            
            # Use the highest confidence key as the default
            self.detected_key.set(f"{key_results[0][0]} - {key_results[0][1]}")
            
            try:
                bpm, _ = predict_global_bpm(filename)
            except Exception as e:
                print(f"DeepRhythm error: {e}, falling back to librosa")
                bpm = load_and_analyze_bpm(filename)
            self.detected_bpm.set(f"{bpm}")
            print("Analysis complete")

    def start_processing(self):
        input_file = self.file_path.get()
        if not input_file:
            self.status_label.config(text="Please select a file first")
            return

        print("\n=== Starting Stem Separation Process ===")
        final_bpm = self.bpm_override.get() if self.bpm_override.get() else self.detected_bpm.get()
        final_key = self.key_override.get() if self.key_override.get() else self.detected_key.get().split(" - ")[0]
        
        input_folder = os.path.dirname(input_file)
        output_folder = os.path.join(input_folder, "output")
        
        print(f"Using BPM: {final_bpm}")
        print(f"Using Key: {final_key}")
        
        separate_stems(input_folder, output_folder)
        self.status_label.config(text="Processing complete!")
        print("=== Processing Complete ===")
        self.root.destroy()

    def run(self):
        self.root.mainloop()