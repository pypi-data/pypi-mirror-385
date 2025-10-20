# JSON Scout

[![Documentation](https://img.shields.io/badge/docs-live-brightgreen)](https://deamonpog.github.io/json-scout/)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](./LICENSE)

**Scout JSON structure and navigate data safely with intuitive exploration tools.**

JSON Scout provides a robust suite of tools designed for developers and data professionals who need to introspect, analyze, and safely navigate complex JSON data structures. Whether you're working with APIs, configuration files, or large datasets, JSON Scout offers both low-level utilities and high-level abstractions to make JSON exploration intuitive and error-free.

## ✨ Key Features

- **🔍 Structural Analysis**: Automatic schema discovery and hierarchy inspection
- **🛡️ Safe Navigation**: Exception-free access with monadic-style `Maybe` wrapper
- **🔧 Comprehensive Utilities**: File operations, XML integration, and unified interface
- **📊 Enterprise Ready**: Type safety, performance optimization, and comprehensive documentation

## 🚀 Quick Start

### Installation

```bash
pip install json-scout
```

### Basic Usage

```python
import jsonscout as js

# Sample data
data = {
    "users": [
        {"name": "Alice", "age": 30, "email": "alice@example.com"},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35, "email": "charlie@example.com"}
    ],
    "metadata": {"version": "1.0", "created": "2024-01-01"}
}

# Safe navigation with automatic error handling
explorer = js.Xplore(data)
user_name = explorer['users'][0]['name'].value()  # Returns: "Alice"
missing_field = explorer['users'][1]['email'].value()  # Returns: None (no exception)

# Structural analysis
explore = js.Explore(data['users'])
field_frequency = explore.field_counts()
print(field_frequency)  # {'name': 3, 'age': 3, 'email': 2}

# File operations
json_files = js.get_json_file_paths('/path/to/data', '*.json')
for file_path in json_files:
    data = js.read_json_file(file_path)
    explorer = js.Xplore(data)
    # Process safely...
```

## 📚 Documentation

- **[Complete Documentation](https://deamonpog.github.io/json-scout/)**: Comprehensive guides and examples
- **[API Reference](https://deamonpog.github.io/json-scout/api/)**: Detailed API documentation with examples

## 🏗️ Core Components

- **`Explore`**: Lightweight structural analysis and schema discovery
- **`Maybe`**: Monadic wrapper for safe, chainable data access
- **`SimpleXML`**: Efficient XML-to-dictionary conversion utilities
- **`Xplore`**: Unified facade combining all functionality

## 🎯 Use Cases

- **API Response Analysis**: Schema evolution tracking and data validation
- **Configuration Management**: Safe navigation of complex configuration hierarchies
- **Data Pipeline Processing**: ETL operations with robust error handling
- **Research and Analysis**: Dataset exploration and statistical analysis

## 🤝 Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details on how to submit bug reports, feature requests, and code contributions.

## 📄 License

JSON Scout is licensed under the [Apache License 2.0](./LICENSE).  
© 2025 Chathura Jayalath. See the [NOTICE](./NOTICE) file for more details.
