import os
import subprocess
from pathlib import Path
import shutil
import re
from concurrent.futures import ThreadPoolExecutor
import torch
import soundfile as sf
import resampy

def separate_stems(input_file, output_folder, progress_callback=None, prefix='', device='cpu', stems=None):
    """
    Separates audio into stems using Demucs v4
    """
    try:
        # Ensure paths are strings and absolute
        input_file = str(Path(input_file).absolute())
        output_folder = str(Path(output_folder).absolute())
        
        print("\nSeparating stems...")
        print(f"Input: {input_file}")
        print(f"Output folder: {output_folder}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Build demucs command
        demucs_cmd = [
            'demucs',
            '-n', 'htdemucs',
            '--out', output_folder,
            '--device', device
        ]
        
        # Add stems parameter if specified
        if stems:
            demucs_cmd.extend(['--stems', '+'.join(stems)])
        
        # Add input file
        demucs_cmd.append(input_file)
        
        print(f"Running command: {' '.join(demucs_cmd)}")
        
        process = subprocess.Popen(
            demucs_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Monitor the output
        while True:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
                
            # Parse progress from demucs output
            if "%" in line:
                try:
                    progress = float(line.split("%")[0].strip())
                    if progress_callback:
                        progress_callback(progress, f"Separating stems: {progress:.1f}%")
                except ValueError:
                    pass
        
        # Get the base name without any existing prefix
        input_filename = Path(input_file).stem
        base_name = input_filename
        
        # The stems will be in a subdirectory named after the model and input file
        temp_stem_folder = os.path.join(output_folder, 'htdemucs', Path(input_file).stem)
        
        # Move and rename stems to the main output folder
        stem_paths = {}
        if os.path.exists(temp_stem_folder):
            for stem_file in os.listdir(temp_stem_folder):
                if stem_file.endswith('.wav'):
                    stem_type = stem_file.split('.')[0]  # drums, bass, vocals, other
                    old_path = os.path.join(temp_stem_folder, stem_file)
                    
                    # Use the provided prefix for the new filename
                    new_name = f"{prefix}{base_name}_{stem_type}.wav"
                    new_path = os.path.join(output_folder, new_name)
                    shutil.move(old_path, new_path)
                    stem_paths[stem_type.upper()] = new_path
                    print(f"Created {stem_type} stem at {new_path}")
            
            # Clean up the temporary folder structure
            shutil.rmtree(os.path.dirname(temp_stem_folder))
        
        if stem_paths:
            print("\nStem separation completed successfully!")
            return stem_paths
        else:
            print("\nNo stems were generated!")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"\nError during stem separation: {e}")
        return None
    except Exception as e:
        print(f"\nUnexpected error during stem separation: {e}")
        import traceback
        traceback.print_exc()
        return None

def separate_stems_multi_gpu(input_files, output_folder, num_gpus=2):
    """
    Process multiple files in parallel using multiple GPUs
    """
    def process_on_gpu(file_data):
        file_path, gpu_id = file_data
        torch.cuda.set_device(gpu_id)
        return separate_stems(file_path, output_folder, device=f'cuda:{gpu_id}')

    # Distribute files across GPUs
    file_gpu_pairs = [(f, i % num_gpus) for i, f in enumerate(input_files)]
    
    with ThreadPoolExecutor(max_workers=num_gpus) as executor:
        results = list(executor.map(process_on_gpu, file_gpu_pairs))
    
    return results

def optimize_audio_for_separation(input_file):
    """
    Optimize audio file before separation
    """
    # Load audio
    y, sr = sf.read(input_file)
    
    # Resample to 44.1kHz if different
    if sr != 44100:
        y = resampy.resample(y, sr, 44100)
        sr = 44100
    
    # Convert to mono if stereo (optional, depends on your needs)
    if len(y.shape) > 1:
        y = y.mean(axis=1)
    
    # Save optimized file
    optimized_path = input_file.replace('.wav', '_optimized.wav')
    sf.write(optimized_path, y, sr)
    return optimized_path

def verify_gpu_setup():
    """
    Verify GPU setup and print diagnostics
    """
    print("\nChecking GPU setup...")
    if torch.cuda.is_available():
        print(f"GPU available: {torch.cuda.get_device_name(0)}")
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Memory allocated: {torch.cuda.memory_allocated(0) / 1e9:.2f} GB")
        print(f"Memory cached: {torch.cuda.memory_reserved(0) / 1e9:.2f} GB")
        return True
    else:
        print("No GPU available, using CPU")
        return False

def process_audio_optimized(input_file, output_folder):
    """
    Optimized audio processing pipeline with parallel drum processing
    """
    try:
        print("\nStarting optimized audio processing...")
        gpu_available = verify_gpu_setup()
        device = 'cuda' if gpu_available else 'cpu'
        print(f"Using device: {device}")
        
        # 1. Optimize input file once
        print("Optimizing input file...")
        optimized_file = optimize_audio_for_separation(input_file)
        print(f"Optimized file created: {optimized_file}")
        
        # 2. Start parallel processing
        print("\nStarting parallel stem separation...")
        with ThreadPoolExecutor(max_workers=2) as executor:
            print("Submitting drum separation task...")
            drum_future = executor.submit(
                separate_stems,
                optimized_file,
                output_folder,
                device=device,
                stems=['drums']
            )
            
            print("Submitting other stems separation task...")
            other_stems_future = executor.submit(
                separate_stems,
                optimized_file,
                output_folder,
                device=device,
                stems=['bass', 'vocals', 'other']
            )
            
            print("Waiting for results...")
            drum_paths = drum_future.result()
            other_paths = other_stems_future.result()
            
            print(f"Drum paths: {drum_paths}")
            print(f"Other paths: {other_paths}")
        
        # Combine results
        all_paths = {**drum_paths, **other_paths}
        
        # Clean up
        os.remove(optimized_file)
        return all_paths
        
    except Exception as e:
        print(f"Error during optimized processing: {e}")
        return None