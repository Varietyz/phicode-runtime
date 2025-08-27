<div align="center">

# [![Phicode](https://img.shields.io/badge/(φ)_Phicode_Runtime_Engine-v2.5.0-red.svg)](https://python.org)

<img src="https://banes-lab.com/assets/images/banes_lab/700px_Main_Animated.gif" width="100" alt="Banes Lab" />

**Python execution engine with daemons, caching and import extensions**

[![Python](https://img.shields.io/badge/Python-v3.8%2B-blue.svg)](https://python.org)
[![PyPy Supported](https://img.shields.io/badge/PyPy-Supported-green.svg)](https://pypy.org)
[![License](https://img.shields.io/badge/LICENSE-Non--Commercial-blue.svg)](https://banes-lab.com/licensing)

[![PyPI Package Version](https://img.shields.io/pypi/v/phicode.svg?label=PyPI+Package)](https://pypi.org/project/phicode/)
[![PyPI Monthly Downloads](https://img.shields.io/pypi/dw/phicode.svg?label=PyPI+Downloads)](https://pypi.org/project/phicode/)

[![VS Code Extension Version](https://img.shields.io/visual-studio-marketplace/v/Banes-Lab.phicode.svg?label=VS+Code+Extension)](https://marketplace.visualstudio.com/items?itemName=Banes-Lab.phicode)
[![VS Code Extension Installs](https://img.shields.io/visual-studio-marketplace/i/Banes-Lab.phicode.svg?label=VS+Code+Installs)](https://marketplace.visualstudio.com/items?itemName=Banes-Lab.phicode)


</div>

## Overview

Phicode Engine executes Python modules through an optimized runtime featuring robust and self-healing caching mechanisms, automatic interpreter optimization, and modified import system. It supports standard Python with optional custom syntax transpilation. The integrated Phiemon daemon system provides production-ready process management with crash recovery and multi-daemon support.

## Project Philosophy

*"I believe in architectural minimalism with deterministic reliability - every line of code must earn its place through measurable value, not feature-rich design patterns. I build systems that work predictably in production, not demonstrations of architectural sophistication. My approach is surgical: target the exact problem with minimal code, reuse existing components rather than building new ones, and resist feature bloat by consistently asking whether each addition truly serves the core purpose."* - Jay Baleine

---

## Navigation

* [Quick Start](#quick-start)
* [Architecture](#architecture)
* [Usage](#usage)
* [Configuration](#configuration)
* [Customize Syntax](#custom-syntax-support)
* [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# Install and run Python modules
pip install phicode
phicode my_module

# Use PyPy interpreter
phicode my_module --pypy

# Start HTTP API server
phicode --api-server
```

## Installation

### Standard Installation
```bash
pip install phicode
```

### With System Utilities
```bash
pip install phicode[utility]
```

### Development Installation
```bash
git clone https://github.com/Varietyz/phicode-engine
cd phicode-engine
pip install -e .
```

### Optional Security Components
```bash
phicode --security-install    # Install Phimmuno + PhiRust
phicode --security-status     # Check installation status
```

## Core Features

### Python Module Execution
Execute any Python module with caching:

```bash
phicode calculator              # Standard execution
phicode my_script --debug      # With debug logging  
phicode large_app --pypy       # Use PyPy interpreter
```

### Multi-Level Caching
Four distinct cache layers with automatic invalidation:
- **Source Cache**: Raw file contents with LRU eviction
- **Python Cache**: Processed code keyed by content hash
- **Spec Cache**: Import specifications with modification tracking
- **Bytecode Cache**: Compiled code with integrity validation

### HTTP API Server
JSON endpoints for remote execution:

```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"hello\")"}'
```

### Security Integration
Integration with Phimmuno and PhiRust components for threat detection using pattern matching algorithms.

### Custom Syntax Support (Optional)
The engine supports custom symbol mappings through `.φ` files. This feature is completely optional - the engine works with standard Python by default.

## Architecture

**Core Components:**
- `core.importing`: MetaPathFinder and Loader implementations
- `core.transpilation`: Text transformation using regex patterns  
- `core.cache`: Multi-level caching with LRU eviction
- `core.runtime`: Module execution and cleanup
- `core.interpreter`: Command-line interface and interpreter selection

**Additional Components:**
- `api`: HTTP endpoints with subprocess isolation
- `benchsuite`: Performance measurement tools
- `security`: Integration with optional threat detection
- `rust`: Optional acceleration components


## System Architecture

```mermaid
flowchart TB
    subgraph TopSystems [" "]
        direction LR
        Security["Security System<br/>Phimmuno Validator<br/>Threat Detection<br/>Bypass Modes"]
        Config["Configuration<br/>Symbol Mappings<br/>Custom Loading<br/>Validation & Conflicts"]
        BenchSuite["Benchmark Suite<br/>15+ Scenarios<br/>System Fingerprinting<br/>Performance Baseline<br/>Mermaid Visualization"]
        APIServer["HTTP API Server<br/>4 REST Endpoints<br/>Subprocess Isolation<br/>Code Execution Handler"]
        Installers["Binary Installers<br/>PhiRust & Phimmuno<br/>Download + Retry Logic<br/>Cargo Fallback"]
        RustBinaries["Rust Binaries<br/>phimmuno-engine<br/>phirust-transpiler<br/>Aho-Corasick Pattern Matching"]
        PhiemonDaemon["Phiemon Daemon<br/>Multi-Daemon Support<br/>Crash Recovery<br/>PID Tracking"]
    end
    
    Start([CLI Entry Point]) --> AutoImport[Auto Import Discovery]
    AutoImport --> Logger[Initialize Logger]
    Logger --> CLIParse[CLI Parser & Handlers]
    CLIParse --> EarlyExit{Early Exit?}
    
    EarlyExit -->|--version| Version[Version Info]
    EarlyExit -->|--list-interpreters| IntList[List Interpreters]
    EarlyExit -->|--help| Help[Help Display]
    EarlyExit -->|Commands| Route{Route Command}
    
    Version --> End([Complete])
    IntList --> End
    Help --> End
    
    Route -->|--benchmark| BenchSuite
    Route -->|--api-server| APIServer
    Route -->|--security-*| Security
    Route -->|--config-*| Config
    Route -->|--*-install| Installers
    Route -->|--phiemon| PhiemonDaemon
    Route -->|--phiemon-status| DaemonStatus[Show Daemon Status]
    Route -->|--phiemon-list| DaemonList[List All Daemons]
    Route -->|module_name| ProjectSetup[Project Setup & Discovery]
    
    DaemonStatus --> End
    DaemonList --> End
    
    ProjectSetup --> ProjRoot[Detect Project Root]
    ProjRoot --> AutoDiscover[Auto-Discover φ Directories]
    AutoDiscover --> Recommendations[Show Interpreter Recommendations]
    Recommendations --> ICheck{Interpreter Analysis}
    
    ICheck -->|Switch Needed| Switch[Interpreter Switch]
    ICheck -->|Current OK| ImportSetup[Import System Setup]
    Switch --> SubProc[Subprocess Execution]
    
    ImportSetup --> Dedup[Check Finder Deduplication]
    Dedup --> Finder[PhicodeFinder Registration]
    Finder --> ModuleResolve[Module Resolution Logic]
    ModuleResolve --> StdlibCheck{Stdlib Module?}
    StdlibCheck -->|Yes| SkipImport[Skip Import]
    StdlibCheck -->|No| Cache{Cache Check}
    
    Cache -->|Hit| CacheLoad[Load from Multi-Level Cache]
    Cache -->|Miss| FileRead[File Read with Memory Mapping]
    
    FileRead --> RetryLogic{File Read Failed?}
    RetryLogic -->|Retry| FileRead
    RetryLogic -->|Success| TransSystem[Transpilation System]
    
    subgraph TransSys [Advanced Transpilation Pipeline]
        SymLoad[Load Custom Symbol Config]
        SymValidate[Symbol Conflict Detection]
        SymOpt[Symbol Order Optimization]
        RegexFallback[Regex vs Standard Re Fallback]
        SymbolDetect[Unicode Symbol Detection]
        RustCheck{Size > 300KB?}
        RustTrans[Rust Transpiler via Binary]
        PyTrans[Python Pattern Matching]
        StringProtect[String Literal Protection]
        SecValidate[Multi-Stage Security Validation]
    end
    
    TransSystem --> TransSys
    SymLoad --> SymValidate
    SymValidate --> SymOpt
    SymOpt --> RegexFallback
    RegexFallback --> SymbolDetect
    SymbolDetect --> RustCheck
    RustCheck -->|Yes| RustTrans
    RustCheck -->|No| PyTrans
    RustTrans --> StringProtect
    PyTrans --> StringProtect
    StringProtect --> SecValidate
    
    SecValidate -->|Threat Detected| Block[Block Execution]
    SecValidate -->|Safe| Compile[AST Parse & Bytecode Compilation]
    
    Compile --> IntegrityCheck[Cache Integrity Validation]
    IntegrityCheck --> BatchCache[Queue Batch Cache Writes]
    BatchCache --> Execute[Module Execution]
    
    Execute --> ArgvMgmt[Argv Context Management]
    ArgvMgmt --> MainDetect[Main Module Detection]
    MainDetect --> SignalSetup[Signal Handler Setup]
    SignalSetup --> ModuleRun[Execute Module Code]
    ModuleRun --> PerfWarning{Slow Startup?}
    PerfWarning -->|Yes| WarnUser[Display Performance Warning]
    PerfWarning -->|No| Cleanup[Graceful Shutdown & Cleanup]
    WarnUser --> Cleanup
    
    Block --> SecurityError[Security Error Response]
    SecurityError --> Cleanup
    SubProc --> Cleanup
    SkipImport --> End
    
    Cleanup --> FlushBatch[Flush Batch Writes]
    FlushBatch --> CleanTemp[Clean Temp Files]
    CleanTemp --> RunHooks[Execute Shutdown Hooks]
    RunHooks --> End
    
    subgraph CacheSystem [Sophisticated Cache System]
        direction TB
        SC[Source Cache - LRU: 512<br/>Memory Mapping for Large Files]
        PC[Python Cache - xxHash/MD5 Keys<br/>Transpilation Results]
        SpC[Spec Cache - ModTime Tracking<br/>Import Specifications]
        BC[Bytecode Cache - SHA256 Validation<br/>Magic Number Verification<br/>Batch Write Queue]
        CacheOps[Advanced Cache Operations<br/>Retry Logic with Backoff<br/>Integrity Validation<br/>Canonical Path Caching]
    end
    
    subgraph InterpreterSys [Interpreter Management System]
        direction TB
        ISel[Interpreter Selection & Detection]
        IHints[Performance Hints & Analysis]
        ISwitch[Runtime Switching Logic]
        IAnalysis[C Extension Analysis]
        IDisplay[Version Display & Recommendations]
        IDedup[Path Deduplication]
    end
    
    subgraph RuntimeSys [Runtime Management System]
        direction TB
        ModExec[Module Executor]
        ArgvCtx[Argv Context Management]
        SignalH[Signal Handlers SIGINT/SIGTERM]
        ShutdownH[Shutdown Hook Registry]
        MainMod[Main Module Detection]
        PerfMon[Performance Monitoring]
    end
    
    subgraph ProcessSys [Process & Subprocess Management]
        direction TB
        SubHandler[Subprocess Handler]
        CodeExec[Isolated Code Execution]
        TimeoutMgmt[Timeout Management]
        ResultCapture[Output Capture & Processing]
    end
    
    subgraph DaemonSys [Phiemon Daemon System]
        direction TB
        MultiDaemon[Multi-Daemon Support with Per-Process State Files]
        DaemonLoop[Restart Loop with Backoff: 1s→2s→4s→8s→16s→30s max]
        PIDTrack[PID Tracking & Crash Detection]
        StatusMgmt[Status Management & Debugging]
    end
    
    Cache -.-> CacheSystem
    BatchCache -.-> CacheSystem
    ICheck -.-> InterpreterSys
    Switch -.-> InterpreterSys
    Execute -.-> RuntimeSys
    Cleanup -.-> RuntimeSys
    APIServer -.-> ProcessSys
    RustTrans -.-> RustBinaries
    SecValidate -.-> RustBinaries
    PhiemonDaemon -.-> DaemonSys
    
    style Start fill:#034a69
    style End fill:#3d5a1d
    style Block fill:#880014
    style SecurityError fill:#800013
    style BenchSuite fill:#582460
    style Security fill:#6f4500
    style CacheSystem fill:#245524
    style InterpreterSys fill:#826200
    style TransSys fill:#094a7b
    style RuntimeSys fill:#840f35
    style ProcessSys fill:#5f6512
    style RustBinaries fill:#826200
    style PhiemonDaemon fill:#6f2c00
    style DaemonSys fill:#6f2c00
```

## Configuration

### Environment Variables

**Runtime Settings:**
- `PHICODE_CACHE_SIZE`: LRU cache entry limits (default 512)
- `PHICODE_MMAP_THRESHOLD`: Memory-mapping file size threshold (default 8192)
- `PHICODE_BATCH_SIZE`: Bytecode write batch size (default 5)
- `RUST_SIZE_THRESHOLD`: Rust component activation threshold (default 300KB)

**Interpreter Selection:**
- `PHITON_PATH`: Custom CPython executable path
- `PHIPY_PATH`: Custom PyPy executable path (default pypy3)

### Import System Integration

The system inserts itself at position 0 in Python's `sys.meta_path`:

**PhicodeFinder**: Intercepts import statements, resolves files, maintains path cache  
**PhicodeLoader**: Reads source files, processes content, compiles bytecode, executes modules

## Performance Testing

Run the benchmark suite:

```bash
phicode --benchmark              # Interactive selection
phicode --benchmark --full       # Complete test suite
phicode --benchmark --json       # JSON output format
```

The benchmark suite measures cache behavior, transpilation speed, and system limits under various conditions.

## Command Reference

### Execution Commands
```bash
phicode <module>                    # Execute Python module
phicode <module> --debug            # Execute with debug output
phicode <module> --bypass           # Skip security validation
phicode <module> --pypy             # Use PyPy interpreter
```

### System Commands
```bash
phicode --version                   # Show version information
phicode --list-interpreters         # List available interpreters
phicode --api-server               # Start HTTP server
phicode --benchmark                # Run performance tests
phicode --config-generate           # Create configuration file
phicode --config-reset              # Reset to defaults
```

### HTTP Endpoints

| Endpoint | Method | Purpose |
|----------|---------|---------|
| `/execute` | POST | Execute code remotely |
| `/convert` | POST | Transform code syntax |
| `/info` | GET | Engine information |
| `/symbols` | GET | Available syntax mappings |

## Python Integration

```python
from phicode_engine import install_phicode_importer, transpile_symbols

# Enable custom file imports
install_phicode_importer("/path/to/files")

# Manual transpilation
result = transpile_symbols("ƒ test(): ⟲ 42")
# Returns: "def test(): return 42"
```

---

## Phiemon Process Management (Daemon Setup)

Start processes with automatic crash recovery and multi-daemon support:

```bash
phicode my_app --phiemon                    # Start as daemon
phicode my_app --phiemon --name myservice   # Custom name
phicode my_app --phiemon --max-restarts 10  # Restart limit
phicode --phiemon-status                    # Check all daemons
phicode --phiemon-status myservice          # Check specific daemon
```

**Phiemon Daemon Features:**
- **Multi-daemon support** with isolated state files per process
- **Automatic restart** on process crashes with configurable limits
- **Exponential backoff** prevents resource exhaustion (1s→2s→4s→8s→16s→30s max)
- **Per-daemon state persistence** through `phiemon_{name}.state` files
- **Process tracking** with PID monitoring and crash detection
- **Enhanced debugging** with detailed error logging and status reporting
- **Concurrent execution** of multiple services without conflicts

**Status Management:**
```bash
phicode --phiemon-status                    # List all active daemons
phicode --phiemon-status webapp             # Check specific daemon status
phicode --phiemon-list                      # Show daemon overview with uptimes
```

The daemon wraps standard PhiCode execution, maintaining all security scanning and caching behavior while providing production-ready process management. Each daemon operates independently with its own state tracking and restart logic.

---

# Custom Syntax Support

*Phicode Engine supports custom syntax through configurable symbol mappings. This feature is completely optional - the engine works with standard Python.*

## Setup

Generate configuration file:
```bash
phicode --config-generate
```

Creates `.(φ)/config.json` with customizable mappings:

```json
{
  "file_extension": ".φ",
  "symbols": {
    "def": "ƒ",
    "class": "ℂ", 
    "print": "π",
    "return": "⟲"
  }
}
```

## Usage Example

Create `example.φ` with custom syntax:
```python
ƒ factorial(n):
    ¿ n <= 1:
        ⟲ 1
    ⋄:
        ⟲ n * factorial(n-1)

π(factorial(5))
```

Execute normally:
```bash
phicode example
```

## Default Symbol Mappings

*Available default symbols for customization:*

### Control Flow
- `¿` → if, `⤷` → elif, `⋄` → else
- `∀` → for, `↻` → while  
- `⇲` → break, `⇉` → continue

### Functions & Classes
- `ƒ` → def, `ℂ` → class
- `⟳` → async, `⌛` → await, `λ` → lambda

### Logic & Comparison
- `∧` → and, `∨` → or, `¬` → not
- `∈` → in, `≡` → is

### Constants & Returns
- `✓` → True, `⊥` → False, `Ø` → None
- `⟲` → return, `⟰` → yield, `⋯` → pass

### Built-in Functions
- `π` → print, `ℓ` → len
- `⟪` → range, `№` → enumerate

*You can add or remove mappings as pleased*

## Configuration Management

### File Locations (Priority Order)
1. `.(φ)/config.json` - Project root
2. `.phicode/config.json` - Broader compatibility  
3. Environment variables - Runtime parameters
4. Built-in defaults - Default symbol set

### Validation Settings
- Conflict detection prevents overriding built-ins
- Python identifier validation for custom keywords
- Integration with security validation when available
- Configurable strict vs permissive modes

### Configuration Commands
```bash
phicode --config-generate    # Create initial configuration
phicode --config-reset       # Reset to built-in defaults
```

### Environment Variables
- `PHICODE_VALIDATION`: Enable symbol validation (default true)
- `PHICODE_STRICT`: Use strict validation mode (default false)

---

## System Requirements

**Dependencies:** Python 3.8 or later required. Optional components need additional libraries (xxHash, psutil, regex). Security features require Rust toolchain or precompiled binaries.

## Limitations

**Performance Characteristics:**
- Import hook adds measurable startup overhead
- Caching mechanism consumes additional disk space in `.φcache/` directories
- Memory-mapped I/O used for files larger than 8KB threshold

**Platform Requirements:**
- Requires Unicode-capable terminals and fonts for symbol display
- Subprocess execution required for interpreter switching
- Optional binary components depend on Rust toolchain availability

**Security Model:**
- Security validation depends on optional binary components
- Pattern matching may produce false positives with legitimate code patterns
- Bypass mode disables all protection mechanisms

## Troubleshooting

### Performance Issues
- Use PyPy for compute-intensive workloads: `phicode --pypy`
- Check cache directory write permissions
- Monitor system resources during execution

### Import Problems  
- Verify file paths and extensions
- Confirm import hooks are installed
- Check module dependencies

### Configuration Issues
- Reset configuration: `phicode --config-reset`
- Validate environment variable syntax
- Verify interpreter availability with `--list-interpreters`

### Security Component Issues
- Install components: `phicode --security-install`
- Skip validation for trusted code: `phicode --bypass`
- Check status: `phicode --security-status`

### Symbol Configuration Issues
- Check symbol mappings don't conflict with Python syntax
- Verify custom syntax matches configuration
- Ensure terminal supports Unicode characters

### File Extension Problems  
- Confirm file extension matches configuration setting
- Verify import paths point to correct directories
- Check that custom files exist in configured locations

## Support

- **Website:** [banes-lab.com](https://banes-lab.com)
- **GitHub:** [Varietyz/phicode-engine](https://github.com/Varietyz/phicode-engine)
- **Email:** [jay@banes-lab.com](mailto:jay@banes-lab.com)

**License:** [Phicode Non-Commercial License](https://banes-lab.com/licensing)  
**Author:** Jay Baleine