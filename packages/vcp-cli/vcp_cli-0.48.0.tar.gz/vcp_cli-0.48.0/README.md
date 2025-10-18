# Virtual Cells Platform Command Line Interface

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/chanzuckerberg/vcp-cli/actions)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

A command-line interface for interacting with the Virtual Cells Platform ("VCP").

## Requirements

- [Python 3.10+](https://www.python.org/downloads/)
- On MacOS or [Windows WSL](https://learn.microsoft.com/en-us/windows/wsl/), you will need a terminal app.
- For the `benchmarks` commands, you will need to be running on an Intel/AMD64 architecture CPU with NVIDIA GPU, running Linux with NVIDIA drivers.
- For other commands (e.g. `data`) you will need a Virtual Cells Platform account ([register here](https://virtualcellmodels.cziscience.com/?register=true))


## Installation

### Core Installation (Minimal)

Install only the core CLI functionality (auth, config, version commands):

```bash
pip install vcp-cli
```

This installs a minimal footprint (<50MB) without heavy dependencies like MLflow, boto3, or benchmarking tools.

### Full Installation

Install all features (model, data, and benchmarks commands):

```bash
pip install vcp-cli[all]
```

### Selective Installation

Install only the features you need:

```bash
# For model operations only
pip install vcp-cli[model]

# For data operations only
pip install vcp-cli[data]

# For benchmarks only
pip install vcp-cli[benchmarks]

# Combine multiple features
pip install vcp-cli[model,data]
```

**Optional Feature Groups:**
- `model` - Model operations (init, stage, submit) - requires MLflow, numpy, copier, GitPython
- `data` - Data operations (search, download, describe) - requires boto3 for S3 downloads
- `benchmarks` - Benchmark operations (run, list, get) - requires cz-benchmarks, anndata

## Documentation

Available at https://chanzuckerberg.github.io/vcp-cli/


## License

This package is licensed under the MIT License.