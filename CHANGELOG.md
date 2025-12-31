# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive README with installation and usage instructions
- CONTRIBUTING.md for contributor guidelines
- CHANGELOG.md for version tracking
- Improved setup.py with proper metadata and dependencies

### Changed
- Updated README with correct GitHub repository URL
- Enhanced installation instructions with virtual environment setup
- Added mod-script-pipe setup instructions
- Improved documentation for automated vs manual modes

### Fixed
- Corrected GitHub repository URL in README
- Aligned dependencies between requirements.txt and setup.py
- Added logs/ directory to .gitignore

## [0.1.0] - Initial Release

### Added
- Automated audio processing workflow using Audacity
- Integration with Audacity via named pipes (mod-script-pipe)
- Audio enhancement features:
  - Custom EQ curve application (Filter Curve)
  - Audio normalization to -1.0 dB
  - Dynamic range compression
- File selection dialogs for import/export
- Export support for WAV and MP3 formats
- Comprehensive logging system
- Fallback to manual mode when pipes are unavailable
- GUI automation alternative using pyautogui
- Configurable audio processing parameters
- Windows support with named pipe implementation

### Project Structure
- Controllers for user interaction (import/export)
- Services for business logic (Audacity API, logging)
- Repositories for data access (named pipe communication)
- Configuration system for audio processing presets

[Unreleased]: https://github.com/pegallardo/publi_cast/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/pegallardo/publi_cast/releases/tag/v0.1.0

