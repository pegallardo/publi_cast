from tkinter import filedialog
import tkinter as tk

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
                ("WAV files", "*.wav"),
                ("MP3 files", "*.mp3"),
                ("All files", "*.*")
            ],
            title="Save Audio File"
        )
        
        if file_path:
            self.logger.info(f"Selected export path: {file_path}")
            export_command = f'Export2: Filename="{file_path}"'
            self.audacity_api.run_command(export_command)
            return file_path
            
        self.logger.info("Export cancelled by user")
        return None
