from tkinter import filedialog
import tkinter as tk
import os

def select_audio_file(logger):
    logger.info("Opening audio file selection dialog")
    root = tk.Tk()
    root.withdraw()
    
    try:
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.mp3;*.wav;*.ogg;*.flac;*.m4a"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            # Normalize the path for Windows compatibility
            normalized_path = os.path.normpath(file_path)

            # Wrap in double quotes to handle spaces in Windows paths
            quoted_path = f'"{normalized_path}"'
            logger.info(f"Selected audio file: {quoted_path}")
            
            return quoted_path
        else:
            logger.warning("No file selected")
            return None
    except Exception as e:
        logger.error(f"Error in file selection: {e}")
        raise
    finally:
        root.destroy()
