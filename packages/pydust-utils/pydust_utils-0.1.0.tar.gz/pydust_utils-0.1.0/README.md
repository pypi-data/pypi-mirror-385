# PyDUST

Python library for parsing and analyzing DUST post-processing output files.

## Installation

**Requirements:** SSH key configured with GitLab

Install directly from the GitLab repository:

```bash
# Install latest from pydust branch
pip install git+ssh://git@gitlab.com/Alecocco.1994/dust-private.git@pydust#subdirectory=pydust

# Or install specific commit
pip install git+ssh://git@gitlab.com/Alecocco.1994/dust-private.git@abc1234#subdirectory=pydust
```

## Development Installation

For development with editable mode:

```bash
git clone git@gitlab.com:Alecocco.1994/dust-private.git
git checkout pydust
cd dust-private/pydust
pip install -e ".[dev,docs]"
```

## Quick Start

```python
from pydust import read_sectional, read_probes, read_integral

# Read sectional loads
sectional_data = read_sectional('sectional_loads.dat')
print(sectional_data.sec.shape)  # (n_time, n_sec)

# Read probe velocities
probe_data = read_probes('probes_velocity.dat')
print(probe_data.velocities.shape)  # (n_time, n_probes, 3)

# Read integral loads
integral_data = read_integral('integral_loads.dat')
lift = integral_data.forces[:, 2]  # Extract lift force
```

## Available Parsers

- `read_sectional` - Sectional aerodynamic loads
- `read_probes` - Velocity probe data
- `read_chordwise` - Chordwise distributions
- `read_integral` - Integral loads
- `read_hinge` - Hinge loads

## Documentation

Build documentation locally:

```bash
cd pydust_utils
source .venv-docs/bin/activate
sphinx-build -b html docs/source docs/build/html
```

## Running Tests

```bash
cd pydust_utils
pip install -e ".[dev]"
pytest tests/
```

## Build 
```bash
pip install build 
python -m build 
pip install twine 
```

## License

MIT License

---

**Note:** This is a private package for DUST team members. Ensure you have SSH access configured with GitLab before installation.
