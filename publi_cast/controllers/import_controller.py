from tkinter import filedialog
import tkinter as tk
import os
import shlex
import subprocess

class ImportController:
    def __init__(self, logger):
        self.logger = logger

    def select_audio_file(self):
        """Opens a file dialog to select an audio file and returns the path."""
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

            # Normalize path for Windows (use backslashes and handle spaces correctly)
            normalized_path = os.path.normpath(file_path)
            
            # For Windows, we don't need to quote the path when passing it to Python functions
            # Just return the normalized path as is
            self.logger.info(f"Selected audio file: {normalized_path}")
            return normalized_path

        except Exception as e:
            self.logger.error(f"Error during file selection: {e}")
            raise
        finally:
            root.destroy()

    def get_short_path_name(self, long_path):
        """
        Gets the short path name (8.3 format) for a given long path.
        This can help with paths containing spaces on Windows.
        """
        try:
            import win32api
            return win32api.GetShortPathName(long_path)
        except ImportError:
            self.logger.warning("win32api not available, cannot get short path name")
            return long_path
        except Exception as e:
            self.logger.error(f"Error getting short path name: {e}")
            return long_path