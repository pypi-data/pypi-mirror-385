# FMORG - Smart File Organization Tool

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

A highly opinionated command-line tool that automatically organizes your files into folders based on intelligent filename analysis. Perfect for organizing media files, documents, and any other files with structured naming patterns.

## Features

- **Intelligent Filename Analysis**: Extracts meaningful titles from complex filenames
- **Smart Pattern Recognition**: Automatically filters out TV series patterns (S01E01), years, video formats, codecs, and technical metadata
- **Safe File Operations**: Creates folders as needed and moves files with conflict resolution
- **Configurable Thresholds**: Set minimum file count per folder to avoid clutter
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Colored Terminal Output**: Beautiful, easy-to-read output with color coding
- **Dry Run Mode**: Preview operations before executing them
- **User Confirmation**: Interactive prompts before making changes
- **Simplified Interface**: Clean, intuitive CLI without unnecessary subcommands
- **Hidden File Handling**: Automatically ignores system files like `.gitignore` and `.DS_Store`

## Installation

### From Source

```bash
git clone https://github.com/Phr33d0m/fmorg.git
cd fmorg
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/Phr33d0m/fmorg.git
cd fmorg
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

Organize files in the current directory:

```bash
fmorg
```

Or specify a directory:

```bash
fmorg /path/to/files
```

### Dry Run (Preview Changes)

See what would be done without actually moving files:

```bash
fmorg --dry-run
```

### Advanced Examples

Organize with a minimum of 2 files per folder:

```bash
fmorg /path/to/files --min 2
```

Recursively scan subdirectories:

```bash
fmorg /path/to/files --recursive
```

Organize to a different output directory:

```bash
fmorg /path/to/source --output /path/to/target
```

Skip confirmation prompts:

```bash
fmorg /path/to/files --yes
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--min` | `-m` | Minimum files per folder | `1` |
| `--output` | `-o` | Output directory for organized files | Same as input |
| `--recursive` | `-r` | Scan subdirectories recursively | `False` |
| `--dry-run` | `-d` | Preview without executing | `False` |
| `--yes` | `-y` | Skip confirmation prompt | `False` |
| `--verbose` | `-v` | Enable verbose output | `False` |
| `--quiet` | `-q` | Suppress non-error output | `False` |
| `--no-color` | | Disable colored output | `False` |
| `--help` | `-h` | Show help message | |
| `--version` | | Show version | |

## How It Works

### Filename Analysis

FMORG intelligently analyzes filenames to extract meaningful titles by:

1. **Removing TV Series Patterns**: Filters out `S01E01`, `S1E1` patterns
2. **Filtering Years**: Removes years like `2023`, `1999`
3. **Removing Quality Indicators**: Strips `1080p`, `4K`, `HDR`, etc.
4. **Cleaning Technical Terms**: Removes codecs, sources, release groups
5. **Normalizing Separators**: Converts dots, underscores, hyphens to spaces
6. **Extracting Latin Content**: Keeps only meaningful Latin letter content

### Example Transformations

```text
Divine.Love.Deep.Blue.S01E01.2025.2160p.WEB-DL.H265.HDR.AAC-ColorTV.mkv
→ Divine Love Deep Blue

The.Matrix.1999.1080p.BluRay.x264.AC3-XYZ.mp4
→ The Matrix

Breaking.Bad.S01E01.2008.HDTV.x264-LOL.mkv
→ Breaking Bad
```

### File Organization

1. **Analysis**: Files are analyzed and grouped by extracted title
2. **Planning**: Creates a safe plan showing which files will move where
3. **Validation**: Checks for potential issues (permissions, conflicts)
4. **Execution**: Moves files to appropriate folders with conflict resolution

## File Categories

FMORG automatically categorizes files by extension:

- **Videos**: `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`
- **Audio**: `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.wma`, `.m4a`
- **Documents**: `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.xls`, `.xlsx`, `.ppt`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.svg`
- **Archives**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`
- **Other**: All other file types

## Usage Examples

### Organizing Media Files

```bash
# Organize a directory of TV shows and movies
fmorg /downloads/media --recursive --min 1

# Only organize if there are at least 3 files with the same title
fmorg /downloads --min 3 --dry-run
```

### Development Workflow

```bash
# Test your organization strategy
fmorg /test/files --dry-run --verbose

# Execute after review
fmorg /test/files --yes

# Organize to a clean structure
fmorg /messy/downloads --output /organized/library --recursive
```

### Batch Operations

```bash
# Quiet mode for scripts
fmorg /auto/organize --quiet --yes

# Detailed logging for troubleshooting
fmorg /problem/files --verbose --dry-run

# Organize current directory with minimal output
fmorg --quiet --yes
```

## Configuration

### Environment Variables

- `FMORG_DEFAULT_MIN`: Default minimum files per folder
- `FMORG_NO_COLOR`: Disable colored output by default
- `FMORG_DEFAULT_DRY_RUN`: Default to dry-run mode

### Example Configuration

```bash
# Set in ~/.bashrc or ~/.zshrc
export FMORG_DEFAULT_MIN=2
export FMORG_NO_COLOR=1
```

## Troubleshooting

### Common Issues

**"Permission denied" errors:**

- Ensure you have read permissions for source files
- Ensure you have write permissions for target directory

**"No files found to organize":**

- Check that files exist in the specified directory
- Use `--recursive` to include subdirectories
- Try `--verbose` to see what files are being scanned

**Files not being grouped as expected:**

- Check that your minimum threshold (`--min`) isn't too high
- Files with no extractable title will be skipped
- Hidden files (starting with dot) are automatically ignored

### Debug Mode

For detailed debugging information:

```bash
fmorg /path/to/files --verbose --dry-run
```

### Getting Help

```bash
# Show help message
fmorg --help

# Show version
fmorg --version
```

## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI interface
- Uses [Colorama](https://pypi.org/project/colorama/) for cross-platform colors
- Tested with [pytest](https://pytest.org/)
- Formatted with [Black](https://black.readthedocs.io/) and linted with [Ruff](https://github.com/astral-sh/ruff)

## License

This project is released under the MIT License.

## Contributing

Contributions are welcome, support is not offered. Please feel free to send pull requests.
