# SUND toolbox

<img src="https://gitlab.liu.se/ISBgroup/projects/sund/-/raw/main/logo/SUND_logo.png"
     alt="SUND logo"
     style="max-height:300px;width:100%;width:auto;display:block;margin:0 auto 1rem;" />

SUND (Simulation Using Nonlinear Dynamic models) is a Python package for high‑level, object‑oriented modeling and fast simulation of ODE/DAE systems with complex time‑dependent inputs and hierarchical model structures. Models compile against a SUNDIALS backend for performance and can be seamlessly connected by declaring inputs and outputs.

Supported Python: 3.10–3.14 on Linux (x86_64), Windows (x86_64) and macOS (Intel & ARM).

## Requirements

A C++ compiler (GCC, Clang, or MSVC) is required to install SUND and to compile models for efficient simulations. Pre-built wheels are not provided, as model compilation is performed locally. Ensure your system has a working C++ compiler before installing.

## Install

Install using `pip` or `uv` (requires compiler):

```bash
pip install sund   # or: uv add sund
```

## Quick start

Minimal end‑to‑end example:

```python
import sund

# 1. Generate a template model file
sund.save_model_template("example_model.txt", model_name="Example")

# 2. Install (compiles → C extension module under sund/models)
sund.install_model("example_model.txt")

# 3. Load an instance
model = sund.load_model("Example")

# 4. Simulate (time vector in model time unit; default from template is 's')
sim = sund.Simulation(models=[model], time_vector=[0, 1, 2, 3], time_unit=model.time_unit)
sim.simulate()

# 5. Get the results as a dict and print
print(sim.features_as_dict())
```

See the docs for activities (time‑varying inputs), multiple models, events, validation.

## Documentation

Full user & API docs: <https://isbgroup.eu/sund-toolbox> (versioned; latest alias always points to newest release).

## Model validation (optional)

Validate a model file or content before installing:

```python
import sund
results = sund.validate_model_file("example_model.txt", verbose=True)
```

## Citation

If you use SUND in academic work, please cite the project (formal citation text will be added once available).

## Getting help

Open an issue or start a discussion on the project GitLab. Bug reports with a minimal reproducer and model snippet are appreciated.
