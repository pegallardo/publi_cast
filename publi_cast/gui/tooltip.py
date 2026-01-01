# -*- coding: utf-8 -*-
"""
PubliCast - Tooltip widget for tkinter
"""
import tkinter as tk


class Tooltip:
    """
    Creates a tooltip for a given widget.
    """
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.scheduled_id = None
        
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<ButtonPress>", self._on_leave)

    def _on_enter(self, event=None):
        """Schedule tooltip display."""
        self._cancel_scheduled()
        self.scheduled_id = self.widget.after(self.delay, self._show_tooltip)

    def _on_leave(self, event=None):
        """Hide tooltip and cancel scheduled display."""
        self._cancel_scheduled()
        self._hide_tooltip()

    def _cancel_scheduled(self):
        """Cancel any scheduled tooltip display."""
        if self.scheduled_id:
            self.widget.after_cancel(self.scheduled_id)
            self.scheduled_id = None

    def _show_tooltip(self):
        """Display the tooltip."""
        if self.tooltip_window or not self.text:
            return
            
        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # Create tooltip content
        frame = tk.Frame(tw, background="#ffffe0", borderwidth=1, relief="solid")
        frame.pack()
        
        label = tk.Label(
            frame,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            foreground="#000000",
            font=("Segoe UI", 9),
            padx=8,
            pady=5
        )
        label.pack()

    def _hide_tooltip(self):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def update_text(self, text):
        """Update tooltip text."""
        self.text = text

