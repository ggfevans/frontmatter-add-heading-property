# Obsidian Heading Property Script

A Python script that automatically adds `heading` properties to the frontmatter of all Markdown files in an Obsidian vault. This enables better file discovery and display in Obsidian plugins like **Omnisearch**, **Quick Switcher**, and various graph/search tools that use the `heading` property as a display name.

## Why Use This Script?

Many Obsidian users maintain systematic file naming conventions for organization (like `01-PROJECTS/backup-system-implementation.md` or `2025-07-22.md` for daily notes), but these technical filenames aren't ideal for searching or display purposes. 

This script solves that problem by:

- **Preserving your existing file naming system** - No need to rename files or reorganize your vault
- **Enhancing plugin compatibility** - Plugins like Omnisearch, Quick Switcher, and dataview can display human-readable names
- **Improving search experience** - Find files by their readable display names while keeping systematic file organization
- **Maintaining automation workflows** - Your existing scripts, templates, and organizational systems continue to work unchanged

**Example Benefits:**
- File: `01-PROJECTS/backup-system-implementation.md` → Display: "Backup System Implementation"
- File: `2025-07-22.md` → Display: "Daily Note 2025-07-22" 
- File: `project-management-summary.md` → Display: "project-management - Summary"

The script intelligently generates heading values based on file location, naming patterns, and content structure, giving you the best of both worlds: systematic organization and human-readable display names.

## Features

- **Plugin-Friendly Display Names**: Creates `heading` properties that plugins like Omnisearch and Quick Switcher use for display
- **Smart Heading Generation**: Automatically generates appropriate heading values based on file context and location
- **Preserves File Organization**: Works with your existing file naming and folder structure - no renaming required
- **Daily Notes Detection**: Special formatting for daily note files in configured directories
- **Template Recognition**: Identifies and formats template files appropriately
- **Title Case Conversion**: Optional intelligent title case conversion with technical term preservation
- **Flexible Configuration**: Command-line options and YAML configuration file support
- **Safety Features**: Dry-run mode, backup creation, and comprehensive error handling
- **Robust Processing**: Handles edge cases, malformed frontmatter, and large vaults efficiently

## Installation

### Prerequisites

- Python 3.7 or higher
- PyYAML library

### Setup

1. Clone or download the script:
```bash
git clone <repository-url>
cd obsidian-heading-script
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install pyyaml
```

## Quick Start

```bash
# Preview what changes will be made (recommended first step)
python add_headings.py /path/to/your/obsidian/vault --dry-run --verbose

# Process entire vault with title case conversion for better display names
python add_headings.py /path/to/your/obsidian/vault --title-case

# Create backups and process with detailed logging
python add_headings.py /path/to/your/obsidian/vault --backup --title-case --verbose
```

**After running the script**, your files will have `heading` properties that plugins can use:

- **Omnisearch**: Will display the heading value instead of filename in search results
- **Quick Switcher**: Shows readable names when switching between files  
- **Graph View**: Uses heading values for node labels (if configured)
- **Dataview**: Can query and display files using the heading property

## Heading Generation Rules

The script applies different heading formats based on file characteristics:

### 1. Daily Notes
Files in daily note directories get special formatting:
- **Directories**: `00-INBOX/daily-notes/`, `99-ARCHIVE/2025/05-May/`, `journal/`
- **Format**: `Daily Note [filename]`
- **Examples**:
  - `00-INBOX/daily-notes/2025-07-22.md` → `heading: Daily Note 2025-07-22`
  - `99-ARCHIVE/2025/05-May/2025-05-15.md` → `heading: Daily Note 2025-05-15`

### 2. Project Summary Files
Files ending with `-summary.md`:
- **Format**: `[project-name] - Summary`
- **Examples**:
  - `backup-system-summary.md` → `heading: backup-system - Summary`
  - `website-redesign-summary.md` → `heading: website-redesign - Summary`

### 3. Template Files
Files in template directories or with "template" in the name:
- **Directories**: `04-TEMPLATES/`, `templates/`
- **Format**: `Template: [filename]`
- **Examples**:
  - `04-TEMPLATES/project-template.md` → `heading: Template: project-template`
  - `daily-note-template.md` → `heading: Template: daily-note-template`

### 4. Index Files
Files named "index":
- **Format**: `[parent-folder-name] - Index`
- **Example**: `/01-PROJECTS/web-dev/index.md` → `heading: web-dev - Index`

### 5. README Files
Files named "README" (case-insensitive):
- **Format**: `[parent-folder-name] - README`
- **Example**: `/projects/backup-system/README.md` → `heading: backup-system - README`

### 6. Smart Title Case (Optional)
When `--title-case` is enabled:
- Converts kebab-case to Title Case: `backup-system-implementation` → `Backup System Implementation`
- Preserves technical terms: `API`, `UI`, `CSS`, `HTML`, `JSON`, etc.
- Removes organizational prefixes: `01-PROJECTS` → `Projects`

### 7. Default Behavior
For all other files, uses the filename without extension as the heading value.

## Command-Line Options

```bash
python add_headings.py [VAULT_PATH] [OPTIONS]
```

