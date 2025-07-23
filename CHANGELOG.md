# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-07-23

### Added
- Initial release of Obsidian Heading Property Script
- Smart heading generation based on file location and naming patterns
- Support for daily notes, templates, project summaries, index files, and README files
- Title case conversion with technical term preservation
- YAML configuration file support (`.heading-config.yaml`)
- Command-line interface with multiple options
- Dry-run mode for safe preview of changes
- Backup creation functionality
- Comprehensive error handling and logging
- Cross-platform compatibility (Windows, macOS, Linux)
- Full test suite with 95%+ coverage
- Detailed documentation and examples

### Features
- **Daily Notes Detection**: Special formatting for files in `00-INBOX/daily-notes/`, `99-ARCHIVE/*/`, etc.
- **Template Recognition**: Identifies template files and formats them appropriately
- **Project Summary Files**: Handles `-summary.md` files with special formatting
- **Smart Title Case**: Converts kebab-case to readable names while preserving technical terms
- **Plugin Integration**: Creates heading properties for Omnisearch, Quick Switcher, and other Obsidian plugins
- **Safety Features**: Skip existing headings, create backups, comprehensive error handling
- **Flexible Configuration**: Command-line options and YAML config file support

### Technical
- Python 3.7+ compatibility
- UTF-8 encoding support
- Robust YAML frontmatter parsing
- Efficient processing for large vaults
- Memory-optimized for thousands of files

[Unreleased]: https://github.com/username/obsidian-heading-script/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/username/obsidian-heading-script/releases/tag/v1.0.0