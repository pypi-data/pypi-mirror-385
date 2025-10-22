# herrkunft

**From German "Herkunft" (origin, provenance)**

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pgierz/herrkunft/main?labpath=docs%2Fnotebooks)

Track configuration value origins and modification history through YAML parsing with modern Python best practices.

## Overview

`herrkunft` is a standalone library extracted from [esm_tools](https://github.com/esm-tools/esm_tools) that provides transparent provenance tracking for configuration values loaded from YAML files. It tracks:

- **Where** each value came from (file path, line number, column)
- **When** it was set or modified
- **How** conflicts were resolved using hierarchical categories
- **What** the complete modification history is

Perfect for scientific computing, workflow configuration, and any application where configuration traceability matters.

## Features

- 🎯 **Transparent Tracking**: Values behave like normal Python types while tracking their provenance
- 📍 **Precise Location**: Track exact file, line, and column for every configuration value
- 🏗️ **Hierarchical Resolution**: Category-based conflict resolution (e.g., defaults < user < runtime)
- 🔄 **Modification History**: Complete audit trail of all changes to configuration values
- 🎨 **Type-Safe**: Full type hints and Pydantic validation throughout
- 📝 **YAML Round-Trip**: Preserve provenance as comments when writing YAML
- 🚀 **Modern Python**: Built with Pydantic 2.0, ruamel.yaml, and loguru
- 📓 **Interactive Docs**: Try it in Binder without installing anything

## Try It Now

Launch interactive notebooks in your browser (no installation required):

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pgierz/herrkunft/main?labpath=docs%2Fnotebooks)

## Installation

```bash
pip install herrkunft
```

For development:

```bash
pip install herrkunft[dev]
```

## Quick Start

```python
from provenance import load_yaml

# Load a configuration file with provenance tracking
config = load_yaml("config.yaml", category="defaults")

# Access values normally
database_url = config["database"]["url"]
print(database_url)  # postgresql://localhost/mydb

# Access provenance information
print(database_url.provenance.current.yaml_file)  # config.yaml
print(database_url.provenance.current.line)       # 15
print(database_url.provenance.current.column)     # 8
```

### Hierarchical Configuration

```python
from provenance import ProvenanceLoader

# Set up hierarchy: defaults < user < production
loader = ProvenanceLoader()

# Load multiple configs with different priorities
defaults = loader.load("defaults.yaml", category="defaults")
user_config = loader.load("user.yaml", category="user")
prod_config = loader.load("production.yaml", category="production")

# Merge with automatic conflict resolution
from provenance import HierarchyManager

hierarchy = HierarchyManager(["defaults", "user", "production"])
final_config = hierarchy.merge(defaults, user_config, prod_config)

# Production values override user values, which override defaults
# Full history is preserved in provenance
```

### Save with Provenance Comments

```python
from provenance import dump_yaml

# Save configuration with provenance as inline comments
dump_yaml(config, "output.yaml", include_provenance=True)
```

Output:

```yaml
database:
  url: postgresql://localhost/mydb  # config.yaml:15:8
  port: 5432  # config.yaml:16:8
```

## Architecture

herrkunft is built with modern Python best practices:

- **Pydantic 2.0**: Type-safe data models and settings
- **ruamel.yaml**: YAML parsing with position tracking and comment preservation
- **loguru**: Simple, powerful logging
- **Type hints**: Full typing support for IDE autocomplete and type checking

### Core Components

```
herrkunft/
├── core/           # Provenance tracking and hierarchy management
├── types/          # Type wrappers (DictWithProvenance, etc.)
├── yaml/           # YAML loading and dumping
├── utils/          # Utilities for cleaning, validation, serialization
└── config/         # Library configuration and settings
```

## Use Cases

### Scientific Computing

Track which configuration file and parameters were used for each simulation run:

```python
config = load_yaml("simulation.yaml")
run_simulation(config)

# Later, audit which file provided each parameter
for key, value in config.items():
    print(f"{key}: {value.provenance.current.yaml_file}")
```

### Multi-Environment Configuration

Manage development, staging, and production configs with clear conflict resolution:

```python
loader = ProvenanceLoader()
config = loader.load_multiple([
    ("defaults.yaml", "defaults"),
    ("production.yaml", "production"),
    ("secrets.yaml", "secrets"),  # Highest priority
])
```

### Configuration Auditing

Export complete provenance history for compliance or debugging:

```python
from provenance import to_json

# Export config with full provenance metadata
to_json_file(config, "audit.json")
```

## Documentation

Full documentation is available at [https://herrkunft.readthedocs.io](https://herrkunft.readthedocs.io)

- [Getting Started Guide](https://herrkunft.readthedocs.io/getting-started)
- [API Reference](https://herrkunft.readthedocs.io/api)
- [Architecture Overview](https://herrkunft.readthedocs.io/architecture)
- [Migration from esm_tools](https://herrkunft.readthedocs.io/migration)

## Development

### Setup

```bash
git clone https://github.com/pgierz/herrkunft.git
cd herrkunft
pip install -e .[dev]
```

### Testing

```bash
pytest                          # Run all tests
pytest --cov=provenance        # With coverage
pytest -v tests/test_core/     # Specific test directory
```

### Code Quality

```bash
black provenance tests          # Format code
ruff provenance tests           # Lint
mypy provenance                 # Type check
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Authors

- **Paul Gierz** - [paul.gierz@awi.de](mailto:paul.gierz@awi.de)
- **Miguel Andrés-Martínez** - [miguel.andres-martinez@awi.de](mailto:miguel.andres-martinez@awi.de)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Extracted from the [esm_tools](https://github.com/esm-tools/esm_tools) project, which provides workflow management for Earth System Models. The provenance tracking feature was originally developed to track configuration origins in complex HPC simulation workflows.

## Related Projects

- [esm_tools](https://github.com/esm-tools/esm_tools) - Earth System Model workflow management
- [OmegaConf](https://omegaconf.readthedocs.io/) - Hierarchical configuration (no provenance tracking)
- [Dynaconf](https://www.dynaconf.com/) - Settings management (no provenance tracking)
- [Hydra](https://hydra.cc/) - Configuration framework (no detailed provenance)

## Citation

If you use herrkunft in your research, please cite:

```bibtex
@software{herrkunft2024,
  title = {herrkunft: Configuration Provenance Tracking for Python},
  author = {Gierz, Paul and Andrés-Martínez, Miguel},
  year = {2024},
  url = {https://github.com/pgierz/herrkunft}
}
```
