# ExpView

> ⚠️ Currently under active development.

## Overview

**ExpView** is a terminal-based analytics and visualization tool inspired by Excel.  
Designed for developers and data scientists, it displays pandas DataFrames directly in the terminal using the **Curses** library — with fast navigation, shortcut keys, and instant refresh.

ExpView can integrate with experiment pipelines: pass variable configurations to external programs, collect CSV/TSV/JSON outputs, manage configurations, and visualize results with matplotlib to analyze parameter effects and performance trends.

---

## Installation

```bash
pip install expview
````

This installs ExpView and its dependencies.

---

## Quick Start

To open a dataset, run:

```bash
expview data.csv
```

If you have multiple datasets in a folder, just run:

```bash
expview
```

---

## Using ExpView to Generate Experiment Results

Example usage:

```python
# my_experiment.py
import random
from expview import experiment, cli

@experiment
def my_experiment(run_args, exp_vars, results):
    """Example experiment function."""
    print(f"--- Experiment {run_args['expid']} ---")
    for k, v in exp_vars.items():
        print(f"{k}: {v}")
    results["accuracy"] = round(random.uniform(0.4, 0.99), 2)
    print("accuracy:", results["accuracy"])

if __name__ == "__main__":
    cli()
```

Then call your program like this:

```bash
python my_experiment.py run --var1=val1/val2 --var2=val1/val2
```

This runs the experiment with all combinations of input variables and creates four test results in `logs` directory.
For full documentation, refer to the [GitHub homepage](https://github.com/puraminy/expview).

---

## Exploring Results

Run `expview` inside the experiment or `logs` directory or any subdirectory containing the result files.  
ExpView merges the files and displays results in a navigable terminal table:

```bash
expview
```

---

## Plotting

ExpView supports interactive plotting. Example workflow:

1. Select a column as **x-axis** (`Shift + X`)
2. Select another column as **y-axis** (`Shift + Y`)
3. Optionally, select a column for **legend** (`Shift + T`)
4. Open the command prompt (`:`) and type `line` to generate a plot.

For full documentation, visit [the GitHub repository](https://github.com/puraminy/expview).

---

## License

MIT License © 2025 Ahmad Pouramini

```

