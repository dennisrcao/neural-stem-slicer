import os
import shutil
import sys

def remove_output_contents():
    """Remove all contents from the output directory"""
    try:
        # Get the output directory path relative to the script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, 'output')
        
        # Check if output directory exists
        if not os.path.exists(output_dir):
            print("Output directory doesn't exist. Nothing to clean.")
            return
            
        # List all items in the output directory
        items = os.listdir(output_dir)
        
        if not items:
            print("Output directory is already empty.")
            return
            
        # Remove each item in the directory
        for item in items:
            item_path = os.path.join(output_dir, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"Error removing {item}: {e}")
                
        print("Successfully cleaned output directory!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    remove_output_contents() 