### Required Arguments
- `VAULT_PATH`: Path to your Obsidian vault directory

### Optional Arguments

| Option | Description | Default |
|--------|-------------|---------|
| `--dry-run` | Preview changes without modifying files | False |
| `--backup` | Create .bak files before modification | False |
| `--verbose`, `-v` | Enable detailed output | False |
| `--skip-existing` | Skip files with existing heading property | True |
| `--title-case` | Convert filenames to smart title case | False |
| `--preserve-case` | Keep original filename casing | False |
| `--exclude-dirs` | Comma-separated directories to exclude | None |
| `--include-patterns` | Additional daily note directory patterns | None |

### Examples

```bash
# Basic processing with preview
python add_headings.py /path/to/vault --dry-run --verbose

# Process with backups and title case
python add_headings.py /path/to/vault --backup --title-case

# Exclude specific directories
python add_headings.py /path/to/vault --exclude-dirs "04-TEMPLATES,drafts,archive"

# Include custom daily note patterns
python add_headings.py /path/to/vault --include-patterns "**/daily/**,**/journal/**"

# Process only files without existing headings
python add_headings.py /path/to/vault --skip-existing
```

## Configuration File

Create a `.heading-config.yaml` file in your vault root for advanced configuration:

```yaml
# Custom daily note directory patterns
daily_note_patterns:
  - "00-INBOX/daily-notes/"
  - "99-ARCHIVE/*/??-*/"
  - "journal/"
  - "daily/"

# Project summary file suffix
project_summary_suffix: "-summary"

# Title case configuration
title_case:
  enabled: true
  preserve_terms: 
    - "API"
    - "UI" 
    - "CSS"
    - "HTML"
    - "JSON"
    - "YAML"
    - "REST"
    - "GraphQL"

# Template directories
template_directories:
  - "04-TEMPLATES/"
  - "templates/"
  - "template/"

# Exclusion patterns
exclude_patterns:
  - "**/.obsidian/**"
  - "**/drafts/**"
  - "**/*.excalidraw.md"
  - "**/temp/**"
```

## Output and Logging

The script provides clear feedback about its progress:

```
Processing vault: /path/to/vault
✓ Added heading to: daily-note.md → "Daily Note 2025-07-22"
⚠ Skipped (has heading): project-summary.md  
✗ Error reading: corrupted-file.md

==================================================
SUMMARY
==================================================
✓ Processed: 45
⚠ Skipped (existing): 3
⚠ Skipped (special): 2
✗ Errors: 1

Total files: 51
```

## Safety Features

### Dry Run Mode
Use `--dry-run` to preview all changes before applying them:
```bash
python add_headings.py /path/to/vault --dry-run --verbose
```

### Backup Creation
Create backup files before modification:
```bash
python add_headings.py /path/to/vault --backup
```

### Skip Existing Headers
By default, files with existing `heading` properties are skipped to prevent overwriting custom values.

## Edge Cases Handled

- **Empty files**: Gracefully handled without errors
- **Malformed YAML**: Invalid frontmatter is detected and reported
- **Binary files**: Files with `.md` extension but binary content are skipped
- **Special Obsidian files**: `.canvas` and `.excalidraw.md` files are automatically excluded
- **Unicode content**: Full UTF-8 support for international characters
- **Large files**: Efficient processing for vaults with thousands of files
- **Symbolic links**: Properly handled without infinite loops
- **Read-only files**: Appropriate error handling and reporting

## Development and Testing

### Running Tests

The project includes a comprehensive test suite:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=add_headings --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run code quality checks
make lint       # Run flake8 linting
make format     # Format code with black
make typecheck  # Run mypy type checking

# Run all checks
make test-all
```

## File Structure

```
obsidian-heading-script/
├── add_headings.py          # Main script
├── README.md               # This file
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Development dependencies
├── pytest.ini            # Test configuration
├── Makefile              # Development shortcuts
└── tests/                # Test suite
    ├── conftest.py       # Test fixtures
    ├── test_heading_processor.py  # Main tests
    ├── test_config.py    # Configuration tests
    ├── test_utils.py     # Utility tests
    ├── fixtures/         # Sample test files
    └── README.md         # Test documentation
```

## Troubleshooting

### Common Issues

**Permission Errors**
- Ensure you have read/write access to the vault directory
- On Windows, run as administrator if needed
- Check file permissions for read-only files

**YAML Errors**
- Validate your `.heading-config.yaml` syntax
- Use online YAML validators if needed
- Check for proper indentation (spaces, not tabs)

**Memory Issues with Large Vaults**
- Process directories in smaller batches
- Use `--exclude-dirs` to skip large unnecessary directories
- Close other applications to free memory

**Encoding Issues**
- Ensure files are saved in UTF-8 encoding
- Use `--verbose` flag to identify problematic files
- Check for BOM (Byte Order Mark) in files

### Debug Mode

Enable verbose logging for troubleshooting:
```bash
python add_headings.py /path/to/vault --verbose --dry-run
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `make test-all`
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Changelog

### v1.0.0
- Initial release with core functionality
- Support for all heading generation rules
- Configuration file support
- Comprehensive test suite
- Full cross-platform compatibility