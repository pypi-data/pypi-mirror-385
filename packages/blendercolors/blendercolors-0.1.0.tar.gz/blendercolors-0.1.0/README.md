# Blendercolors

A simple module for coloring terminal output via ANSI codes. Based on the classic bcolors snippet from Blender 3D source code.

Works on all terminals with ANSI. (Linux, MacOS, modern Windows)

## Features

- Simple ANSI color codes
- Cross-platform (works in most modern terminals)
- Lightweight and *dependency-free*

## Installation

```bash
pip install blendercolors
```

## Usage

```python
from blendercolors import bcolors

print(f"{bcolors.WARNING}Warning: No active frommets remain. Continue?{bcolors.ENDC}")
print(f"{bcolors.OKGREEN}Success!{bcolors.ENDC}")
```

Start coloring text with defined choiced color, finish coloring by bcolors.ENDC

ANSI codes:
```python

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
```

Based on the classic bcolors snippet popularized by Blender and Stack Overflow.

Inspired by stackoverflow post: https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
