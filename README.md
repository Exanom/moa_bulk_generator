# moa_bulk_generator

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)]()

A Python library to generate multiple synthetic datasets with configurable concept drift using the Java **MOA (Massive Online Analysis)** framework. 

## Table of Contents

- [Features](#features)  
- [Installation](#installation)
- [Requirements](#requirements)
- [Usage](#usage)
  - [Usage In Scripts](#usage-in-scripts)  
  - [Usage From Command Line](#usage-from-command-line)  
- [Configuration File](#configuration-file)
- [Dataset Definition Format](#dataset-definition-format)
- [Project Structure](#project-structure)  
- [Planned Features](#pllaned--features)  

---

## Features

- Automates generation of multiple datasets via the Java MOA framework.
- Supports specifying various types of concept drift (e.g., sudden, gradual).
- Generates datasets in bulk.

---

## Installation

```bash
pip install git+https://github.com/Exanom/moa_bulk_generator.git
```
Or for editable module:
```bash
git clone https://github.com/Exanom/moa_bulk_generator.git
cd moa_bulk_generator
pip install -e .
```
---
## Requirements


This project depends on the Java framework **MOA (Massive Online Analysis)**.  
Download MOA from: https://moa.cms.waikato.ac.nz/downloads/

You must also have a Java JDK installed (see `java -version`).

---
## Usage


`moa_bulk_generator` can be run from the command line or imported as a Python module.

### Invocation modes
- **Interactive**: Start an interactive CLI to create/edit dataset definitions.
- **Automatic (non-interactive)**: Load dataset definitions from a text file and generate datasets automatically.

### Parameters
- `--interactive` (*bool*, default: `false`)  
  Enable interactive mode. If `false`, `--datasets` must be provided. Note: even in non-interactive mode the tool may prompt for input if a dataset definition is invalid or if the output directory does not exist.

- `--datasets <path>` (*str*)  
  Path to a text file with dataset definitions (one definition per line). In interactive mode the file will be loaded and editable.

- `--config <path>` (*str*, default: `config.json`)  
  Path to a JSON config file. If the file does not exist, a template config will be created and an exception will be raised.

- `--out <path>` (*str*, default: `results`)  
  Directory where generated datasets will be saved.

### Usage In Scripts

Import the main class:

```python
from moa_bulk_generator import MOABulkGenerator
```

Initialize the generator (examples):

```python
# interactive mode
bulk_generator = MOABulkGenerator(interactive=True)

# automatic mode (load definitions from a file)
bulk_generator = MOABulkGenerator(datasets='datasets.txt')

# full constructor
bulk_generator = MOABulkGenerator(
    interactive=True,
    datasets='datasets.txt',
    config='custom_config.json',
    out='datasets/synthetic'
)
```
Run the generator:

```python
bulk_generator.run()
```

Once the object is properly initialized, the main functionality can be ran with run() method:

```python
bulk_generator.run()
```

## Usage From Command Line

Run in interactive mode (opens the CLI editor):

```bash
python -m moa_bulk_generator -i
```

Run in automatic mode, using dataset definitions from a file:

```bash
python -m moa_bulk_generator -d datasets.txt
```

Run with all parameters:

```bash
python -m moa_bulk_generator -d datasets.txt -i --out synthetic --config moa_config.json
```

Notes:
- --interactive / -i starts the interactive CLI. If --datasets is supplied together with --interactive, the file will be loaded for editing in the interactive session.
- --datasets / -d expects a path to a plain text file with dataset definitions.
