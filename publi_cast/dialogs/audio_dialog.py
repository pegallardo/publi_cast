from tkinter import filedialog
import tkinter as tk
import os

def select_audio_file(logger):
    """Open a dialog for the user to select an audio file.

    Args:
        logger: Logger instance to record actions and errors.

    Returns:
        str or None: The normalized and quoted file path if a file is selected; otherwise, None.
    """
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

        if not file_path:
            logger.warning("No file selected")
            return None

        normalized_path = os.path.normpath(file_path)
        quoted_path = f'"{normalized_path}"'
        logger.info(f"Selected audio file: {quoted_path}")
        return quoted_path

    except Exception as e:
        logger.error(f"Error during file selection: {e}")
        raise
    finally:
        root.destroy()