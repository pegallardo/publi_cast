# -*- coding: utf-8 -*-
"""
PubliCast - Main GUI Window
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import logging
import queue


class TextHandler(logging.Handler):
    """Custom logging handler that writes to a tkinter Text widget."""

    def __init__(self, text_widget, log_queue):
        super().__init__()
        self.text_widget = text_widget
        self.log_queue = log_queue

    def emit(self, record):
        msg = self.format(record)
        self.log_queue.put(msg)


class MainWindow:
    """Main application window with log display and control buttons."""

    def __init__(self, process_callback, on_exit_callback=None):
        self.process_callback = process_callback
        self.on_exit_callback = on_exit_callback
        self.root = tk.Tk()
        self.root.title("PubliCast - Audio Processor")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # Handle window close button (X)
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)

        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Queue for thread-safe logging
        self.log_queue = queue.Queue()

        # Processing state
        self.is_processing = False

        self._create_widgets()
        self._setup_logging()
        self._poll_log_queue()

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="PubliCast - Audio Processor",
            font=("Segoe UI", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))

        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Logs", padding="5")
        log_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.log_text.config(state=tk.DISABLED)

        # Configure log colors
        self.log_text.tag_config("INFO", foreground="#00ff00")
        self.log_text.tag_config("WARNING", foreground="#ffff00")
        self.log_text.tag_config("ERROR", foreground="#ff0000")
        self.log_text.tag_config("DEBUG", foreground="#888888")

        # Status bar
        self.status_var = tk.StringVar(value="Prêt")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        # Process button
        self.process_btn = ttk.Button(
            button_frame,
            text="🎵 Traiter un fichier audio",
            command=self._on_process_click
        )
        self.process_btn.grid(row=0, column=0, padx=5, sticky="ew")

        # Clear log button
        clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Effacer les logs",
            command=self._clear_logs
        )
        clear_btn.grid(row=0, column=1, padx=5, sticky="ew")

        # Exit button
        exit_btn = ttk.Button(
            button_frame,
            text="❌ Quitter",
            command=self._on_exit
        )
        exit_btn.grid(row=0, column=2, padx=5, sticky="ew")

    def _setup_logging(self):
        """Setup logging to redirect to the text widget."""
        self.text_handler = TextHandler(self.log_text, self.log_queue)
        self.text_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        )

    def get_log_handler(self):
        """Return the text handler for the logger service."""
        return self.text_handler

    def _poll_log_queue(self):
        """Poll the log queue and update the text widget."""
        while not self.log_queue.empty():
            try:
                msg = self.log_queue.get_nowait()
                self._append_log(msg)
            except queue.Empty:
                break
        self.root.after(100, self._poll_log_queue)

    def _append_log(self, msg):
        """Append a message to the log text widget."""
        self.log_text.config(state=tk.NORMAL)

        # Determine tag based on log level
        tag = "INFO"
        if "ERROR" in msg:
            tag = "ERROR"
        elif "WARNING" in msg:
            tag = "WARNING"
        elif "DEBUG" in msg:
            tag = "DEBUG"

        self.log_text.insert(tk.END, msg + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _clear_logs(self):
        """Clear the log text widget."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _on_process_click(self):
        """Handle process button click."""
        if self.is_processing:
            return

        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED)
        self.status_var.set("Traitement en cours...")

        # Run processing in a separate thread
        thread = threading.Thread(target=self._run_process, daemon=True)
        thread.start()

    def _run_process(self):
        """Run the audio processing in a background thread."""
        try:
            self.process_callback()
        except Exception as e:
            self.log_queue.put(f"ERROR - Erreur: {e}")
        finally:
            # Re-enable button on main thread
            self.root.after(0, self._processing_complete)

    def _processing_complete(self):
        """Called when processing is complete."""
        self.is_processing = False
        self.process_btn.config(state=tk.NORMAL)
        self.status_var.set("Traitement terminé - Prêt pour un nouveau fichier")

    def _on_exit(self):
        """Handle exit button click or window close."""
        if self.is_processing:
            if not tk.messagebox.askyesno(
                "Traitement en cours",
                "Un traitement est en cours. Voulez-vous vraiment quitter?"
            ):
                return

        # Call cleanup callback before closing
        if self.on_exit_callback:
            try:
                self.log("Fermeture en cours...", "INFO")
                self.on_exit_callback()
            except Exception as e:
                self.log(f"Erreur lors de la fermeture: {e}", "ERROR")

        self.root.quit()
        self.root.destroy()

    def log(self, message, level="INFO"):
        """Add a log message directly."""
        self.log_queue.put(f"{level} - {message}")

    def run(self):
        """Start the main event loop."""
        self.log("Application démarrée", "INFO")
        self.root.mainloop()
