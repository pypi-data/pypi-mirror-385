# dive_deco_py

> **⚠️ Work in Progress**: This project is currently under active development and represents an ongoing effort to create Python bindings for the [dive-deco](https://github.com/the-emerald/dive-deco) Rust library. The API may change, and some features may be incomplete or experimental. Use with caution and please report any issues you encounter.

A high-performance Python library for dive decompression calculations using the Bühlmann decompression algorithm. Built with Rust for speed and safety, with Python bindings via PyO3.

This library provides Python bindings for the [dive-deco](https://github.com/the-emerald/dive-deco) Rust library, bringing high-performance decompression calculations to Python.

## Features

- **Bühlmann Decompression Model**: Industry-standard ZH-L16 algorithm implementation
- **Gradient Factors Support**: Configurable GF-Low/GF-High for conservative dive planning
- **Multi-Gas Decompression**: Plan dives with multiple gas mixes (air, nitrox, trimix, oxygen)
- **Tissue Compartment Analysis**: Access to all 16 tissue compartments with detailed saturation data
- **Fast Performance**: Rust-powered core for efficient calculations
- **Type Safety**: Full type hints and stub files for excellent IDE support

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd dive_deco_py

# Build the library
./build.sh

# Install in development mode
pip install -e .
```

### Requirements

- Python 3.7+
- Rust toolchain (for building from source)
- Optional: matplotlib, numpy (for running examples)

## Quick Start

```python
from dive_deco_py import BuhlmannModel, Gas

# Create a Bühlmann model with default GF 30/70
model = BuhlmannModel()

# Define your breathing gas (21% O2, 0% He = Air)
air = Gas(0.21, 0.0)

# Record a dive segment: 30 minutes at 40 meters on air
model.record(40, 30, air)

# Get the decompression ceiling
ceiling = model.ceiling()
print(f"Ceiling depth: {ceiling}m")

# Calculate decompression schedule
deco = model.deco([air])
print(f"Total Time to Surface: {deco.tts:.1f} minutes")
```

## Core API

### BuhlmannModel

The main decompression model class.

```python
# Create with default GF 30/70
model = BuhlmannModel()

# Create with custom gradient factors
model = BuhlmannModel(gf_low=0.35, gf_high=0.75)
```

#### Methods

- **`record(depth: float, time: float, gas: Gas)`**: Record a dive segment at a specific depth with a gas mix
- **`ceiling() -> float`**: Get the current decompression ceiling depth in meters
- **`tissues() -> list[Tissue]`**: Get detailed information about all 16 tissue compartments
- **`supersaturation() -> Supersaturation`**: Get supersaturation data (GF99, GF at surface)
- **`deco(gases: list[Gas]) -> DecoSchedule`**: Calculate decompression schedule with available gases

### Gas

Represents a breathing gas mixture.

```python
# Air (21% O2, 0% He)
air = Gas(0.21, 0.0)

# EAN50 (50% O2, 0% He)
ean50 = Gas(0.50, 0.0)

# Pure Oxygen
oxygen = Gas(1.0, 0.0)

# Trimix 18/45 (18% O2, 45% He)
trimix = Gas(0.18, 0.45)
```

### Tissue

Tissue compartment data structure with the following properties:

- **`no`**: Compartment number (1-16)
- **`n2_ip`**: Nitrogen inert pressure (bar)
- **`he_ip`**: Helium inert pressure (bar)
- **`total_ip`**: Total inert gas pressure (bar)
- **`m_value_calc`**: Calculated M-value with gradient factors applied (bar)

### DecoSchedule

Decompression schedule information:

- **`tts`**: Time to surface in minutes
- **`tts_at_5`**: Time to surface if you stay 5 more minutes at current depth
- **`tts_delta_at_5`**: Delta between TTS and TTS+5 (penalty for staying longer)

### Supersaturation

Current supersaturation state:

- **`gf_99`**: GF99 - gradient factor at 99th percentile tissue
- **`gf_surf`**: Gradient factor if surfaced immediately

## Examples

### Basic Dive with Decompression

```python
from dive_deco_py import BuhlmannModel, Gas

model = BuhlmannModel()
air = Gas(0.21, 0.0)

# 30 minute dive at 40 meters
model.record(40, 30, air)

# Check ceiling
ceiling = model.ceiling()
print(f"Decompression ceiling: {ceiling}m")

# Get supersaturation
ss = model.supersaturation()
print(f"GF99: {ss.gf_99:.1f}%")
print(f"GF at surface: {ss.gf_surf:.1f}%")
```

### Multi-Gas Decompression Planning

```python
from dive_deco_py import BuhlmannModel, Gas

# Define gas mixes
air = Gas(0.21, 0.0)
ean50 = Gas(0.50, 0.0)
oxygen = Gas(1.0, 0.0)

model = BuhlmannModel()
model.record(40, 30, air)

# Compare decompression times with different gas strategies
deco_air = model.deco([air])
deco_nitrox = model.deco([air, ean50])
deco_full = model.deco([air, ean50, oxygen])

print(f"Air only TTS: {deco_air.tts:.1f} min")
print(f"Air + EAN50 TTS: {deco_nitrox.tts:.1f} min")
print(f"Air + EAN50 + O2 TTS: {deco_full.tts:.1f} min")
```

### Tissue Compartment Analysis

```python
from dive_deco_py import BuhlmannModel, Gas

model = BuhlmannModel()
air = Gas(0.21, 0.0)
model.record(40, 30, air)

# Analyze tissue saturation
tissues = model.tissues()
for tissue in tissues:
    saturation = (tissue.total_ip / tissue.m_value_calc) * 100
    print(f"Compartment {tissue.no}: {saturation:.1f}% saturated")
```

### Running the Examples

The `examples/` directory contains full working examples with visualization:

```bash
# Tissue saturation visualization
python examples/tissues_example.py

# Multi-gas decompression comparison
python examples/deco_gas_mix_example.py

# Basic Bühlmann model usage
python examples/buhlmann_example.py

# Time checking example
python examples/time_check_example.py
```

All examples save their output plots to `examples/out/`.

#### Example Visualizations

**Tissue Saturation Analysis**

![Tissue Saturation](examples/out/tissue_saturation.png)

The tissue saturation example visualizes:
- Inert gas pressures (N2 and He) across all 16 tissue compartments
- Saturation percentages after bottom time
- Saturation at the decompression ceiling depth
- M-values with gradient factors applied

**Multi-Gas Decompression Comparison**

![Decompression Comparison](examples/out/deco_comparison.png)

The decompression comparison example shows:
- Time-to-surface (TTS) for different gas configurations
- Impact of using nitrox and oxygen for decompression
- TTS+5 calculations (if you stay 5 minutes longer)

## Building from Source

```bash
# Make sure you have Rust installed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build the library
./build.sh

# Or manually with maturin
pip install maturin
maturin develop --release
```

## Project Structure

```
dive_deco_py/
├── src/                    # Rust source code
│   ├── lib.rs             # PyO3 Python bindings
│   ├── buhlmann_model.rs  # Bühlmann algorithm implementation
│   ├── compartment.rs     # Tissue compartment logic
│   ├── deco.rs            # Decompression calculations
│   └── gas.rs             # Gas mixture handling
├── examples/              # Python usage examples
│   ├── buhlmann_example.py
│   ├── deco_gas_mix_example.py
│   ├── tissues_example.py
│   ├── time_check_example.py
│   └── out/              # Example output directory
├── dive_deco_py.pyi      # Python type stubs
├── Cargo.toml            # Rust dependencies
├── pyproject.toml        # Python project config
└── build.sh              # Build script
```

## Safety Notice

⚠️ **IMPORTANT**: This library is for educational and planning purposes only. 

- Always dive with proper training and certification
- Use proper dive computers and tables as primary references
- Never rely solely on software for dive planning
- Consult with diving professionals for safety
- No warranty is provided - use at your own risk

Decompression diving is dangerous and requires specialized training. This software should never be used as the primary means of dive planning for actual dives.

## Algorithm Details

This library implements the Bühlmann ZH-L16 decompression algorithm with:

- 16 tissue compartments with different half-times
- Gradient Factors (GF) for conservatism control
- Support for both nitrogen and helium inert gases
- Configurable surface pressure and other parameters

Built on top of the [dive-deco](https://crates.io/crates/dive-deco) Rust crate (v6.0.4), which provides the core decompression algorithm implementation.

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Author

[Add your name/contact here]
