# -*- coding: utf-8 -*-
"""
PubliCast - Main GUI Window
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import logging
import queue

from publi_cast.gui.settings_panel import SettingsPanel
from publi_cast.gui.localization import t, get_language, set_language


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
        self.root.geometry("1000x650")
        self.root.minsize(900, 500)

        # Handle window close button (X)
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)

        # Configure grid - 2 columns: settings panel + main content
        self.root.columnconfigure(0, weight=0)  # Settings panel (fixed width)
        self.root.columnconfigure(1, weight=1)  # Main content (expandable)
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
        # Settings panel (left side)
        self.settings_panel = SettingsPanel(self.root, on_change_callback=self._on_setting_change)
        self.settings_panel.grid(row=0, column=0, sticky="ns", padx=(10, 5), pady=10)

        # Main frame (right side)
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)

        # Header frame (title + language selector)
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)

        # Title
        self.title_label = ttk.Label(
            header_frame,
            text=t("app_title"),
            font=("Segoe UI", 16, "bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        # Language selector
        lang_frame = ttk.Frame(header_frame)
        lang_frame.grid(row=0, column=1, sticky="e")

        self.lang_label = ttk.Label(lang_frame, text=t("language") + ":")
        self.lang_label.grid(row=0, column=0, padx=(0, 5))

        self.lang_var = tk.StringVar(value=get_language())
        lang_combo = ttk.Combobox(
            lang_frame, textvariable=self.lang_var,
            values=["fr", "en"], width=5, state="readonly"
        )
        lang_combo.grid(row=0, column=1)
        lang_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        # Log area
        self.log_frame = ttk.LabelFrame(self.main_frame, text=t("logs"), padding="5")
        self.log_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
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
        self.status_var = tk.StringVar(value=t("ready"))
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=4, column=0, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        # Process button
        self.process_btn = ttk.Button(
            button_frame,
            text=t("btn_process"),
            command=self._on_process_click
        )
        self.process_btn.grid(row=0, column=0, padx=5, sticky="ew")

        # Clear log button
        self.clear_btn = ttk.Button(
            button_frame,
            text=t("btn_clear_logs"),
            command=self._clear_logs
        )
        self.clear_btn.grid(row=0, column=1, padx=5, sticky="ew")

        # Exit button
        self.exit_btn = ttk.Button(
            button_frame,
            text=t("btn_quit"),
            command=self._on_exit
        )
        self.exit_btn.grid(row=0, column=2, padx=5, sticky="ew")

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
                t("processing_in_progress"),
                t("confirm_quit")
            ):
                return

        # Call cleanup callback before closing
        if self.on_exit_callback:
            try:
                self.log(t("closing"), "INFO")
                self.on_exit_callback()
            except Exception as e:
                self.log(f"{t('close_error')}: {e}", "ERROR")

        self.root.quit()
        self.root.destroy()

    def log(self, message, level="INFO"):
        """Add a log message directly."""
        self.log_queue.put(f"{level} - {message}")

    def _on_setting_change(self, section, key, value):
        """Handle setting change from settings panel."""
        self.log(f"{t('setting_changed')}: {section}.{key} = {value}", "INFO")

    def _on_language_change(self, event=None):
        """Handle language change."""
        new_lang = self.lang_var.get()
        set_language(new_lang)
        self._update_ui_language()

    def _update_ui_language(self):
        """Update all UI elements with current language."""
        self.root.title(t("app_title"))
        self.title_label.config(text=t("app_title"))
        self.lang_label.config(text=t("language") + ":")
        self.log_frame.config(text=t("logs"))
        self.process_btn.config(text=t("btn_process"))
        self.clear_btn.config(text=t("btn_clear_logs"))
        self.exit_btn.config(text=t("btn_quit"))

        # Update status if not processing
        if not self.is_processing:
            self.status_var.set(t("ready"))

        # Update settings panel
        self.settings_panel.update_language()

    def run(self):
        """Start the main event loop."""
        self.log(t("app_started"), "INFO")
        self.root.mainloop()
