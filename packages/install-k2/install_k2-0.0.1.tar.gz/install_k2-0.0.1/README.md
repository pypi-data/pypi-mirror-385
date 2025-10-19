# install-k2

[![PyPI version](https://badge.fury.io/py/install-k2.svg)](https://badge.fury.io/py/install-k2)

A simple utility to automatically install the correct k2 wheel for your platform and environment.

## Installation

```bash
pip install install-k2
```

## Usage

After installation, you can run the installer using either command:

```bash
# Using hyphen (recommended)
install-k2

# Or using underscore
install_k2
```

### Options

- `--dry-run`: Show what would be installed without making changes

```bash
install-k2 --dry-run
```

## What It Does

The installer automatically:
- Detects your operating system (Linux, macOS, Windows)
- Identifies your Python version
- Detects CUDA version (if available on Linux)
- Finds the appropriate PyTorch version
- Downloads and installs the compatible k2 wheel from official sources

### Supported Platforms

- **Linux**: CPU and CUDA wheels
- **macOS**: CPU wheels (Intel and Apple Silicon)
- **Windows**: CPU wheels

## Wheel Sources

The installer fetches wheels from official k2 repositories:
- Linux CUDA: https://k2-fsa.github.io/k2/installation/pre-compiled-cuda-wheels-linux/
- macOS CPU: https://k2-fsa.github.io/k2/installation/pre-compiled-cpu-wheels-macos/
- Windows CPU: https://k2-fsa.github.io/k2/installation/pre-compiled-cpu-wheels-windows/

## Requirements

- Python 3.9 or higher
- PyTorch (automatically detected)

## License

Apache License 2.0

## Author

The Lattifai Development Team
