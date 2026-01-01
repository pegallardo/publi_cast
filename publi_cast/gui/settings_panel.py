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

# Config file path (user-writable)
if os.name == 'nt':
    _appdata = os.getenv('APPDATA') or os.path.expanduser('~')
    _config_dir = os.path.join(_appdata, 'PubliCast')
else:
    _config_dir = os.path.join(os.path.expanduser('~'), '.config', 'publi_cast')
CONFIG_FILE = os.path.join(_config_dir, 'user_config.json')

# Default settings
DEFAULT_SETTINGS = {
    "compressor_type": "python",  # "python" or "audacity"
    "compressor": {
        "threshold": -18,
        "ratio": 5,
        "attack": 30,
        "release": 100,
        "makeup": 0
    },
    "dynamic_compressor": {
        "compress_ratio": 0.8,
        "hardness": 0.879,
        "floor": -18.0,
        "noise_factor": 0.0,
        "scale_max": 0.99
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
    "dynamic_compressor": {
        "compress_ratio": {"label_key": "compress_ratio", "tooltip_key": "tooltip_compress_ratio", "min": -0.5, "max": 1.25, "step": 0.05},
        "hardness": {"label_key": "hardness", "tooltip_key": "tooltip_hardness", "min": 0.1, "max": 1.0, "step": 0.01},
        "floor": {"label_key": "floor", "tooltip_key": "tooltip_floor", "min": -96, "max": 0, "step": 1},
        "noise_factor": {"label_key": "noise_factor", "tooltip_key": "tooltip_noise_factor", "min": -2, "max": 10, "step": 0.1},
        "scale_max": {"label_key": "scale_max", "tooltip_key": "tooltip_scale_max", "min": 0.0, "max": 1.0, "step": 0.01}
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
                loaded = json.load(f)
                # Merge with defaults to ensure all keys exist
                result = DEFAULT_SETTINGS.copy()
                for key in result:
                    if key in loaded:
                        if isinstance(result[key], dict):
                            result[key].update(loaded[key])
                        else:
                            result[key] = loaded[key]
                return result
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """Save settings to config file."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)


def apply_settings_to_config(settings):
    """Apply settings to the config module."""
    from publi_cast import config

    # Compressor type
    config.COMPRESSOR_TYPE = settings.get('compressor_type', 'python')

    # Audacity compressor settings
    config.COMPRESSOR_SETTINGS['Threshold'] = settings['compressor']['threshold']
    config.COMPRESSOR_SETTINGS['Ratio'] = settings['compressor']['ratio']
    config.COMPRESSOR_SETTINGS['Attack'] = settings['compressor']['attack']
    config.COMPRESSOR_SETTINGS['Release'] = settings['compressor']['release']
    config.COMPRESSOR_SETTINGS['Makeup'] = settings['compressor']['makeup']

    # Dynamic compressor settings
    config.DYNAMIC_COMPRESSOR_SETTINGS['compress_ratio'] = settings['dynamic_compressor']['compress_ratio']
    config.DYNAMIC_COMPRESSOR_SETTINGS['hardness'] = settings['dynamic_compressor']['hardness']
    config.DYNAMIC_COMPRESSOR_SETTINGS['floor'] = settings['dynamic_compressor']['floor']
    config.DYNAMIC_COMPRESSOR_SETTINGS['noise_factor'] = settings['dynamic_compressor']['noise_factor']
    config.DYNAMIC_COMPRESSOR_SETTINGS['scale_max'] = settings['dynamic_compressor']['scale_max']

    # Normalize settings
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
        self.section_frames = {}

        self._create_widgets()
        apply_settings_to_config(self.settings)

    def _create_widgets(self):
        """Create all setting widgets."""
        row = 0

        # Compressor type selector
        type_frame = ttk.Frame(self)
        type_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 10))

        self.type_label = ttk.Label(type_frame, text=t("compressor_type") + ":", font=("Segoe UI", 10, "bold"))
        self.type_label.pack(side="left")

        self.compressor_type_var = tk.StringVar(value=self.settings.get("compressor_type", "python"))

        self.radio_python = ttk.Radiobutton(
            type_frame, text=t("compressor_python"), value="python",
            variable=self.compressor_type_var, command=self._on_compressor_type_change
        )
        self.radio_python.pack(side="left", padx=(10, 5))

        self.radio_audacity = ttk.Radiobutton(
            type_frame, text=t("compressor_audacity"), value="audacity",
            variable=self.compressor_type_var, command=self._on_compressor_type_change
        )
        self.radio_audacity.pack(side="left", padx=5)
        row += 1

        # Dynamic Compressor section (Python)
        self.dyn_frame = ttk.LabelFrame(self, text=t("dynamic_compressor"), padding="5")
        self.dyn_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 5))
        self.section_frames["dynamic_compressor"] = self.dyn_frame

        dyn_row = 0
        for key, def_info in SETTINGS_DEFS["dynamic_compressor"].items():
            self._create_slider_row_in_frame(self.dyn_frame, dyn_row, "dynamic_compressor", key, def_info)
            dyn_row += 1
        row += 1

        # Audacity Compressor section
        self.aud_frame = ttk.LabelFrame(self, text=t("compressor"), padding="5")
        self.aud_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 5))
        self.section_frames["compressor"] = self.aud_frame

        aud_row = 0
        for key, def_info in SETTINGS_DEFS["compressor"].items():
            self._create_slider_row_in_frame(self.aud_frame, aud_row, "compressor", key, def_info)
            aud_row += 1
        row += 1

        # Separator
        ttk.Separator(self, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=10)
        row += 1

        # Normalize section
        self.norm_label = ttk.Label(self, text=t("normalize"), font=("Segoe UI", 10, "bold"))
        self.norm_label.grid(row=row, column=0, columnspan=3, sticky="w", pady=(0, 5))
        row += 1

        for key, def_info in SETTINGS_DEFS["normalize"].items():
            self._create_slider_row_in_frame(self, row, "normalize", key, def_info)
            row += 1

        # Update visibility based on compressor type
        self._update_compressor_visibility()

    def _on_compressor_type_change(self):
        """Handle compressor type change."""
        self.settings["compressor_type"] = self.compressor_type_var.get()
        save_settings(self.settings)
        apply_settings_to_config(self.settings)
        self._update_compressor_visibility()
        if self.on_change_callback:
            self.on_change_callback("compressor_type", "type", self.compressor_type_var.get())

    def _update_compressor_visibility(self):
        """Show/hide compressor sections based on selected type."""
        comp_type = self.compressor_type_var.get()
        if comp_type == "python":
            self.dyn_frame.grid()
            self.aud_frame.grid_remove()
        else:
            self.dyn_frame.grid_remove()
            self.aud_frame.grid()

    def _create_slider_row_in_frame(self, frame, row, section, key, def_info):
        """Create a row with label, slider, spinbox and tooltip in a specific frame."""
        value = self.settings[section][key]
        var = tk.DoubleVar(value=value)

        # Label with info icon
        label_text = t(def_info["label_key"])
        label = ttk.Label(frame, text=f"ℹ️ {label_text}", width=18)
        label.grid(row=row, column=0, sticky="w", padx=(0, 5))

        # Add tooltip to label
        tooltip = Tooltip(label, t(def_info["tooltip_key"]))
        self.tooltips[f"{section}.{key}"] = tooltip
        self.labels[f"{section}.{key}"] = {"label": label, "label_key": def_info["label_key"], "tooltip_key": def_info["tooltip_key"]}

        # Slider
        slider = ttk.Scale(
            frame, from_=def_info["min"], to=def_info["max"],
            variable=var, orient="horizontal", length=150,
            command=lambda v, s=section, k=key, vr=var: self._on_slider_change(s, k, vr)
        )
        slider.grid(row=row, column=1, sticky="ew", padx=5)

        # Spinbox
        spinbox = ttk.Spinbox(
            frame, from_=def_info["min"], to=def_info["max"],
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
        self.type_label.config(text=t("compressor_type") + ":")
        self.radio_python.config(text=t("compressor_python"))
        self.radio_audacity.config(text=t("compressor_audacity"))
        self.dyn_frame.config(text=t("dynamic_compressor"))
        self.aud_frame.config(text=t("compressor"))
        self.norm_label.config(text=t("normalize"))

        for key, info in self.labels.items():
            label_text = t(info["label_key"])
            info["label"].config(text=f"ℹ️ {label_text}")
            self.tooltips[key].update_text(t(info["tooltip_key"]))

