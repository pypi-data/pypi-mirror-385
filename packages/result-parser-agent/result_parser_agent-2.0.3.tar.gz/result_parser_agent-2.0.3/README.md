# 🎯 Results Parser Agent

A powerful, efficient parser for extracting metrics from benchmark result files using workload-specific extraction scripts. The parser automatically analyzes result files and extracts metrics into structured JSON output with high accuracy and reliability.

## 🚀 Features

- **🎯 Script-Based Parsing**: Uses workload-specific extraction scripts for reliable, deterministic metric extraction
- **📁 Flexible Input**: Process single files or entire directories of result files
- **🔧 Workload-Specific Tools**: Dedicated extraction scripts for different benchmark types (FIO, Redis, Nginx, MariaDB/MySQL TPC-H & TPC-C) that automatically extract all available metrics
- **📊 Structured Output**: Direct output in Pydantic schemas for easy integration
- **🛠️ Professional CLI**: Clean, modular command-line interface with service-based architecture
- **🔧 Python API**: Easy integration into existing Python applications
- **🔄 Error Recovery**: Robust error handling and retry mechanisms
- **📦 Git-based Scripts**: Secure, efficient script distribution and caching system
- **🔒 Enterprise Security**: SSH authentication, environment variables, and secure defaults
- **🏗️ Service Architecture**: Modular, maintainable codebase with clear separation of concerns

## 📦 Installation

### Quick Install (Recommended)

```bash
pip install result-parser-agent
```

### Development Install

```bash
# Clone the repository
git clone https://github.com/Infobellit-Solutions-Pvt-Ltd/result-parser-agent.git
cd result-parser-agent

# Install with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv pip install -e .

# Or install with pip
pip install -e .
```

## 📋 Configuration

### Environment Variables

Create a `.env` file in your project directory:

```bash
# Script Management
SCRIPTS_BASE_URL=git@github.com:AMD-DEAE-CEME/epdw2.0_parser_scripts.git
SCRIPTS_CACHE_DIR=~/.cache/result-parser/scripts
SCRIPTS_CACHE_TTL=3600
```

## 🎯 Quick Start

### 1. Parse Results

```bash
# Parse all files in a directory with workload-specific tools
result-parser parse ./benchmark_results nginx

# Parse Redis results (scripts automatically extract all available metrics)
result-parser parse ./benchmark_results redis

# Parse a single file
result-parser parse ./results.txt fio

# Custom output file
result-parser parse ./results/ mariadb_tpch --output my_results.json

# Verbose output
result-parser parse ./results/ mysql_tpcc --verbose
```

### 2. Manage Registry

```bash
# List all available workloads in registry
result-parser registry list

# Show detailed information about a specific workload
result-parser registry show nginx

# Download workload script to cache
result-parser registry download nginx

# Add new workload to registry
result-parser registry add fio --metrics "random_read_iops,random_write_iops" --description "Storage performance benchmark"

# Update existing workload
result-parser registry update redis --metrics "SET(requests/sec),GET(requests/sec)"
```

### 3. Manage Cache

```bash
# Show cache information and statistics
result-parser cache info

# List cached workloads
result-parser cache list

# Clear specific workload cache
result-parser cache clear fio

# Clear all caches
result-parser cache clear-all
```

### 4. Show Version

```bash
# Show version information
result-parser version
```

## 🏗️ Service-Based Architecture

The parser now uses a modern service-based architecture for better maintainability and testability:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Layer     │    │  Service Layer   │    │  Data Layer     │
│  (Typer CLI)    │◄──►│  (Business Logic)│◄──►│  (Models)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Command Groups │    │  Core Services   │    │  Pydantic       │
│  (parse,        │    │  (Registry,      │    │  Models         │
│   registry,     │    │   Cache,         │    │  (Structured    │
│   cache)        │    │   Workload,      │    │   Results)      │
└─────────────────┘    │   Parsing)       │    └─────────────────┘
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  External        │
                       │  (Git, Cache,    │
                       │   Scripts)       │
                       └──────────────────┘
