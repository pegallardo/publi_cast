from tkinter import filedialog
import tkinter as tk
import os

class ImportController:
    def __init__(self, logger):
        self.logger = logger

    def select_audio_file(self):
        self.logger.info("Opening audio file selection dialog")
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

            if not file_path:
                self.logger.warning("No file selected")
                return None

            normalized_path = os.path.normpath(file_path)
            quoted_path = f'"{normalized_path}"'
            self.logger.info(f"Selected audio file: {quoted_path}")
            return quoted_path

        except Exception as e:
            self.logger.error(f"Error during file selection: {e}")
            raise
        finally:
            root.destroy()
