# Kubernetes Palette

Kubernetes Palette is a simple image-orchestration tool that helps you set the correct image versions in your Kubernetes manifests using a “palette” (configuration file). Instead of manually editing `image:` lines in your YAML, Palette (via the `kelm.py` script) scans your manifests and substitutes placeholders with registry tags defined in a single configuration.

## Features

- Declarative image management via a central configuration file (palette)
- In-place replacement of `image:` references in Kubernetes manifests
- Optional Git integration: checkout a specific commit and print a version string
- Zero dependencies beyond Python’s standard library
- Single-file CLI (`kelm.py`) for easy distribution

## Installation

1. Clone or download this repository.
2. Ensure you have Python 3 installed (no additional libraries required).
3. Make the main script executable (optional):
```bash
$ chmod +x kelm.py
```
4. (Optional) Place kelm.py in a directory that’s on your PATH for global use.
