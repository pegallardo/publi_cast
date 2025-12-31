# PubliCast

PubliCast is an audio processing application that automates the enhancement of audio files using Audacity. It's designed to streamline the workflow for podcast producers, content creators, and audio professionals.

## Features

- Automated audio processing workflow
- Integration with Audacity via named pipes
- Audio enhancement with configurable presets:
  - EQ curve application
  - Compression
  - Normalization
- Simple file selection interface
- Export to multiple formats (WAV, MP3)
- Comprehensive logging system

## Requirements

- Python 3.7+
- Audacity installed on your system
- Windows OS (currently Windows-only due to pipe implementation)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/pegallardo/publi_cast.git
   cd publi_cast
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate on Windows (PowerShell)
   .\venv\Scripts\Activate.ps1

   # Activate on Windows (Command Prompt)
   .\venv\Scripts\activate.bat
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Audacity:
   - Download from: https://www.audacityteam.org/download/
   - Install to default location: `C:\Program Files\Audacity\audacity.exe`
   - Or update the path in `publi_cast/config.py` if installed elsewhere

5. **Enable mod-script-pipe in Audacity (Critical)**:
   - Open Audacity
   - Go to **Edit → Preferences → Modules**
   - Set **mod-script-pipe** to **Enabled**
   - Click **OK** and restart Audacity

   ⚠️ **Without this step, the application will fall back to manual mode**

## Usage

Run the application:
```bash
python -m publi_cast.main
```

The application will:
1. Start Audacity (or connect to a running instance)
2. Prompt you to select an audio file
3. Apply the configured audio processing chain:
   - **Filter Curve EQ** - Custom frequency shaping
   - **Normalize** - Level normalization to -1.0 dB
   - **Compressor** - Dynamic range compression
4. Prompt you to save the processed file (WAV or MP3)

### Automated vs Manual Mode

- **Automated Mode** (if mod-script-pipe is enabled): Fully automated processing
- **Manual Mode** (fallback): The app will guide you through manual steps in Audacity

## Configuration

Edit `publi_cast/config.py` to customize:
- EQ curve points
- Compressor settings
- Normalization parameters
- Audacity path

## Development

### Project Structure
- `publi_cast/main.py`: Application entry point
- `publi_cast/config.py`: Configuration settings
- `publi_cast/repositories/`: Data access layer
- `publi_cast/services/`: Business logic
- `publi_cast/controllers/`: User interaction

### Running Tests
```bash
pytest
```

## Troubleshooting

### mod-script-pipe not working
- Ensure Audacity is completely closed before enabling mod-script-pipe
- After enabling, restart Audacity
- Check that the module shows as "Enabled" in Preferences → Modules

### pywin32 installation issues
```bash
pip install --upgrade pywin32
python venv/Scripts/pywin32_postinstall.py -install
```

### Custom Audacity path
Edit `publi_cast/config.py`:
```python
AUDACITY_PATH = "C:\\Your\\Custom\\Path\\audacity.exe"
```

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.