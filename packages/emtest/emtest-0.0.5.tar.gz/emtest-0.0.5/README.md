# emtest - Python Testing Utilities

A Python package providing testing utilities.

## Features

### 🎨 Clean Test Output for Pytest
- **MinimalReporter**: Custom pytest reporter with clean, colored output using simple symbols (✓/✗/-)
- **Configurable Output**: Toggle between minimal and standard pytest output modes

### 🔧 Development Utilities  
- **Source Path Management**: Dynamically add directories to Python path for testing source code
- **Module Source Validation**: Ensure modules are loaded from source directories (not installed packages)
- **Thread Cleanup Monitoring**: Wait for and verify proper thread cleanup in tests

### ⚡ Enhanced Test Execution
- **Dual Execution Pattern**: Run tests both as pytest tests and standalone Python scripts
- **Breakpoint Integration**: Easy debugging with pytest's `--pdb` integration
- **Progress Indicators**: Visual progress bars for waiting operations

## Installation

```sh
pip install emtest
```

## Usage

See the [Usage docs](docs/Usage/PytestUtils.md) for explanations and a complete working example showing:
- Basic test setup with `conftest.py`
- Showing and hiding logs
- Dual execution pattern implementation
- Source loading validation
- Thread cleanup testing
- Options like minising output, python-debugger breakpoints and more

## Documentation

- [Full Documentation](docs/README.md):
  - [API-Reference](docs/API-Reference/README.html)
  - Usage:
    - [PytestUtils](docs/Usage/PytestUtils.md)
    - [LogRecording](docs/Usage/LogRecording.md)

## Roadmap

## Contributing

### Get Involved

- GitHub Discussions: if you want to share ideas
- GitHub Issues: if you find bugs, other issues, or would like to submit feature requests
- GitHub Merge Requests: if you think you know what you're doing, you're very welcome!

### Donate

To support me in my work on this and other projects, you can make donations with the following currencies:

- **Bitcoin:** `BC1Q45QEE6YTNGRC5TSZ42ZL3MWV8798ZEF70H2DG0`
- **Ethereum:** `0xA32C3bBC2106C986317f202B3aa8eBc3063323D4`
- [Credit Card, Debit Card, Bank Transfer, Apple Pay, Google Pay, Revolut Pay)](https://checkout.revolut.com/pay/4e4d24de-26cf-4e7d-9e84-ede89ec67f32)

Donations help me:
- dedicate more time to developing and maintaining open-source projects
- cover costs for IT resources

## About the Developer

This project is developed by a human one-man team, publishing under the name _Emendir_.  
I build open technologies trying to improve our world;
learning, working and sharing under the principle:

> _Freely I have received, freely I give._

Feel welcome to join in with code contributions, discussions, ideas and more!

## Open-Source in the Public Domain

I dedicate this project to the public domain.
It is open source and free to use, share, modify, and build upon without restrictions or conditions.

I make no patent or trademark claims over this project.  

Formally, you may use this project under either the: 
- [MIT No Attribution (MIT-0)](https://choosealicense.com/licenses/mit-0/) or
- [Creative Commons Zero (CC0)](https://choosealicense.com/licenses/cc0-1.0/)
licence at your choice.  


