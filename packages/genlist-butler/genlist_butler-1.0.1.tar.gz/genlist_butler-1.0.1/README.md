# GenList Butler

[![Tests](https://github.com/TuesdayUkes/genlist/actions/workflows/test.yml/badge.svg)](https://github.com/TuesdayUkes/genlist/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/genlist.svg)](https://badge.fury.io/py/genlist)
[![Python versions](https://img.shields.io/pypi/pyversions/genlist.svg)](https://pypi.org/project/genlist/)

A command-line tool for generating HTML music archives from ChordPro files, PDFs, and other music notation files. Originally created for the Tuesday Ukulele Group, this tool scans a directory tree of music files and generates a searchable, filterable HTML catalog.

## Features

- 📁 **Smart File Discovery**: Automatically finds ChordPro (.chopro, .cho), PDF, MuseScore, and other music files
- 🔍 **Version Control Integration**: Uses git timestamps to identify the newest version of duplicate files
- 🎯 **Filtering Options**: Hide older versions, mark easy songs, exclude specific files
- 📄 **PDF Generation**: Optional automatic PDF generation from ChordPro files
- 🌐 **Interactive HTML**: Generates searchable, filterable HTML catalogs with modern UI
- 🎨 **Beautiful Styling**: Includes Tuesday Ukes' professional HTML template - no configuration needed!
- ⚡ **Fast**: Optimized git operations for quick catalog generation

## Requirements

- Python 3.12 or later
- Git (for version tracking features)

## Installation

Install using pipx (recommended):

```bash
pipx install genlist
```

Or using pip:

```bash
pip install genlist
```

## Usage

Basic usage:

```bash
genlist <music_folder> <output_file>
```

### Examples

Generate a catalog with default settings (newest versions only):

```bash
genlist ./music index.html
```

Show all file versions:

```bash
genlist ./music index.html --filter none
```

Hide only files marked with `.hide` extension:

```bash
genlist ./music index.html --filter hidden
```

Generate PDFs from ChordPro files before cataloging:

```bash
genlist ./music index.html --genPDF
```

### Options

- `musicFolder` - Path to the directory containing music files
- `outputFile` - Path where the HTML catalog will be written
- `--filter [none|hidden|timestamp]` - Filtering method (default: timestamp)
  - `none`: Show all files
  - `hidden`: Hide files with `.hide` extension
  - `timestamp`: Show only newest versions based on git history
- `--intro / --no-intro` - Include/exclude introduction section (default: include)
- `--genPDF / --no-genPDF` - Generate PDFs from ChordPro files (default: no)
- `--forcePDF / --no-forcePDF` - Regenerate all PDFs even if they exist (default: no)

### File Markers

GenList Butler uses special marker files:

- **`.hide` files**: Create a file with `.hide` extension (e.g., `song.hide`) to hide all files with the same base name from the catalog
- **`.easy` files**: Create a file with `.easy` extension (e.g., `song.easy`) to mark all files with the same base name as "easy songs" for filtering

### Custom HTML Styling

GenList-Butler includes a beautiful, professional HTML template out of the box (Tuesday Ukes' styling). However, you can customize it:

1. Create your own `HTMLheader.txt` file in your working directory
2. Run genlist from that directory
3. Your custom header will be used instead of the default

The generated HTML will use your custom styling while maintaining all the interactive search/filter functionality.

## Requirements

- Python 3.8+
- Git (for timestamp-based filtering)
- ChordPro (optional, for PDF generation)

## How It Works

1. **Scans** the music folder recursively for supported file types
2. **Groups** files by song title (normalized, ignoring articles)
3. **Filters** based on the selected method:
   - Uses git history to find the newest version of each file
   - Respects `.hide` marker files
   - Processes `.easy` marker files for special highlighting
4. **Generates** an interactive HTML page with:
   - Searchable song list
   - Download links for all file formats
   - Optional filtering for easy songs
   - Toggle for showing all versions

## Development

To contribute or modify:

```bash
# Clone the repository
git clone https://github.com/TuesdayUkes/genlist.git
cd genlist

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT License - see LICENSE file for details

## Credits

Created for the Tuesday Ukulele Group (https://tuesdayukes.org/)

Maintained by the TUG community.
