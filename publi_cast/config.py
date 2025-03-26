import os
import sys

if sys.platform == 'win32':
    PIPE_TO_AUDACITY = '\\\\.\\pipe\\ToSrvPipe'
    PIPE_FROM_AUDACITY = '\\\\.\\pipe\\FromSrvPipe'
else:
    PIPE_BASE = '/tmp/audacity_script_pipe.'
    PIPE_TO_AUDACITY = PIPE_BASE + 'to.' + str(os.getuid())
    PIPE_FROM_AUDACITY = PIPE_BASE + 'from.' + str(os.getuid())

EOL = '\r\n\0' if sys.platform == 'win32' else '\n'

AUDACITY_PATH = "C:\\Program Files\\Audacity\\audacity.exe"

DEFAULT_RETRY_ATTEMPTS = 5
DEFAULT_RETRY_DELAY = 1  # seconds

# Audacity command configuration
COMPRESSOR_SETTINGS = {
    'Threshold': -18,
    'Ratio': 5,
    'Attack': 30,
    'Release': 100,
    'Makeup': 0
}

# EQ curve points - can be modified independently
EQ_CURVE_POINTS = [
    "20 14", 
    "51 14", 
    "63 12", 
    "76 11", 
    "80 10", 
    "90 9", 
    "120 7", 
    "200 4", 
    "260 3", 
    "300 2", 
    "400 1", 
    "500 0", 
    "10000 0", 
    "13000 -5"
]

# Normalize settings
NORMALIZE_SETTINGS = {
    'remove_dc_offset': True,
    'peak_level': -1.0,
    'normalize_stereo': True
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