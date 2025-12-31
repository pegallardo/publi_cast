# PubliCast - Frequently Asked Questions (FAQ)

## General Questions

### What is PubliCast?
PubliCast is an audio processing application that automates podcast and audio enhancement using Audacity. It applies a professional audio processing chain (EQ, normalization, compression) automatically.

### Why use PubliCast instead of Audacity directly?
- **Consistency**: Same processing applied every time
- **Speed**: No manual clicking through menus
- **Automation**: Process multiple files with the same settings
- **Reproducibility**: Share your config with team members

### Is PubliCast free?
Yes! PubliCast is open-source under the GPL-3.0 license.

---

## Installation & Setup

### What are the system requirements?
- Windows OS (currently Windows-only)
- Python 3.7 or higher
- Audacity (any recent version)
- ~100MB disk space for dependencies

### Do I need to know Python to use PubliCast?
No! Just follow the installation instructions. Basic command-line knowledge is helpful but not required.

### What is mod-script-pipe and why do I need it?
mod-script-pipe is an Audacity module that allows external programs to control Audacity. Without it, PubliCast falls back to manual mode where you have to apply effects yourself.

### How do I enable mod-script-pipe?
1. Open Audacity
2. Edit → Preferences → Modules
3. Set mod-script-pipe to "Enabled"
4. Restart Audacity

### I enabled mod-script-pipe but it still doesn't work
- Make sure you **restarted Audacity** after enabling
- Check that Audacity is fully closed before running PubliCast
- Try running Audacity as Administrator
- Check the logs in the `logs/` directory for errors

---

## Usage

### What audio formats are supported?
**Input**: MP3, WAV, OGG, FLAC, M4A
**Output**: WAV, MP3 (320kbps)

### Can I process multiple files at once?
Currently, PubliCast processes one file at a time. Batch processing is planned for a future release.

### How long does processing take?
Depends on file length:
- 1-hour podcast: ~30-60 seconds
- 5-minute audio: ~10-15 seconds

### Can I customize the audio processing?
Yes! Edit `publi_cast/config.py` to change:
- EQ curve points
- Compressor settings (threshold, ratio, attack, release)
- Normalization level
- And more

### What does each effect do?
- **Filter Curve EQ**: Shapes frequency response (reduce rumble, enhance clarity)
- **Normalize**: Ensures consistent volume levels
- **Compressor**: Reduces dynamic range for more consistent loudness

---

## Troubleshooting

### "Pipe Connection Failed" error
**Cause**: mod-script-pipe not enabled or Audacity not running
**Solution**: 
1. Enable mod-script-pipe in Audacity preferences
2. Restart Audacity
3. Run PubliCast again

### "Python 3.7 or later required" error
**Cause**: Python version too old
**Solution**: Install Python 3.7+ from https://www.python.org/downloads/

### "Audacity not found" error
**Cause**: Audacity not installed or in non-standard location
**Solution**: 
- Install Audacity, OR
- Edit `publi_cast/config.py` and set correct `AUDACITY_PATH`

### pywin32 installation fails
**Solution**:
```powershell
pip install --upgrade pywin32
python venv/Scripts/pywin32_postinstall.py -install
```

### Processing sounds bad / too compressed
**Solution**: Adjust settings in `publi_cast/config.py`:
- Lower compressor ratio (try 3 instead of 5)
- Raise threshold (try -12 instead of -18)
- Adjust EQ curve points

### Output file is too quiet / too loud
**Solution**: Change normalization level in `config.py`:
```python
NORMALIZE_SETTINGS = {
    'peak_level': -1.0,  # Change this value (-3.0 for quieter, -0.5 for louder)
}
```

---

## Advanced

### Can I use PubliCast on Mac or Linux?
Not currently. The named pipe implementation is Windows-specific. Linux/Mac support is planned.

### Can I add custom effects?
Yes! Edit `publi_cast/main.py` and add Audacity commands to the `commands` list. See Audacity's scripting documentation for available commands.

### How do I contribute to PubliCast?
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Where are the log files?
In the `logs/` directory. Each run creates a timestamped log file.

### Can I use this commercially?
Yes, under the GPL-3.0 license terms. You can use it for commercial podcasts, but if you modify and distribute the code, you must share your changes.

---

## Performance

### Why is it slow on first run?
Python is loading dependencies. Subsequent runs are faster.

### Can I speed up processing?
Processing speed is limited by Audacity's effect processing time. PubliCast itself adds minimal overhead.

---

## Getting Help

### Where can I get help?
1. Check this FAQ
2. Read [README.md](README.md)
3. Check [GitHub Issues](https://github.com/pegallardo/publi_cast/issues)
4. Open a new issue with details

### How do I report a bug?
Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) on GitHub Issues.

### How do I request a feature?
Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) on GitHub Issues.

---

**Still have questions? [Open an issue](https://github.com/pegallardo/publi_cast/issues)!**

