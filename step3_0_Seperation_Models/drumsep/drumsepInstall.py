import os
import subprocess
import gdown

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
            
        print("Drumsep model installation complete!")
        return True
        
    except Exception as e:
        print(f"Error installing drumsep model: {e}")
        return False

if __name__ == "__main__":
    install_drumsep() 