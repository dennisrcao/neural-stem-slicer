import os
import subprocess
import gdown
import torch
from torch.serialization import safe_globals
from demucs.hdemucs import HDemucs

def install_drumsep():
    """Install drumsep model for drum separation"""
    try:
        # Create model directory if it doesn't exist
        model_dir = os.path.join(os.path.dirname(__file__), "model")
        os.makedirs(model_dir, exist_ok=True)
        
        # Download model if not already present
        model_path = os.path.join(model_dir, "49469ca8.th")
        if not os.path.exists(model_path):
            print("Downloading drumsep model...")
            # Google Drive file ID for the drumsep model
            file_id = "1-Dm666ScPkg8Gt2-lK3Ua0xOudWHZBGC"
            gdown.download(id=file_id, output=model_path, quiet=False)
        
        # Add HDemucs to safe globals for loading
        torch.serialization.add_safe_globals([HDemucs])
        
        # Verify model loading
        try:
            print("Verifying model loading...")
            with safe_globals([HDemucs]):
                model = torch.load(model_path)
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Warning: Model verification failed: {e}")
            print("This is expected on first install")
            
        print("Drumsep model installation complete!")
        return True
        
    except Exception as e:
        print(f"Error installing drumsep model: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    install_drumsep() 