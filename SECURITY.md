# Security Policy

## Supported Versions

Currently supported versions of PubliCast:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in PubliCast, please follow these steps:

### 1. **Do Not** Open a Public Issue
Please do not report security vulnerabilities through public GitHub issues.

### 2. Report Privately
Send an email to: **[your-email@example.com]** with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. Response Timeline
- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-14 days
  - Medium: 14-30 days
  - Low: 30-90 days

### 4. Disclosure Policy
- We will acknowledge your report within 48 hours
- We will provide a detailed response within 7 days
- We will work with you to understand and resolve the issue
- We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Considerations

### Current Security Measures
- No network communication (local processing only)
- No data collection or telemetry
- All processing happens locally on your machine
- No external API calls (except optional Google API dependencies)

### Known Limitations
- **Windows-only**: Currently only supports Windows OS
- **Local Audacity Control**: Requires Audacity to be running locally
- **File System Access**: Requires read/write access to audio files

### Best Practices for Users
1. **Download from Official Sources**: Only download PubliCast from the official GitHub repository
2. **Verify Dependencies**: Review `requirements.txt` before installation
3. **Use Virtual Environments**: Always use a Python virtual environment
4. **Keep Updated**: Update to the latest version for security fixes
5. **Review Logs**: Check log files in `logs/` directory for unexpected behavior

## Security Updates

Security updates will be released as patch versions (e.g., 0.1.1) and announced via:
- GitHub Security Advisories
- Release notes in CHANGELOG.md
- GitHub Releases page

## Scope

### In Scope
- Code execution vulnerabilities
- Dependency vulnerabilities
- File system access issues
- Privilege escalation
- Data leakage

### Out of Scope
- Issues in Audacity itself (report to Audacity team)
- Issues in Python or system libraries (report to respective projects)
- Social engineering attacks
- Physical access attacks

## Contact

For security concerns: **[your-email@example.com]**

For general issues: [GitHub Issues](https://github.com/pegallardo/publi_cast/issues)

---

**Thank you for helping keep PubliCast secure!**

