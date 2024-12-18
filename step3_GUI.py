import tkinter as tk
from tkinter import ttk, filedialog
import os
from step1_BPMAnalysis import load_and_analyze_bpm
from step2_KeyAnalysis import detect_key
from step4_StemSeperation import separate_stems

class AudioProcessingGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Audio Analysis")
        self.setup_gui()
        print("GUI initialized and ready")

    def setup_gui(self):
        # Create main frame
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize variables
        self.file_path = tk.StringVar()
        self.detected_bpm = tk.StringVar(value="---")
        self.detected_key = tk.StringVar(value="---")
        self.bpm_override = tk.StringVar()
        self.key_override = tk.StringVar()
        
        # Create widgets
        ttk.Button(frame, text="Select File", command=self.browse_file).grid(row=0, column=0, columnspan=2, pady=5)
        
        ttk.Label(frame, text="Detected BPM:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(frame, textvariable=self.detected_bpm).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(frame, text="Override BPM:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame, textvariable=self.bpm_override).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Create key detection results frame
        key_frame = ttk.LabelFrame(frame, text="Detected Keys", padding="5")
        key_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.key_labels = []
        for i in range(2):
            var = tk.StringVar(value="---")
            label = ttk.Label(key_frame, textvariable=var)
            label.grid(row=i, column=0, sticky=tk.W)
            self.key_labels.append(var)
        
        ttk.Label(frame, text="Override Key:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame, textvariable=self.key_override).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        ttk.Button(frame, text="Process", command=self.start_processing).grid(row=5, column=0, columnspan=2, pady=10)
        
        self.status_label = ttk.Label(frame, text="")
        self.status_label.grid(row=6, column=0, columnspan=2)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.flac")]
        )
        if filename:
            print(f"\nAnalyzing file: {filename}")
            self.file_path.set(filename)
            
            # Get key estimates (now returns top 2)
            key_results = detect_key(filename)
            
            # Update GUI with top 2 keys
            for i, (camelot, full_key, confidence) in enumerate(key_results):
                self.key_labels[i].set(f"{camelot} - {full_key} ({confidence:.1%})")
            
            # Use the highest confidence key as the default
            self.detected_key.set(f"{key_results[0][0]} - {key_results[0][1]}")
            
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