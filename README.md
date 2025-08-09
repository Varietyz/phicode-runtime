# PHICODE Runtime Engine

Run φ code directly in Python — a runtime and import system that lets you write and execute PHICODE, a symbolic variant of Python using concise, expressive glyphs.

---

## Overview

PHICODE Runtime Engine (`phicode`) is a Python runtime and import hook designed to run source files written in PHICODE — a symbolic shorthand for Python where keywords and built-in functions are replaced by visually compact Unicode glyphs. This enables writing code in a fresh, expressive style while seamlessly executing it via Python.

PHICODE is not a separate language but a symbolic encoding mapped one-to-one with Python syntax and semantics. Your `.φ` source files decode dynamically into valid Python on import or execution.

---

## Features

- Transparent import of PHICODE `.φ` modules and packages.
- Command-line runner that executes PHICODE modules or files.
- Bidirectional mapping between PHICODE symbols and Python keywords.
- Uses Python's import system (`sys.meta_path`) to enable natural `import` statements for PHICODE files.
- Compatible with Python 3.8+.

---

## Installation

```bash
pip install phicode
```

Or clone the repo and install in editable mode for development:

```bash
git clone https://github.com/Varietyz/pip-phicode
cd phicode
pip install -e .
```

---

## Usage

### Run a PHICODE file or module

```bash
phicode path/to/script.φ
```

or

```bash
phicode module_name
```

* If a file path is provided, it runs that PHICODE `.φ` file.
* If a module name is provided, it looks for the module in the current working directory and runs it.
* Default module is `main` if no argument is given.

### Import PHICODE modules from Python

Inside your Python code, after installing the PHICODE importer, you can import `.φ` files as modules:

```python
from phicode_engine.core.phicode_importer import install_phicode_importer

install_phicode_importer("/path/to/phicode_sources")

import your_phicode_module  # resolves your_phicode_module.φ
```

---

## PHICODE Symbol Mapping

PHICODE replaces many Python keywords and built-ins with single Unicode glyphs for compactness:

| Python Keyword | PHICODE Symbol | Python Keyword | PHICODE Symbol |
| -------------- | -------------- | -------------- | -------------- |
| False          | ⊥              | from           | ←              |
| None           | Ø              | global         | ⟁              |
| True           | ✓              | if             | ¿              |
| and            | ∧              | import         | ⇒              |
| as             | ↦              | in             | ∈              |
| assert         | ‼              | is             | ≡              |
| async          | ⟳              | lambda         | λ              |
| await          | ⌛              | nonlocal       | ∇              |
| break          | ⇲              | not            | ¬              |
| class          | ℂ              | or             | ∨              |
| continue       | ⇉              | pass           | ⋯              |
| def            | ƒ              | raise          | ↑              |
| del            | ∂              | return         | ⟲              |
| elif           | ⤷              | try            | ∴              |
| else           | ⋄              | while          | ↻              |
| except         | ⛒              | with           | ∥              |
| finally        | ⇗              | yield          | ⟰              |
| for            | ∀              | print          | π              |

---

## Architecture

* **PHICODE Loader and Finder:** Implements Python import hooks (`sys.meta_path`) to locate `.φ` files and decode them to Python source on-the-fly.
* **Symbolic Mapping:** Two-way dictionary translating PHICODE glyphs to Python keywords and vice versa.
* **Runtime Runner (`phicode` CLI):** Parses command line, determines file or module, installs the importer, and executes the target.
* **Package layout:** Source code is under `src/phicode_engine/` for clean separation.

---

## Contributing

Contributions and ideas are welcome! Please open issues or pull requests.

---

## License

This project is licensed under the terms found in the [LICENSE](LICENSE) file.

---

## Contact

Jay Baleine — [jay@banes-lab.com](mailto:jay@banes-lab.com)
