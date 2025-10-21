# slither-cli

A Python CLI tool for displaying directory structure as ASCII art trees in your terminal.

## Features

- Display directory trees with beautiful ASCII art formatting
- Customizable depth limiting
- Pattern-based file filtering (include/exclude)
- Show/hide hidden files
- Display file sizes in bytes or human-readable format
- Reverse sort order
- Directories-only mode

## Installation

### Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Install from source

```bash
git clone https://github.com/jesshart/slither-cli.git
cd slither-cli
uv sync
```

## Usage

### Basic usage

```bash
# Display current directory
uv run slither

# Display specific directory
uv run slither /path/to/dir
```

### Options

```bash
# Limit depth to 2 levels
uv run slither -L 2

# Show hidden files
uv run slither -a

# Show directories only
uv run slither -d

# Show only Python files
uv run slither -P "*.py"

# Ignore compiled Python files
uv run slither -I "*.pyc"

# Show file sizes in human-readable format
uv run slither -s -h

# Reverse sort order
uv run slither -r

# Combine multiple options
uv run slither -L 3 -a -P "*.py" -s -h
```

### All available options

| Option | Long form | Description |
|--------|-----------|-------------|
| `-L` | `--level` | Max display depth of the directory tree |
| `-a` | `--all` | Print all files, including hidden files |
| `-d` | `--dirs-only` | List directories only |
| `-P` | `--pattern` | List only files that match the pattern (wildcard) |
| `-I` | `--ignore` | Do not list files that match the pattern |
| `-s` | `--size` | Print file sizes in bytes |
| `-h` | `--human` | Print file sizes in human-readable format |
| `-r` | `--reverse` | Sort output in reverse order |

## Example Output

```
/Users/jesse/Repos/personal/slither-cli
├── slither
│   ├── __init__.py
│   ├── cli.py
│   └── tree.py
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock

1 directory, 6 files
```

## Development

### Project structure

```
slither-cli/
├── slither/           # Main package
│   ├── __init__.py   # Package initialization
│   ├── cli.py        # Typer-based CLI interface
│   └── tree.py       # Core tree building and rendering logic
├── main.py           # Alternative entry point
├── pyproject.toml    # Project configuration
└── uv.lock           # Dependency lock file
```

### Built with

- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting

## License

This project is open source and available under the MIT License.

## Author

Created by Jesse Hart
