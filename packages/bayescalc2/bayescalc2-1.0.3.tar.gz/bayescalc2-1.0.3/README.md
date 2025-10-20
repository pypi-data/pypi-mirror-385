# BayesCalc2: A Bayesian Network Calculator

| Category | Link |
|----------|--------|
|**Package**|[![PyPI version](https://img.shields.io/pypi/v/bayescalc2.svg)](https://pypi.org/project/bayescalc2/) [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)|
|**Documentation**|[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://johan162.github.io/bayescalc2/)|
|**License**|[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)|
|**Release**|[![GitHub release](https://img.shields.io/github/v/release/johan162/bayescalc2?include_prereleases)](https://github.com/johan162/bayescalc2/releases)|
|**CI/CD**|[![CI](https://github.com/johan162/bayescalc2/actions/workflows/ci.yml/badge.svg)](https://github.com/johan162/bayescalc2/actions/workflows/ci.yml) [![Doc build](https://github.com/johan162/bayescalc2/actions/workflows/docs.yml/badge.svg)](https://github.com/johan162/bayescalc2/actions/workflows/docs.yml) [![Coverage](https://img.shields.io/badge/coverage-83%25-green)](coverage.svg)|
|**Code Quality**|[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/) [![Linting: flake8](https://img.shields.io/badge/linting-flake8-yellowgreen)](https://flake8.pycqa.org/)|
|Repo URL|[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat-square&logo=github&logoColor=white)](https://github.com/johan162/bayescalc2)|




## Overview

A Bayesian network calculator designed for learning probabilistic reasoning using Bayesian networks. This tool allows you to define Bayesian networks, calculate probabilities, and perform various probabilistic operations using an efficient variable-elimination algorithm that scales well with network complexity.

## Features

- **Efficient Inference**: Uses variable elimination algorithm instead of exponentially-growing joint probability tables
- **Interactive REPL**: Command-line interface with tab completion and command history
- **Batch Processing**: Execute multiple queries from files or command strings
- **Rich Query Language**: Support for conditional probabilities, arithmetic expressions, and independence tests
- **Information Theory**: Built-in entropy, mutual information, and conditional entropy calculations
- **Network Analysis**: Graph structure analysis with parent/child relationships
- **Network Visualization**: Generate network diagrams with CPT tables (PDF, PNG, SVG)
- **Educational Focus**: Clear output formatting ideal for learning and teaching

## Installation

### Requirements

- Python 3.10 or higher
- NumPy >= 2.3.3
- prompt_toolkit >= 3.0.0
- graphviz >= 0.20.0 (for visualization)

### Install from PyPI

```bash
pip install bayescalc2
```

For visualization support install the `graphviz` system package:

```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Fedora/Redhat
sudo dnf install graphviz

# Windows
# Download from https://graphviz.org/download/
```

### Install from Source

```bash
git clone https://github.com/johan162/bayescalc2.git
cd bayescalc2
pip install -e .
```

## Quick Start

```bash
# Download an example network
wget https://raw.githubusercontent.com/johan162/bayescalc2/main/examples/rain_sprinkler_grass.net

# Launch interactive mode
bayescalc rain_sprinkler_grass.net

# Try some queries
>> P(Rain)
>> P(Rain|GrassWet=True)
>> entropy(Rain)
>> exit
```

## Usage

BayesCalc2 can be used in two modes:

### 1. Interactive Mode

```bash
bayescalc network_file.net
```

This launches an interactive REPL where you can enter probability queries and commands.

### 2. Batch Mode

```bash
bayescalc network_file.net --batch commands.txt
```

or

```bash
bayescalc network_file.net --cmd "P(Rain|GrassWet=Yes);printCPT(Rain)"
```

## Network File Format

Create a Bayesian network definition in a .net file:

```
# Example network definition
boolean Rain
variable Sprinkler {On, Off}
variable GrassWet {Yes, No}

# CPT definitions
Rain {
    P(True) = 0.2
    # P(False) will be auto-filled
}

Sprinkler | Rain {
    P(On | True) = 0.01
    P(On | False) = 0.4
    # P(Off | parent) auto-filled
}

GrassWet | Rain, Sprinkler {
    P(Yes | True, On) = 0.99
    P(Yes | True, Off) = 0.8
    P(Yes | False, On) = 0.9
    # Remaining CPTs auto-completed
}
```

## Available Commands

### Probability Queries
- `P(A)` - Marginal probability
- `P(A|B)` - Conditional probability  
- `P(A,B|C)` - Joint conditional probability
- `P(A|B)*P(B)/P(A)` - Arithmetic expressions

### Network Analysis
- `printCPT(X)` - Display conditional probability table
- `printJPT()` - Display joint probability table
- `parents(X)` - Show parent variables
- `children(X)` - Show child variables
- `showGraph()` - Display network structure
- `visualize(file.pdf)` - Generate network visualization with CPT tables
- `load(file.net)` - Load a different network file

### Independence Testing
- `isindependent(A,B)` - Test marginal independence
- `iscondindependent(A,B|C)` - Test conditional independence

### Information Theory
- `entropy(X)` - Shannon entropy
- `conditional_entropy(X|Y)` - Conditional entropy
- `mutual_information(X,Y)` - Mutual information

### Visualization Examples

```bash
# Generate PDF with CPT tables
>> visualize(network.pdf)

# Generate PNG without CPT tables
>> visualize(simple_network.png, show_cpt=False)

# Generate SVG with horizontal layout
>> visualize(network.svg, rankdir=LR)
```

## Examples

The `examples/` directory contains various Bayesian networks demonstrating different use cases:

- `rain_sprinkler_grass.net` - Classic sprinkler example
- `medical_test.net` - The classical Medical diagnosis scenario 
- `student_network.net` - Academic performance model
- `asia_chest_clinic.net` - Medical expert system

## Use Cases

- **Education**: Teaching probabilistic reasoning and Bayesian networks
- **Research**: Prototyping and testing Bayesian models
- **Analysis**: Exploring conditional dependencies in data
- **Validation**: Verifying hand-calculated probability results

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change. 

### Development Setup

Please read the `docs/developer_guide.md` for specific information about architecture and code base and how to contribute.

```bash
git clone https://github.com/johan162/bayescalc2.git
cd bayescalc2
python -m venv venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"  # Quotes needed for zsh shell
python -m pytest tests/
```

## Documentation & Support

- **Documentation**: See the [online documentation](https://johan162.github.io/bayescalc2/) for both user and developer guides.
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/johan162/bayescalc2/issues)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## Citation

If you use BayesCalc2 in academic work, please cite:

```bibtex
@software{bayescalc2,
  title={BayesCalc2: A Bayesian Network Calculator},
  author={Johan Persson},
  year={2025},
  url={https://github.com/johan162/bayescalc2},
  version={v1.0.3}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.