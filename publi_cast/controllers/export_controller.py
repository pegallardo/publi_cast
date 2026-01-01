import tkinter as tk
from tkinter import filedialog
import os

class ExportController:
    def __init__(self, audacity_api, logger):
        self.audacity_api = audacity_api
        self.logger = logger

    def handle_export(self, input_file_path=None):
        """
        Handle export dialog with optional default filename based on input file.

        Args:
            input_file_path: Path to the input file to use as default name
        """
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        # Build default filename from input file
        initial_file = ""
        initial_dir = ""
        if input_file_path:
            input_dir = os.path.dirname(input_file_path)
            input_name = os.path.splitext(os.path.basename(input_file_path))[0]
            initial_file = input_name
            initial_dir = input_dir

        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            initialfile=initial_file,
            initialdir=initial_dir,
            filetypes=[
                ("MP3 files", "*.mp3"),
                ("WAV files", "*.wav"),
                ("All files", "*.*")
            ],
            title="Save Audio File"
        )

        if not file_path:
            self.logger.info("Export cancelled by user")
            return None, None

        self.logger.info(f"Selected export path: {file_path}")

        # Get file extension
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()

        return file_path, extension
