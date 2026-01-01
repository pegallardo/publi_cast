# -*- coding: utf-8 -*-
"""
PubliCast - Settings Panel for audio processing parameters
"""
import tkinter as tk
from tkinter import ttk
import json
import os

from publi_cast.gui.localization import t
from publi_cast.gui.tooltip import Tooltip

# Config file path
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_config.json")

# Default settings
DEFAULT_SETTINGS = {
    "compressor": {
        "threshold": -18,
        "ratio": 5,
        "attack": 30,
        "release": 100,
        "makeup": 0
    },
    "normalize": {
        "peak_level": -1.0
    }
}

# Settings definitions with min, max, step and tooltip key
SETTINGS_DEFS = {
    "compressor": {
        "threshold": {"label_key": "threshold", "tooltip_key": "tooltip_threshold", "min": -60, "max": 0, "step": 1},
        "ratio": {"label_key": "ratio", "tooltip_key": "tooltip_ratio", "min": 1, "max": 20, "step": 0.5},
        "attack": {"label_key": "attack", "tooltip_key": "tooltip_attack", "min": 0.1, "max": 1000, "step": 1},
        "release": {"label_key": "release", "tooltip_key": "tooltip_release", "min": 1, "max": 3000, "step": 10},
        "makeup": {"label_key": "makeup", "tooltip_key": "tooltip_makeup", "min": -30, "max": 30, "step": 1}
    },
    "normalize": {
        "peak_level": {"label_key": "peak_level", "tooltip_key": "tooltip_peak_level", "min": -10, "max": 0, "step": 0.1}
    }
}


def load_settings():
    """Load settings from config file or return defaults."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """Save settings to config file."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)


def apply_settings_to_config(settings):
    """Apply settings to the config module."""
    from publi_cast import config
    
    config.COMPRESSOR_SETTINGS['Threshold'] = settings['compressor']['threshold']
    config.COMPRESSOR_SETTINGS['Ratio'] = settings['compressor']['ratio']
    config.COMPRESSOR_SETTINGS['Attack'] = settings['compressor']['attack']
    config.COMPRESSOR_SETTINGS['Release'] = settings['compressor']['release']
    config.COMPRESSOR_SETTINGS['Makeup'] = settings['compressor']['makeup']
    config.NORMALIZE_SETTINGS['peak_level'] = settings['normalize']['peak_level']


class SettingsPanel(ttk.LabelFrame):
    """Panel with sliders and spinboxes for audio processing settings."""

    def __init__(self, parent, on_change_callback=None, on_language_change=None):
        super().__init__(parent, text=t("settings_title"), padding="10")
        self.on_change_callback = on_change_callback
        self.on_language_change = on_language_change
        self.settings = load_settings()
        self.widgets = {}
        self.tooltips = {}
        self.labels = {}

        self._create_widgets()
        apply_settings_to_config(self.settings)

    def _create_widgets(self):
        """Create all setting widgets."""
        row = 0

        # Compressor section
        self.comp_label = ttk.Label(self, text=t("compressor"), font=("Segoe UI", 10, "bold"))
        self.comp_label.grid(row=row, column=0, columnspan=3, sticky="w", pady=(0, 5))
        row += 1

        for key, def_info in SETTINGS_DEFS["compressor"].items():
            self._create_slider_row(row, "compressor", key, def_info)
            row += 1

        # Separator
        ttk.Separator(self, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=10)
        row += 1

        # Normalize section
        self.norm_label = ttk.Label(self, text=t("normalize"), font=("Segoe UI", 10, "bold"))
        self.norm_label.grid(row=row, column=0, columnspan=3, sticky="w", pady=(0, 5))
        row += 1

        for key, def_info in SETTINGS_DEFS["normalize"].items():
            self._create_slider_row(row, "normalize", key, def_info)
            row += 1

    def _create_slider_row(self, row, section, key, def_info):
        """Create a row with label, slider, spinbox and tooltip."""
        value = self.settings[section][key]
        var = tk.DoubleVar(value=value)

        # Label with info icon
        label_text = t(def_info["label_key"])
        label = ttk.Label(self, text=f"ℹ️ {label_text}", width=18)
        label.grid(row=row, column=0, sticky="w", padx=(0, 5))

        # Add tooltip to label
        tooltip = Tooltip(label, t(def_info["tooltip_key"]))
        self.tooltips[f"{section}.{key}"] = tooltip
        self.labels[f"{section}.{key}"] = {"label": label, "label_key": def_info["label_key"], "tooltip_key": def_info["tooltip_key"]}

        # Slider
        slider = ttk.Scale(
            self, from_=def_info["min"], to=def_info["max"],
            variable=var, orient="horizontal", length=150,
            command=lambda v, s=section, k=key, vr=var: self._on_slider_change(s, k, vr)
        )
        slider.grid(row=row, column=1, sticky="ew", padx=5)

        # Spinbox
        spinbox = ttk.Spinbox(
            self, from_=def_info["min"], to=def_info["max"],
            increment=def_info["step"], textvariable=var, width=8,
            command=lambda s=section, k=key, vr=var: self._on_value_change(s, k, vr)
        )
        spinbox.grid(row=row, column=2, padx=(5, 0))
        spinbox.bind("<Return>", lambda e, s=section, k=key, vr=var: self._on_value_change(s, k, vr))
        spinbox.bind("<FocusOut>", lambda e, s=section, k=key, vr=var: self._on_value_change(s, k, vr))

        self.widgets[f"{section}.{key}"] = {"var": var, "slider": slider, "spinbox": spinbox}

    def _on_slider_change(self, section, key, var):
        """Handle slider change."""
        self._update_setting(section, key, var.get())

    def _on_value_change(self, section, key, var):
        """Handle spinbox value change."""
        self._update_setting(section, key, var.get())

    def _update_setting(self, section, key, value):
        """Update setting, save and apply."""
        self.settings[section][key] = round(value, 2)
        save_settings(self.settings)
        apply_settings_to_config(self.settings)
        if self.on_change_callback:
            self.on_change_callback(section, key, value)

    def update_language(self):
        """Update all labels and tooltips for current language."""
        self.config(text=t("settings_title"))
        self.comp_label.config(text=t("compressor"))
        self.norm_label.config(text=t("normalize"))

        for key, info in self.labels.items():
            label_text = t(info["label_key"])
            info["label"].config(text=f"ℹ️ {label_text}")
            self.tooltips[key].update_text(t(info["tooltip_key"]))

