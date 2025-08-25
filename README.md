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
- [Switching Concept Drift](#switching-concept-drift)
- [Project Structure](#project-structure)
- [Planned Features](#planned-features)

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

- `--interactive` (_bool_, default: `false`)  
  Enable interactive mode. If `false`, `--datasets` must be provided. Note: even in non-interactive mode the tool may prompt for input if a dataset definition is invalid or if the output directory does not exist.

- `--datasets <path>` (_str_)  
  Path to a text file with dataset definitions (one definition per line). In interactive mode the file will be loaded and editable.

- `--config <path>` (_str_, default: `config.json`)  
  Path to a JSON config file. If the file does not exist, a template config will be created and an exception will be raised.

- `--out <path>` (_str_, default: `results`)  
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

### Usage From Command Line

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

> **Note about `--config` and `--out`**
>
> If the path provided to `--config` or `--out` does not exist, the tool will create the final file/directory component at runtime, **but the specified parent directory must already exist**.  
> Example: `--out "datasets/synthetic"` will create the `synthetic` directory, but the parent directory `datasets` must already exist. If a parent directory is missing, the tool will exit with an error.

---

## Configuration File

The tool is configured via a JSON file. The following keys are used:

- `"MOA_path"`  
  Path (absolute or relative to the current working directory) to the main MOA installation directory — the directory that contains the `lib/` folder.
  > Note: The tool uses the MOA JARs located in `MOA_path/lib`. The two JARS specifically used(In our tests they were the only files required):
  >
  > - `moa.jar`
  > - `sizeofag-1.1.0.jar`
- `"java_path"`  
   The command or path used to run Java. For standard installs `"java"` is usually sufficient. Verify on your system with:
  ```bash
  java --version
  ```
  If Java is not on the PATH, set this to the full path to the java executable.

### Example `config.json`

```json
{
  "MOA_path": "moa/",
  "Java_path": "java"
}
```

---

## Dataset Definition Format

Each dataset is described by a set of named fields. Supported fields:

- `generator` (string)  
  Short name of a MOA datastream generator supported by this tool (typically the class name without the trailing `Generator`).
- `classification_functions` (list[int])  
   One or more classification-function identifiers supported by the chosen generator. At least one value is required. Multiple values indicate concept drift between the listed functions.
- `drift_points` (list[int])  
   The sample indices at which consecutive concept drifts center (equivalent to the `-p` parameter for MOA `ConceptDriftStream`). Must contain exactly `len(classification_functions) - 1` entries.
- `drift_widths` (list[int])  
   Width (number of samples) over which each consecutive concept drift occurs (equivalent to the `-w` parameter for `ConceptDriftStream`). Must contain exactly `len(classification_functions) - 1` entries.
- `num_of_samples` (int)  
   Total number of samples to generate for this dataset.
  > Note: To check currently supported generators and the valid values for their classification functions, following code can be used:
  >
  > ```python
  > from moa_bulk_generator.dataset_defs import DatasetObject
  >
  > print(DatasetObject.GENERATORS)
  > ```
  >
  > Or call the module with `-l` parameter:
  >
  > ```bash
  > python -m moa_bulk_generator -l
  > ```

### Dataset String Definition

Multiple dataset definitions can be stored inside a text file — one dataset per line.  
Each dataset is encoded as an underscore (`_`)-separated token sequence. The **first** token is the generator name (short form, e.g. `Agrawal` → `AgrawalGenerator`). All remaining tokens come in key/value groups. Keys are single characters and identify a parameter, values for a key follow immediately and continue until the next key or the end of the line.

Supported keys:

- `classification_functions` -> `f`
- `drift_points` -> `p`
- `drift_widths` -> `w`
- `num_of_samples` -> `s`
  Values after a given keyword and before the next keyword represent the target values for a given parameter.

#### Example dataset definition:

```
Agrawal_f_1_2_3_p_500_1500_w_200_1_s_2000
```

> Note: This string will result in a dataset containing 2000 samples, generated with generators.AgrawalGenerator MOA datastream. It will contain two concept drift, first from function `1` to function `2`, centered around sample `500` and occuring over `200` samples(sample 400 to sample 600). The second concept drift will change the classification function from `2` to `3` exactly on sample `1500`(since the width is `1`)

In cases when the dataset should have no concept drifts, the `p` and `w` keywords should be omitted:

```
Agrawal_f_1_s_2000
```

> Note: It's possible to validate the string definitions without generating them:
>
> ```python
> datasets, errors = MOABulkGenerator.validate_datasets("datasets.txt")
> print('Valid datasets:')
> for dataset in datasets:
>    print(f'\t {dataset.to_string()}')
> print('Errors:')
> for error in errors:
>    print(f'\t {error}')
> ```
>
> Or call the module with `--validate` parameter:
>
> ```bash
> python -m moa_bulk_generator --validate datasets.txt
> ```

It is also possible to load datasets from json file:

```json
[
  {
    "generator": "STAGGER",
    "classification_functions": [1],
    "num_of_samples": 100
  },
  {
    "generator": "Agrawal",
    "classification_functions": [1, 2],
    "num_of_samples": 1000,
    "drift_points": [100],
    "drift_widths": [1]
  }
]
```

---

## Switching Concept Drift

This tool supports a _label-switching_ variant of concept drift: the underlying classification function stays the same while the _label assignment_ is changed by applying a mapping to all labels at a drift point.

**How to declare it**  
A switching drift is declared by repeating the same `classification_functions` value for consecutive positions. Example:

```
Agrawal_f_1_1_p_500_w_200_s_1000
```

That means: the classification function remains `1` before and after the drift, but at the drift point the labels are remapped according to a randomly generated mapping.

You can mix switching drifts with ordinary function changes:

```
Agrawal_f_1_1_2_p_500_1500_w_200_1_s_2000
```

> Note: the tool generates a random bijective mapping over the label set at each switching-drift occurrence. For multiclass datasets, mappings are not guaranteed to be identical across separate runs even when using the same switching-drift specification.

---

## Project Structure

```
moa_bulk_generator/
├── generator.py                     # Implementation of MoaBulkGenerator
├── __main__.py                      # Handles calling the module with `python -m moa_bulk_generator`
├── log.txt                          # Log file containing all command calls and errors
├───dataset_defs
│   ├── dataset_object.py            # Loads, parses, and validates dataset definitions
│   └── types.py                     # Custom types related to dataset definitions
├───input_handling
│   ├── file_input_handler.py        # Loads dataset definitions from a file
│   ├── interactive_input_handler.py # Implements CLI for interactive mode
│   ├── types.py                     # Custom types related to user interaction
│   └── utils.py                     # Helper functions for user interaction
├───moa_handling
    ├──moa_handler.py                # Builds and executes MOA command calls
    └──utils.py                      # Helper functions for MOA handling
```

---

## Planned Features

- Load datasets from `.json` files.
- Allow passing dataset definitions at runtime (as strings, dictionaries, or `DatasetObject` instances).
- Add support for additional MOA datastreams.
- Add support for `ConceptDriftRealStream`.
