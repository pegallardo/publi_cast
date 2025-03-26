import tkinter as tk
from tkinter import filedialog
import os

class ExportController:
    def __init__(self, audacity_api, logger):
        self.audacity_api = audacity_api
        self.logger = logger
  
    def handle_export(self):
       
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[
                ("MP3 files", "*.mp3"),
                ("WAV files", "*.wav"),
                ("All files", "*.*")
            ],
            title="Save Audio File"
        )
        
        if not file_path:
            self.logger.info("Export cancelled by user")
            return None
        
        self.logger.info(f"Selected export path: {file_path}")
        
        # Get file extension
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()
        
        return file_path, extension
