import tkinter as tk
from tkinter import filedialog

def select_audio_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    file_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=[
            ("Audio Files", "*.wav *.mp3 *.ogg *.flac *.m4a *.aac"),
            ("All Files", "*.*")
        ]
    )
    
    return file_path if file_path else None
