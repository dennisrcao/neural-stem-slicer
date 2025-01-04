import os
from tkinter import filedialog
import tkinter as tk

try:
    from src.deeprhythm.model.infer import predict_global_bpm
except ImportError as e:
    print("Error: DeepRhythm dependencies not properly installed")
    print(f"Details: {e}")
    exit(1)

def main():
    print("\n" + "="*40)
    print("     Starting BPM Analysis")
    print("="*40 + "\n")
    
    # Create a root window but keep it hidden
    root = tk.Tk()
    root.withdraw()
    
    # Open file dialog
    file_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.flac")]
    )
    
    if file_path:
        print(f"Analyzing file: {file_path}")
        bpm, analysis_time = predict_global_bpm(file_path)
        print(f"Detected BPM: {bpm:.2f}")
        print(f"Analysis time: {analysis_time:.3f}s")
        
        # Get directory and filename
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        
        # Create new filename with BPM
        new_filename = f"{bpm:.2f}BPM_{name}{ext}"
        new_path = os.path.join(directory, new_filename)
        
        # Rename the file
        try:
            os.rename(file_path, new_path)
            print(f"\nFile renamed to: {new_filename}")
        except OSError as e:
            print(f"Error renaming file: {e}")
    else:
        print("No file selected")

if __name__ == "__main__":
    main()