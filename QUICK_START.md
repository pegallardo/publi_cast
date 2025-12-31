# PubliCast - Quick Start Guide

Get up and running with PubliCast in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:
- ✅ Windows OS
- ✅ Python 3.7 or higher installed
- ✅ Audacity installed

## Installation (5 Steps)

### Step 1: Clone the Repository
```bash
git clone https://github.com/pegallardo/publi_cast.git
cd publi_cast
```

### Step 2: Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Enable Audacity mod-script-pipe ⚠️ CRITICAL
1. Open Audacity
2. Go to **Edit → Preferences → Modules**
3. Find **mod-script-pipe** and set to **Enabled**
4. Click **OK**
5. **Restart Audacity**

### Step 5: Run PubliCast
```powershell
python -m publi_cast.main
```

## First Use

1. **Select Audio File**: Choose your podcast/audio file
2. **Wait for Processing**: The app will automatically:
   - Apply EQ curve
   - Normalize audio
   - Compress dynamics
3. **Save Output**: Choose where to save (WAV or MP3)
4. **Done!** Your audio is enhanced

## Using PowerShell Tasks (Optional)

For easier workflow, use the task runner:

```powershell
# Run the application
.\tasks.ps1 run

# Run tests
.\tasks.ps1 test

# Clean project
.\tasks.ps1 clean

# See all commands
.\tasks.ps1 help
```

## Troubleshooting

### "Pipe Connection Failed" Error
**Solution:** You forgot Step 4! Enable mod-script-pipe in Audacity.

### "Python 3.7 or later required"
**Solution:** Update Python from https://www.python.org/downloads/

### pywin32 Installation Error
```powershell
pip install --upgrade pywin32
python venv/Scripts/pywin32_postinstall.py -install
```

### Audacity Not Found
Edit `publi_cast/config.py`:
```python
AUDACITY_PATH = "C:\\Your\\Path\\To\\audacity.exe"
```

## Customization

Want to change audio processing settings?

Edit `publi_cast/config.py`:

```python
# EQ Curve Points
EQ_CURVE_POINTS = [
    "20 14",   # Boost low frequencies
    "500 0",   # Flat midrange
    # ... add your own points
]

# Compressor Settings
COMPRESSOR_SETTINGS = {
    'Threshold': -18,  # dB
    'Ratio': 5,        # 5:1
    'Attack': 30,      # ms
    'Release': 100,    # ms
}

# Normalize Settings
NORMALIZE_SETTINGS = {
    'peak_level': -1.0,  # dB
}
```

## What's Next?

- 📖 Read the full [README.md](README.md)
- 🤝 Want to contribute? See [CONTRIBUTING.md](CONTRIBUTING.md)
- 🐛 Found a bug? [Report it](https://github.com/pegallardo/publi_cast/issues)
- 💡 Have an idea? [Request a feature](https://github.com/pegallardo/publi_cast/issues)

## Support

Need help? Check:
- [README.md](README.md) - Full documentation
- [GitHub Issues](https://github.com/pegallardo/publi_cast/issues) - Known issues
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide

---

**Happy podcasting! 🎙️**

