# ncbi-tree

[![PyPI version](https://badge.fury.io/py/ncbi-tree.svg)](https://badge.fury.io/py/ncbi-tree)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

**ncbi-tree** is an open source, cross-platform command-line tool for downloading the latest NCBI taxonomy database and converting it to Newick tree format (.tre), with optional plain-text visualization (.txt).

## Quick Start

```bash
pip install ncbi-tree
ncbi-tree ./output
```

That's it! The tool will download the latest NCBI taxonomy, generate phylogenetic trees, and create detailed reports.

## Features

- [x] **Automatic Download**: Fetches the latest taxonomy data from NCBI FTP servers  
- [x] **Version Tracking**: Automatically detects and records the exact server version  
- [x] **Smart Caching**: Skips re-download and re-extraction when files already exist  
- [x] **Progress Bars**: Visual feedback for downloads and extraction using tqdm  
- [x] **Multiple Output Formats**: Newick with IDs only, Newick with names, text tree, TSV mapping  
- [x] **Comprehensive Reports**: Detailed taxonomy analysis with rank distribution and depth statistics  
- [x] **Name Sanitization**: By default inital letter is capitalized and space is replaced by `-`. Configurable name formatting with --no-sanitize option  
- [x] **Interactive Mode**: Optional files generated on demand without re-reading data  
- [x] **Merged Taxa Support**: Handles merged taxonomy IDs from merged.dmp  
- [x] **Cross-Platform**: Works on Linux, macOS, and Windows  
- [x] **Memory Efficient**: Reuses data in memory for optional file generation  
- [x] **Error Handling**: Comprehensive error catching with user-friendly messages  

## Installation

```bash
pip install ncbi-tree
```

## Usage

### Basic Usage

```bash
# Download and build taxonomy tree with default settings
ncbi-tree ./output

# Clean up intermediate files after processing
ncbi-tree ./output --no-cache

# Disable name sanitization (keep original spaces)
ncbi-tree ./output --no-sanitize

# Use custom download URL
ncbi-tree ./output --url https://custom-mirror.org/taxdump.tar.gz

# Combined options
ncbi-tree ./output --no-cache --no-sanitize
```

### Help

```bash
ncbi-tree --help
ncbi-tree --version
```

## Output Files

### Core Files (Generated Automatically)

1. **`output.NCBI.tree.tre`** - Newick tree with NCBI taxonomy IDs only
2. **`output.NCBI.report.txt`** - Exploratory taxonomy analysis and statistics
3. **`version.txt`** - Server timestamped version for downloaded taxdump.tar.gz

### Optional Files (User Prompted)

After core files are generated, you will be prompted:
```
Would you like to generate optional files (output.NCBI.tree.txt, output.NCBI.named.tree.tre, output.NCBI.ID.to.name.tsv)? [y/N]:
```

If you answer `y`, additional files will be generated **without re-reading data**:

4. **`output.NCBI.tree.txt`** - Plain-text tree with Unicode box-drawing
5. **`output.NCBI.named.tree.tre`** - Newick tree with rank:id:name labels
6. **`output.NCBI.ID.to.name.tsv`** - TSV mapping of IDs to names (TaxID, Name, Rank)

## Name Sanitization

By default, taxon names are sanitized for consistent display:
- Spaces replaced with `-`
- Existing `-` escaped as `<->`
- Title case applied
- Special characters removed

**Default (sanitized):**
```
"Human;Homo-Sapiens"
"Norway-Rat;Rattus-Norvegicus"
```

**With `--no-sanitize` flag:**
```
"human; Homo sapiens"
"Norway rat; Rattus norvegicus"
```

## Advanced Configuration

### Custom Name Display

To customize which name types are displayed, edit `NAME_PRIORITIES` in `ncbi_tree/core.py`:

```python
# Default: both common and scientific names
NAME_PRIORITIES = {"genbank common name": 0, "scientific name": 1}
# Result: "Human; Homo sapiens"

# Scientific name only (disable common name)
NAME_PRIORITIES = {"genbank common name": -1, "scientific name": 0}
# Result: "Homo sapiens"

# Common name only (disable scientific name)
NAME_PRIORITIES = {"genbank common name": 0, "scientific name": -1}
# Result: "Human"
```

**Note:** Priority value `-1` disables that name type, `>= 0` enables it (lower number = higher priority).

## Example

```bash
$ ncbi-tree ./ncbi_output

Output files:
  - ./ncbi_output/output.NCBI.tree.tre
  - ./ncbi_output/output.NCBI.tree.txt
  - ./ncbi_output/version.txt
```

## Requirements

- Python 3.8 or higher
- requests >= 2.25.0
- tqdm >= 4.50.0

## Technical Details

### Data Source
- **Primary**: NCBI Taxonomy Database (https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/)
- **Updates**: Automatic detection of latest version with timestamp tracking
- **Size**: ~70-100 MB compressed, ~2.7M+ taxonomy entries at the time of writing (October 2025)
- **Format**: NCBI taxdump format (nodes.dmp, names.dmp, merged.dmp)

### Output Formats
1. **Newick (`.tre`)**: Standard phylogenetic tree format compatible with all major tree viewers
2. **Text Tree (`.txt`)**: Unicode-based visualization for terminal/text viewing
3. **TSV Mapping (`.tsv`)**: Tabular format for database integration and lookups
4. **Report (`.txt`)**: Statistical analysis with rank distribution and depth metrics

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0).

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Acknowledgments

- NCBI for providing the taxonomy database