# Blendercolors

A simple module for coloring terminal output via ANSI codes with a few colors. 

Works on all terminals with ANSI. (Linux, MacOS, modern Windows)

Lightweight and *dependency-free*

### What you get
Just put inside f-string in print:
![Demo](https://raw.githubusercontent.com/tdhster/blendercolors/main/example.png)


## Installation

```bash
pip install blendercolors
```

## Usage

```python
from blendercolors import bcolors

print(f"{bcolors.WARNING}Yellow color for warnings{bcolors.ENDC}")
print(f"Three OK colors")
print(f" {bcolors.OKGREEN}green{bcolors.ENDC}, \
         {bcolors.OKBLUE}blue{bcolors.ENDC} and \
         {bcolors.OKCYAN}cyan{bcolors.ENDC}")
print(f"{bcolors.FAIL}Red for error texts{bcolors.ENDC}")
# and others color and formatting.
```

Start coloring text with defined choiced color, finish coloring by bcolors.ENDC

ANSI codes:
```python

    HEADEanytimeR = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
```

Anytime your can disable all coloring without removing previos written code, just place at top of program:

```python
bcolors.disable()
```

Based on the classic bcolors snippet popularized by Blender and Stack Overflow.

Inspired by stackoverflow post: https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
