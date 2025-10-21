# 🚀 Winipedia Utils 
(Some of the README is AI generated, so code examples might have bugs, please check the source code directly on problems. Every functions has a docstring.)

> A comprehensive Python utility package that enforces best practices, automates project setup, and provides a complete testing framework for modern Python projects.

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Setup Process](#setup-process)
- [Utilities](#utilities)
- [Usage Examples](#usage-examples)
- [Important Notes](#important-notes)

---

## Overview

**Winipedia Utils** is a utility library that serves two primary purposes:

1. **🛠️ Utility Package** - Provides reusable functions across several domains (concurrency, data handling, security, testing, etc.)
2. **🏗️ Project Framework** - Automates project setup, testing infrastructure, code quality checks, and best practices enforcement

### Key Features

✨ **Automatic Test Generation** - Creates mirror test structure matching your source code
🔒 **Security First** - Built-in encryption, keyring integration, and security scanning
⚡ **Concurrent Processing** - Unified interface for multiprocessing and multithreading
📊 **Data Handling** - Polars-based dataframe utilities with cleaning pipelines
🎯 **Strict Type Checking** - mypy in strict mode with full type annotations
🧹 **Code Quality** - Automated linting, formatting, and security checks
📝 **Comprehensive Logging** - Automatic method instrumentation and performance tracking

> **Note:** Functions starting with `_` are for internal use only and should not be called directly by package users.

---

## Quick Start

### Installation

```bash
# clone from github
git clone https://github.com/user/your-repo.git

# Initialize a new Poetry project
poetry init

# Add winipedia-utils to your project
poetry add winipedia-utils

# Run the automated setup
poetry run python -m winipedia_utils.setup
```

That's it! The setup script will configure everything for you.

---

## Setup Process

The `winipedia_utils.setup` command automates the entire project initialization in a few steps:

### Step 1️⃣ - Install Dev Dependencies
Installs all development tools needed for code quality like:
- `ruff` - Fast Python linter and formatter
- `mypy` - Static type checker
- `pytest` - Testing framework
- `bandit` - Security scanner
- `pre-commit` - Git hooks framework

### Step 2️⃣ - Create Pre-commit Configuration
Sets up `.pre-commit-config.yaml` with the winipedia-utils hook that runs on every commit.

### Step 3️⃣ - Install Pre-commit Framework
Installs git hooks so checks run automatically before commits.

### Step 4️⃣ - Update .gitignore
Adds standard patterns for Python projects:
```
__pycache__/
.idea/
.mypy_cache/
.pytest_cache/
.ruff_cache/
.vscode/
dist/
test.py
.git/
```

### Step 5️⃣ - Configure pyproject.toml
Adds tool configurations in pyproject.toml for e.g.:
- **mypy** - Strict type checking
- **ruff** - Linting and formatting rules
- **pytest** - Test discovery and execution
- **bandit** - Security scanning

### Step 6️⃣ - Create GitHub Actions Workflow
Sets up `.github/workflows/publish.yaml` for automated PyPI publishing:
- Triggers on GitHub releases
- Configures Poetry with PyPI token
- Builds and publishes package automatically

### Step 7️⃣ - Create Project Root
Creates your project's root package directory with `py.typed` marker for type hint support.

### Step 8️⃣ - Run Pre-commit Hook
Executes the complete quality pipeline (see below).

---

## Pre-commit Hook Workflow

When you commit code, the winipedia-utils hook automatically runs a few quality checks e.g.:
```
┌─────────────────────────────────────────────────────────┐
│         Pre-commit Hook Execution Pipeline              │
├─────────────────────────────────────────────────────────┤
│ 1. Patch Version (poetry version patch, git add toml)   │
│ 2. Update Poetry                                        │
│ 3. Install Dependencies (poetry install)                │
│ 4. Update All Dependencies (poetry update)              │
│ 5. Lock Dependencies (poetry lock)                      │
│ 6. Validate Configuration (poetry check)                │
│ 7. Generate Tests (auto-create test files)              │
│ 8. Lint Code (ruff check --fix)                         │
│ 9. Format Code (ruff format)                            │
│ 10. Type Check (mypy)                                   │
│ 11. Security Scan (bandit)                              │
│ 12. Run Tests (pytest)                                  │
└─────────────────────────────────────────────────────────┘
```

### Auto-generated Test Structure

The test generation creates a **mirror structure** of your source code:

```
my_project/
├── my_project/
│   ├── module_a.py
│   └── package_b/
│       └── module_c.py
└── tests/
    ├── test_module_a.py
    └── test_package_b/
        └── test_module_c.py
```

For each function, class, and method, skeleton tests are created with `NotImplementedError` placeholders for you to implement.

---

## Utilities

Winipedia Utils provides comprehensive utility modules:

### 1. 🔄 Concurrent Processing

Execute functions in parallel with automatic worker pool management.

**Use Cases:** CPU-bound tasks, I/O-bound operations, batch processing

```python
from winipedia_utils.concurrent.multiprocessing import multiprocess_loop
from winipedia_utils.concurrent.multithreading import multithread_loop

# CPU-bound: Process data in parallel
def expensive_computation(x):
    return x ** 2

data = [[i] for i in range(100)]
results = multiprocess_loop(expensive_computation, data)

# I/O-bound: Fetch URLs concurrently
def fetch_url(url):
    return requests.get(url).text

urls = [["https://example.com"], ["https://google.com"]]
results = multithread_loop(fetch_url, urls)
```

**Key Functions:**
- `multiprocess_loop()` - Parallel execution for CPU-bound tasks
- `multithread_loop()` - Parallel execution for I/O-bound tasks
- `cancel_on_timeout()` - Decorator to timeout long-running functions
- `find_max_pools()` - Automatically determine optimal worker count

---

### 2. 📊 Data Cleaning & Handling

Build data cleaning pipelines using Polars (not Pandas).

**Use Cases:** ETL pipelines, data validation, dataframe transformations

```python
from winipedia_utils.data.dataframe.cleaning import CleaningDF
import polars as pl

class MyDataCleaner(CleaningDF):
    COL_NAME = "name"
    COL_VALUE = "value"

    @classmethod
    def get_rename_map(cls):
        return {cls.COL_NAME: "original_name", cls.COL_VALUE: "original_value"}

    @classmethod
    def get_col_dtype_map(cls):
        return {cls.COL_NAME: pl.Utf8, cls.COL_VALUE: pl.Float64}

    @classmethod
    def get_fill_null_map(cls):
        return {cls.COL_NAME: "Unknown", cls.COL_VALUE: 0.0}

    @classmethod
    def get_drop_null_subsets(cls):
        return ((cls.COL_NAME,),)

    @classmethod
    def get_sort_cols(cls):
        return ((cls.COL_NAME, False),)

    @classmethod
    def get_unique_subsets(cls):
        return ((cls.COL_NAME,),)

    @classmethod
    def get_no_null_cols(cls):
        return (cls.COL_NAME,)

    @classmethod
    def get_col_converter_map(cls):
        return {cls.COL_NAME: cls.lower_col}

    @classmethod
    def get_add_on_duplicate_cols(cls):
        return (cls.COL_VALUE,)

    @classmethod
    def get_col_precision_map(cls):
        return {cls.COL_VALUE: 2}

# Usage
data = MyDataCleaner({"original_name": ["Alice", "bob"], "original_value": [1.5, 2.7]})
print(data.df)  # Cleaned and validated dataframe
```

**Key Features:**
- Automatic column renaming
- Type conversion and validation
- Null value handling
- Deduplication with aggregation
- Sorting and precision rounding
- Comprehensive data validation

---

### 3. 🔧 Git Utilities

Manage gitignore patterns, pre-commit configuration, and GitHub Actions workflows.

**Use Cases:** Project setup, git workflow automation, CI/CD pipeline setup

```python
from winipedia_utils.git.gitignore.gitignore import (
    path_is_in_gitignore,
    walk_os_skipping_gitignore_patterns,
    add_patterns_to_gitignore
)
from winipedia_utils.git.workflows.publish import (
    load_publish_workflow,
    dump_publish_workflow
)

# Check if path is ignored
if path_is_in_gitignore("dist/"):
    print("This path is in .gitignore")

# Walk directory respecting gitignore
for root, dirs, files in walk_os_skipping_gitignore_patterns("."):
    print(f"Processing: {root}")

# Add patterns to gitignore
add_patterns_to_gitignore(["*.log", "temp/"])

# Load and modify publish workflow
workflow = load_publish_workflow()
print(f"Workflow name: {workflow.get('name')}")
```

**Key Functions:**
- `path_is_in_gitignore()` - Check if path matches gitignore patterns
- `walk_os_skipping_gitignore_patterns()` - Directory traversal respecting gitignore
- `add_patterns_to_gitignore()` - Add patterns to .gitignore file
- `load_publish_workflow()` - Load GitHub Actions publish workflow
- `dump_publish_workflow()` - Save GitHub Actions publish workflow
- Pre-commit configuration management

---

### 4. 🔁 Iterating Utilities

Handle iterables with sensible defaults.

**Use Cases:** Working with generators, unknown-length iterables

```python
from winipedia_utils.iterating.iterate import get_len_with_default

# Get length with fallback
length = get_len_with_default(some_generator, default=100)
print(f"Length: {length}")
```

---

### 5. 📝 Logging Utilities

Simple, standardized logging setup with automatic method instrumentation.

**Use Cases:** Application logging, debugging, performance tracking

```python
from winipedia_utils.logging.logger import get_logger

logger = get_logger(__name__)
logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred")
```

**Features:**
- Pre-configured logging levels
- ANSI color support for terminal output
- Automatic method logging via metaclasses

---

### 6. 📦 Module/Package Utilities

Introspect and manipulate Python modules and packages dynamically.

**Use Cases:** Testing frameworks, code generation, dynamic imports

```python
from winipedia_utils.modules.module import (
    to_module_name,
    to_path,
    create_module,
    import_obj_from_importpath,
    make_obj_importpath
)
from winipedia_utils.modules.class_ import get_all_cls_from_module
from winipedia_utils.modules.function import get_all_functions_from_module
from winipedia_utils.modules.package import find_packages, walk_package

# Convert between paths and module names
module_name = to_module_name("src/package/module.py")  # "src.package.module"
path = to_path("src.package.module", is_package=False)  # Path("src/package/module.py")

# Create modules dynamically
new_module = create_module("my_package.new_module", is_package=False)

# Import objects by path
obj = import_obj_from_importpath("my_package.MyClass")

# Get all classes in a module
classes = get_all_cls_from_module("my_package.module")

# Get all functions in a module
functions = get_all_functions_from_module("my_package.module")

# Find all packages
packages = find_packages(depth=1)

# Walk package hierarchy
for package, modules in walk_package(my_package):
    print(f"Package: {package.__name__}, Modules: {len(modules)}")
```

---

### 7. 🎯 Object-Oriented Programming Utilities

Advanced metaclasses and mixins for class composition and behavior extension.

**Use Cases:** Framework development, enforcing design patterns, automatic instrumentation

```python
from winipedia_utils.oop.mixins.mixin import ABCLoggingMixin, StrictABCLoggingMixin
from abc import abstractmethod
from typing import final

# Automatic logging + ABC functionality
class MyService(ABCLoggingMixin):
    def process_data(self, data):
        # Automatically logged with timing
        return data * 2

# Strict implementation enforcement + logging
class StrictService(StrictABCLoggingMixin):
    @abstractmethod
    def required_method(self):
        pass

    @final
    def final_method(self):
        return "Cannot be overridden"

# Usage
service = MyService()
result = service.process_data(42)  # Automatically logged
```

**Features:**
- `ABCLoggingMixin` - Automatic method logging with performance tracking
- `StrictABCLoggingMixin` - Enforces implementation + logging
- Rate-limited logging to prevent log flooding
- Automatic timing of method execution

---

### 8. 🖥️ OS Utilities

Operating system utilities for command execution and path management.

**Use Cases:** Subprocess management, command discovery

```python
from winipedia_utils.os.os import which_with_raise, run_subprocess

# Find command path
python_path = which_with_raise("python")

# Run subprocess with timeout
result = run_subprocess(
    ["python", "-c", "print('hello')"],
    timeout=5,
    capture_output=True
)
print(result.stdout)
```

---

### 9. 🏗️ Projects Utilities

Poetry and project setup utilities.

**Use Cases:** Project initialization, configuration management

```python
from winipedia_utils.projects.project import make_name_from_package
from winipedia_utils.projects.poetry.config import get_poetry_package_name

# Get project name from pyproject.toml
project_name = get_poetry_package_name()

# Convert package name to human-readable format
readable_name = make_name_from_package(my_package)
# "my_package" -> "My-Package"
```

---

### 10. 🔐 Security Utilities

Encryption and secure credential storage using keyring.

**Use Cases:** API key management, secure data encryption

```python
from winipedia_utils.security.keyring import (
    get_or_create_fernet,
    get_or_create_aes_gcm
)

# Get or create Fernet encryption key
fernet, key_bytes = get_or_create_fernet("my_app", "user@example.com")
encrypted = fernet.encrypt(b"secret data")
decrypted = fernet.decrypt(encrypted)

# Get or create AES-GCM key
aes_gcm, key_bytes = get_or_create_aes_gcm("my_app", "user@example.com")
```

**Features:**
- Automatic key generation and storage
- Keyring integration for secure storage
- Support for Fernet and AES-GCM encryption

---

### 11. 🧪 Testing Utilities

Comprehensive testing framework with automatic test generation.

**Use Cases:** Test infrastructure, test discovery, custom assertions

```python
from winipedia_utils.testing.assertions import assert_with_msg
from winipedia_utils.testing.convention import (
    make_test_obj_name,
    get_test_obj_from_obj,
    make_test_obj_importpath_from_obj
)

# Custom assertions
assert_with_msg(result == expected, "Result does not match expected value")

# Test naming conventions
test_name = make_test_obj_name(my_function)  # "test_my_function"

# Get corresponding test object
test_obj = get_test_obj_from_obj(my_function)

# Get test import path
test_path = make_test_obj_importpath_from_obj(my_function)
```

**Features:**
- Automatic test file generation
- Mirror test structure matching source code
- Test naming conventions
- Fixture management with scopes (function, class, module, package, session)

---

### 12. 📄 Text Utilities

String manipulation and text processing utilities.

**Use Cases:** String processing, XML parsing, hashing, user input

```python
from winipedia_utils.text.string import (
    ask_for_input_with_timeout,
    find_xml_namespaces,
    value_to_truncated_string,
    get_reusable_hash,
    split_on_uppercase
)

# Get user input with timeout
user_input = ask_for_input_with_timeout("Enter value: ", timeout=10)

# Extract XML namespaces
namespaces = find_xml_namespaces("<root xmlns:ns='http://example.com'/>")

# Truncate values for logging
truncated = value_to_truncated_string(large_object, max_length=50)

# Generate consistent hash
hash_value = get_reusable_hash({"key": "value"})

# Split on uppercase
parts = split_on_uppercase("HelloWorld")  # ["Hello", "World"]
```

---

### 13. 🎨 Resources Utilities

SVG and resource utilities (minimal, may be removed in future versions).

---

## Usage Examples

### Example 1: Setting Up a New Project

```bash
# Create new project
mkdir my_project
cd my_project

# Initialize Poetry
poetry init

# Add winipedia-utils
poetry add winipedia-utils

# Run setup (this does everything!)
poetry run python -m winipedia_utils.setup

# Start coding
poetry run python -m my_project
```

### Example 2: Using Concurrent Processing

```python
from winipedia_utils.concurrent.multiprocessing import multiprocess_loop

def process_item(item_id, multiplier):
    return item_id * multiplier

# Process 1000 items in parallel
items = [[i] for i in range(1000)]
results = multiprocess_loop(
    process_item,
    items,
    process_args_static=[2],  # multiplier = 2
    process_args_len=1000
)
```

### Example 3: Building a Data Pipeline

```python
from winipedia_utils.data.dataframe.cleaning import CleaningDF
import polars as pl

class SalesDataCleaner(CleaningDF):
    COL_PRODUCT = "product"
    COL_AMOUNT = "amount"

    @classmethod
    def get_rename_map(cls):
        return {cls.COL_PRODUCT: "product_name", cls.COL_AMOUNT: "sale_amount"}

    @classmethod
    def get_col_dtype_map(cls):
        return {cls.COL_PRODUCT: pl.Utf8, cls.COL_AMOUNT: pl.Float64}

    # ... implement other required methods ...

# Usage
raw_data = {"product_name": ["A", "B"], "sale_amount": [100.5, 200.7]}
cleaned = SalesDataCleaner(raw_data)
print(cleaned.df)
```

---

## Important Notes

### ⚠️ Git Commit Workflow

When using winipedia-utils, you **must** use Poetry to run git commit:

```bash
# ✅ Correct - Uses Python environment for pre-commit hook
poetry run git commit -m "Your commit message"

# ❌ Wrong - Pre-commit hook won't run properly
git commit -m "Your commit message"
```

This is necessary because the pre-commit hook needs access to the Python environment and installed packages.

### 📌 Internal Functions

Functions and methods starting with `_` are for **internal use only**:

```python
# ❌ Don't use these
from winipedia_utils.git.gitignore.gitignore import _get_gitignore_patterns

# ✅ Use public API instead
from winipedia_utils.git.gitignore.gitignore import add_patterns_to_gitignore
```

### 🎯 Philosophy

The core philosophy of Winipedia Utils is to:

> **Enforce good habits, ensure clean code, and save time when starting new projects**

By automating setup, testing, linting, formatting, and type checking, you can focus on writing business logic instead of configuring tools.

---

## Requirements

- **Python:** 3.12 or higher
- **Poetry:** For dependency management
- **Git:** For version control and pre-commit hooks

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

## Contributing

Contributions are welcome! Please ensure all code follows the project's quality standards:

- Type hints on all functions
- Comprehensive docstrings (Google style)
- Full test coverage
- Pass all linting and security checks

---
