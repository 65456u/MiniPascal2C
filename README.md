# MiniPascal2C

## Introduction
This project is a compiler for a subset of the Pascal language, called MiniPascal, to C. The compiler is written in Python and uses the `Lark` library for parsing. The compiler is able to generate C code from MiniPascal code, which can then be compiled and executed.

## Quick Start

### Prerequisites
- Python 3.11 or later
- Clang 18.0.0 or later (for compiling and analyzing the generated C code)

### Python Package

#### Manual Installation
1. Clone the repository
```shell
git clone https://github.com/65456u/MiniPascal2C.git
cd MiniPascal2C
```
2. Install the package
```shell
pip install .
```

#### PyPI Installation
```shell
pip install mp2c
```

### CLI Usage
```shell
python main.py -i <input_file> -o <output_file>
```

### GUI Usage
```shell
python gui.py
```

