# ExpView

> ⚠️ Currently under active development.

## Overview

**ExpView** is a terminal-based analytics and visualization tool inspired by Excel. Designed for developers and data scientists, it displays pandas DataFrames directly in the terminal using the Curses library, with fast navigation, shortcut keys, and instant refresh.

ExpView can integrate with experiment pipelines: pass variable configurations to external programs, collect CSV/TSV/JSON outputs, manage configs, and visualize results with matplotlib to analyze parameter effects and performance trends.

## Installation

```bash
pip install expview
```

This installs ExpView and its dependencies.

## Quick Start

Example usage:

```python
import random
from expview import experiment, cli

@experiment
def dummy_experiment(run_args, exp_vars, results):
    """Example experiment function."""
    print(f"--- Experiment {run_args['expid']} ---")
    for k, v in exp_vars.items():
        print(f"{k}: {v}")
    results["accuracy"] = round(random.uniform(0.4, 0.99), 2)
    print("accuracy:", results["accuracy"])

if __name__ == "__main__":
    cli()
```

## Exploring Results

Run `expview` inside a `logs` directory or any subdirectory containing CSV, TSV, or JSON files. ExpView merges the files and displays results in a navigable terminal table:

```bash
expview
```

## Plotting

ExpView supports interactive plotting. Example workflow:

1. Select a column as **x-axis** (Shift + X).
2. Select another column as **y-axis** (Shift + Y).
3. Optionally, select a column for **legend** (Shift + T).
4. Open the command prompt (`:`) and type `line` to generate a plot.

---
