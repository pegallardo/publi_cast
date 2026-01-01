import os
import sys
import subprocess
import getpass

# Check if Audacity has mod-script-pipe enabled
def check_script_pipe_enabled():
    # Path to Audacity's configuration file
    if sys.platform == 'win32':
        appdata = os.getenv('APPDATA')
        config_path = os.path.join(appdata, "audacity", "audacity.cfg")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                for line in f:
                    if "mod-script-pipe" in line and "enabled=1" in line:
                        return True
    return False

# Windows pipe configuration
if sys.platform == 'win32':
    # Standard pipe names
    PIPE_TO_AUDACITY = r'\\.\pipe\ToSrvPipe'
    PIPE_FROM_AUDACITY = r'\\.\pipe\FromSrvPipe'
    
    # Alternative pipe names to try
    ALT_PIPE_TO_AUDACITY = r'\\.\pipe\audacity_script_pipe.to'
    ALT_PIPE_FROM_AUDACITY = r'\\.\pipe\audacity_script_pipe.from'
    
    # Windows 11 specific pipe names (with user ID)
    username = getpass.getuser()
    WIN11_PIPE_TO_AUDACITY = fr'\\.\pipe\audacity_script_pipe.to.{username}'
    WIN11_PIPE_FROM_AUDACITY = fr'\\.\pipe\audacity_script_pipe.from.{username}'
else:
    PIPE_BASE = '/tmp/audacity_script_pipe.'
    PIPE_TO_AUDACITY = PIPE_BASE + 'to.' + str(os.getuid())
    PIPE_FROM_AUDACITY = PIPE_BASE + 'from.' + str(os.getuid())

EOL = '\r\n\0' if sys.platform == 'win32' else '\n'

AUDACITY_PATH = "C:\\Program Files\\Audacity\\audacity.exe"

DEFAULT_RETRY_ATTEMPTS = 5
DEFAULT_RETRY_DELAY = 2  # seconds

# Compressor type: "audacity" (standard Audacity) or "python" (dynamic compressor)
COMPRESSOR_TYPE = "python"  # Default to Python dynamic compressor

# Audacity standard compressor settings
COMPRESSOR_SETTINGS = {
    'Threshold': -18,
    'Ratio': 5,
    'Attack': 30,
    'Release': 100,
    'Makeup': 0
}

# Python Dynamic Compressor settings (based on compress.ny by Chris Capel)
# Default values from Audacity's Compress dynamics 1.2.6 preset
DYNAMIC_COMPRESSOR_SETTINGS = {
    'compress_ratio': 0.8,      # Compression amount (-.5 to 1.25)
    'hardness': 0.879,          # Compression hardness (0.1 to 1.0)
    'floor': -18.0,             # Floor in dB (-96 to 0)
    'noise_factor': 0.0,        # Noise gate falloff (-2 to 10)
    'scale_max': 0.99           # Maximum amplitude (0.0 to 1.0)
}

# EQ curve points - Podcast preset from Audacity
# Format: "frequency gain_in_dB"
EQ_CURVE_POINTS = [
    "20 15",
    "30 15",
    "40 15",
    "60 15",
    "100 15",
    "140 12",
    "200 6",
    "300 3",
    "500 1",
    "700 0",
    "1000 0",
    "2000 0",
    "3000 0",
    "5000 -3",
    "10000 -6",
    "20000 -6"
]

# Normalize settings
NORMALIZE_SETTINGS = {
    'remove_dc_offset': True,
    'peak_level': -1.0,
    'normalize_stereo': False  # Normalize stereo channels together, not independently
}

AUDACITY_COMMANDS = {
    'select_all': 'SelectAll'

}

# Function to build the filter curve command from points
def build_filter_curve_command():
    points_str = "; ".join(EQ_CURVE_POINTS)
    return f'FilterCurve:FilterType=Draw Points="{points_str}"'

# Function to build the normalize command from settings
def build_normalize_command():
    return f'Normalize:RemoveDcOffset={str(NORMALIZE_SETTINGS["remove_dc_offset"])} PeakLevel={NORMALIZE_SETTINGS["peak_level"]} NormalizeStereo={str(NORMALIZE_SETTINGS["normalize_stereo"])}'

# Function to build the compressor command from settings
def build_compressor_command():
    return f"Compressor:Threshold={COMPRESSOR_SETTINGS['Threshold']},Ratio={COMPRESSOR_SETTINGS['Ratio']},Attack={COMPRESSOR_SETTINGS['Attack']},Release={COMPRESSOR_SETTINGS['Release']},Makeup={COMPRESSOR_SETTINGS['Makeup']}"