```

### **Service Layer Components:**

- **RegistryService**: Manages workload registry and metadata
- **CacheService**: Handles script and registry caching
- **WorkloadService**: Orchestrates workload operations
- **ParsingService**: Core parsing logic and result processing

### **Key Benefits:**
- **Modular**: Clear separation of concerns
- **Testable**: Each service can be tested independently
- **Maintainable**: Easy to modify and extend
- **Scalable**: Services can be easily replaced or enhanced

## 🚀 Cache-First Architecture

The CLI tool uses a **cache-first approach** for better performance and offline capability:

### **Local Cache Priority**
- **No API calls by default**: The CLI first checks local cache for available workload scripts
- **Fast startup**: No network delays when using cached workloads
- **Offline capability**: Works without internet connection for cached workloads
- **Smart downloading**: Scripts are downloaded only when needed

### **Smart Workload Discovery**
- **Cache-first validation**: When parsing, checks local cache first
- **Auto-download**: If workload not in cache, automatically downloads from registry
- **Registry management**: Use `registry list` to see all available workloads

## 📊 How Metrics Extraction Works

The agent uses a **two-phase approach** for metrics extraction:

### **Phase 1: Automatic Extraction**
- **Scripts are self-sufficient**: Each workload-specific script automatically extracts all available metrics from the data
- **No user input required**: You don't need to specify which metrics to extract when parsing
- **Comprehensive coverage**: Scripts extract all metrics they can find in the data

### **Phase 2: Validation & Reporting**
- **Expected metrics**: Defined in the workload registry for validation purposes
- **Automatic validation**: The agent compares extracted metrics against expected metrics
- **Detailed reporting**: Shows missing metrics, unexpected metrics, and extraction success

### **Example Output**
```bash
📊 Expected metrics for fio: ['random_read_iops', 'random_write_iops']
📈 Extracted metrics: random_read_iops, random_write_iops, sequential_read_mbps
ℹ️  Additional metrics found: sequential_read_mbps
✅ All expected metrics successfully extracted!
```

This approach ensures **maximum flexibility** while maintaining **quality control** through validation.

## 🔧 Supported Workloads

The agent supports various benchmark workloads with dedicated extraction scripts:

| Workload | Description | Example Metrics |
|----------|-------------|-----------------|
| **FIO** | Storage performance benchmark | `random_read_iops`, `random_write_iops`, `sequential_read_mbps` |
| **Redis** | In-memory database benchmark | `SET(requests/sec)`, `GET(requests/sec)` |
| **Nginx** | Web server performance | `Requests/sec`, `Transfer/sec` |
| **MariaDB TPC-H** | Database TPC-H benchmark | `Power@Size`, `Throughput@Size`, `QphH@Size` |
| **MySQL TPC-H** | Database TPC-H benchmark | `Power@Size`, `Throughput@Size`, `QphH@Size` |
| **MariaDB TPC-C** | Database TPC-C benchmark | `tpmC`, `tpmTOTAL` |
| **MySQL TPC-C** | Database TPC-C benchmark | `tpmC`, `tpmTOTAL` |
| **Stream** | Memory bandwidth benchmark | `Triad` |
| **DGEMM** | Matrix multiplication benchmark | `GFLOPS` |
| **Cassandra** | Database benchmark | `Op rate(op/s)`, `Read(op/s)`, `Write(op/s)` |
| **HPL** | High Performance Linpack | `GFLOPS` |
| **SPEC CPU** | CPU benchmark suite | `SPECrate(R)2017_int_base`, `SPECrate(R)2017_fp_base` |
| **FFmpeg** | Video encoding benchmark | `fps`, `fph`, `avg_elapsed_time(secs)` |
| **LTP** | Linux Test Project | `Total Tests`, `Total Skipped Tests`, `Total Failures` |
| **SPECjbb** | Java business benchmark | `hbir (max attempted)`, `max-jops`, `critical-jops` |

## 🛠️ CLI Commands Reference

### `parse` - Parse Benchmark Results
```bash
result-parser parse <input_path> <workload> [OPTIONS]

Arguments:
  input_path              Path to results file or directory
  workload                Workload type (fio, redis, nginx, etc.)

Options:
  --output TEXT           Output file path [default: results.json]
  --verbose               Enable verbose logging
  --help                  Show this message and exit
```

### `registry` - Manage Workload Registry
```bash
result-parser registry <command> [OPTIONS]

Commands:
  list                    List all available workloads in registry
  show <workload>         Show detailed information about a workload
  add <workload>          Add a new workload to registry
  update <workload>       Update an existing workload
  download <workload>     Download workload script to cache
```

### `cache` - Manage Script Cache
```bash
result-parser cache <command> [OPTIONS]

Commands:
  info                    Show cache information and statistics
  list                    List all cached workloads
  clear [workload]        Clear specific or all caches
```

### `version` - Show Version
```bash
result-parser version

Shows:
- Application version
- Build information
```

## 🔒 Security Features

- **SSH Authentication**: Secure access to private Git repositories
- **Environment Variables**: No hardcoded secrets or API keys
- **Input Validation**: Comprehensive validation of all user inputs
- **Secure Defaults**: Principle of least privilege in configuration
- **Script Isolation**: Scripts run in controlled environment

## 🚀 Performance Features

- **Script Caching**: Local cache with TTL-based invalidation
- **Sparse Git Operations**: Efficient individual script retrieval
- **Lazy Loading**: Scripts downloaded only when needed
- **Service Architecture**: Optimized for performance and scalability

## 🧪 Testing

Run the comprehensive test suite to ensure everything works correctly:

```bash
# Run all tests
uv run python tests/test_functionality.py

# Run with pytest
uv run pytest

# Run with coverage
uv run pytest --cov=src/result_parser_agent

# Run specific test file
uv run pytest tests/test_functionality.py
```

## 📚 Development

### Code Quality
```bash
# Format code
uv run black .

# Sort imports
uv run isort .

# Lint code
uv run ruff check .

# Type checking
uv run mypy src/

# Run all quality checks
uv run ruff check . && uv run black --check . && uv run isort --check-only .
```

### Service Development
The codebase is organized into clear service layers:

- **`src/result_parser_agent/services/`**: Core business logic services
- **`src/result_parser_agent/cli/commands/`**: CLI command implementations
- **`src/result_parser_agent/models/`**: Pydantic data models
- **`src/result_parser_agent/utils/`**: Utility functions and validators

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [GitHub Wiki](https://github.com/Infobellit-Solutions-Pvt-Ltd/result-parser-agent/wiki)
- **Issues**: [GitHub Issues](https://github.com/Infobellit-Solutions-Pvt-Ltd/result-parser-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Infobellit-Solutions-Pvt-Ltd/result-parser-agent/discussions)

## 🏆 Acknowledgments

- Powered by [Typer](https://typer.tiangolo.com/) for CLI development
- Enhanced with [Pydantic](https://pydantic.dev/) for data validation
- Script management powered by Git and SSH
- Built with Python async/await for efficient processing
- Service architecture inspired by modern microservices patterns