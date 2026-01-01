# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2026-01-01 (Config Directory Management)

### Added
- User-writable configuration directory support
  - Windows: %APPDATA%/PubliCast/user_config.json
  - Linux/macOS: ~/.config/publi_cast/user_config.json
- Automatic config directory creation on first write
- PyInstaller spec includes user_config.json in package data
- Package data configuration in setup.py and pyproject.toml

### Fixed
- Settings persistence in protected installation directories
- Config file write access when app is installed system-wide or bundled

## [0.2.0] - 2025-12-31 (Major Feature Release)

### Added
- Python dynamic compressor as alternative to Audacity standard compressor
- Bilingual UI support (French/English) with language persistence
- Comprehensive parameter tooltips for all audio settings
- Settings panel with sliders and spinboxes for real-time parameter adjustment
- User configuration system with JSON persistence
- Improved pipe management and application lifecycle handling
- Nyquist dynamic compressor plugins (compress.ny, compress-advanced.ny)

### Changed
- EQ and normalization defaults updated to match Audacity Podcast preset
- Enhanced audio processing workflow with compressor type selection
- Improved error handling and logging
- CI configuration updates

### Fixed
- Corrected imports and added missing dependencies
- Fixed pipe creation and management on Windows 11
- Minor fixes for pipe initialization

## [0.1.1] - 2025-05-01 (Windows 11 & Documentation)

### Added
- README with installation and usage instructions
- CONTRIBUTING.md for contributor guidelines
- CHANGELOG.md for version tracking

### Changed
- Updated documentation with correct GitHub repository URL
- Enhanced installation instructions with virtual environment setup
- Added mod-script-pipe setup instructions

### Fixed
- Windows 11 specific Audacity named pipe handling
- Improved pipe naming for user-specific pipes
- Import filename fixes
- Minor fixes for 0.1 release

## [0.1.0] - 2025-03-26 (Initial Release)

### Added
- Automated audio processing workflow using Audacity
- Integration with Audacity via named pipes (mod-script-pipe)
- Audio enhancement features:
  - Custom EQ curve application (Filter Curve)
  - Audio normalization to -1.0 dB
  - Dynamic range compression
- File selection dialogs for import/export
- Export support for WAV and MP3 formats
- Comprehensive logging system with logger service
- Fallback to manual mode when pipes are unavailable
- GUI automation alternative using pyautogui
- Configurable audio processing parameters
- Windows support with named pipe implementation
- Dependency injection container for service management
- Unit testing framework
- Non-blocking pipe reading using threads

### Project Structure
- Controllers for user interaction (import/export)
- Services for business logic (Audacity API, logging)
- Repositories for data access (named pipe communication)
- Configuration system for audio processing presets
- Comprehensive test suite

[Unreleased]: https://github.com/pegallardo/publi_cast/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/pegallardo/publi_cast/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/pegallardo/publi_cast/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/pegallardo/publi_cast/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/pegallardo/publi_cast/releases/tag/v0.1.0
