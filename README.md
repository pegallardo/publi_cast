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
   ```
   git clone https://github.com/yourusername/publi_cast.git
   cd publi_cast
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Make sure Audacity is installed at the default location or update the path in `config.py`

## Usage

Run the application:
```
python -m publi_cast.main
```

The application will:
1. Start Audacity (or connect to a running instance)
2. Prompt you to select an audio file
3. Apply the configured audio processing chain
4. Prompt you to save the processed file

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
```
pytest
```

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.