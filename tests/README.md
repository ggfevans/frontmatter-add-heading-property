# Test Suite for add_headings.py

This directory contains a comprehensive test suite for the `add_headings.py` script, which adds heading properties to Obsidian markdown files.

## Structure

```
tests/
├── README.md                    # This file
├── conftest.py                  # Pytest fixtures and configuration
├── test_heading_processor.py    # Tests for HeadingProcessor class
├── test_config.py              # Tests for configuration handling
├── test_utils.py               # Tests for utility functions and edge cases
└── fixtures/                   # Sample files for testing
    ├── sample_note.md
    ├── daily_note.md
    ├── template_note.md
    ├── malformed_frontmatter.md
    ├── no_frontmatter.md
    ├── empty_frontmatter.md
    └── sample_config.yaml
```

## Test Categories

### Unit Tests (`test_*.py`)
- **HeadingProcessor Tests**: Core functionality testing
  - Frontmatter parsing and reconstruction
  - Heading value generation rules
  - File processing logic
  - Directory exclusion logic
  - Title case conversion

- **Configuration Tests**: Configuration handling
  - Config dataclass initialization
  - YAML config file loading
  - Command-line argument merging
  - Pattern and exclusion handling

- **Utility Tests**: Edge cases and utilities
  - CLI argument parsing
  - Error handling
  - Logging functionality
  - Special character handling
  - File system operations

### Test Fixtures
Located in `fixtures/` directory:
- `sample_note.md` - Standard note with valid frontmatter
- `daily_note.md` - Example daily note without frontmatter
- `template_note.md` - Template file example
- `malformed_frontmatter.md` - Invalid YAML for error testing
- `no_frontmatter.md` - Plain markdown without frontmatter
- `empty_frontmatter.md` - Empty frontmatter block
- `sample_config.yaml` - Example configuration file

## Running Tests

### Prerequisites
Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Basic Usage
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_heading_processor.py

# Run specific test method
pytest tests/test_heading_processor.py::TestHeadingProcessor::test_generate_heading_value_daily_note
```

### Test Categories
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests  
pytest -m integration

# Run fast tests (exclude slow tests)
pytest -m "not slow"

# Run smoke tests
pytest -m smoke
```

### Coverage Reports
```bash
# Run with coverage
pytest --cov=add_headings

# Generate HTML coverage report
pytest --cov=add_headings --cov-report=html

# Coverage with missing lines
pytest --cov=add_headings --cov-report=term-missing
```

### Using the Test Runner
```bash
# Use the custom test runner
python run_tests.py                 # All tests
python run_tests.py --unit          # Unit tests only
python run_tests.py --coverage      # With coverage
python run_tests.py --lint          # Code quality checks
python run_tests.py --all           # Everything
```

### Using Makefile
```bash
make test                # Run all tests
make test-unit          # Unit tests only
make test-coverage      # With coverage
make lint               # Code quality
make all                # Tests + linting
```

## Test Scenarios Covered

### Core Functionality
- ✅ Frontmatter parsing (valid, invalid, empty, missing)
- ✅ YAML reconstruction with proper formatting
- ✅ Heading generation for all file types:
  - Daily notes (multiple directory patterns)
  - Project summaries
  - Template files
  - Index files
  - README files
  - Regular files
- ✅ Title case conversion with preserved terms
- ✅ File system operations (reading, writing, backup)

### Configuration Handling
- ✅ Config dataclass initialization
- ✅ YAML config file loading and validation
- ✅ Command-line argument parsing
- ✅ Config merging (CLI args + file config)
- ✅ Pattern matching and exclusions

### Edge Cases and Error Handling
- ✅ Malformed YAML frontmatter
- ✅ Empty and missing frontmatter
- ✅ Unicode content handling
- ✅ Special characters in filenames
- ✅ Windows path handling
- ✅ File permission errors
- ✅ Concurrent file modification
- ✅ Very long frontmatter
- ✅ Empty vault directories

### Integration Scenarios
- ✅ Full vault processing
- ✅ Dry run mode
- ✅ Backup creation
- ✅ Skip existing headings
- ✅ Directory exclusions
- ✅ Custom patterns from config files

## Test Fixtures and Mocking

The test suite uses several approaches for testing:

### Temporary Directories
- Uses `tmp_path` fixture for isolated file system testing
- Creates realistic Obsidian vault structures
- Automatically cleaned up after tests

### Mocking
- Logger output capture for testing logging
- File system operations mocking
- Command-line argument simulation

### Fixtures
- Shared test data in `fixtures/` directory
- Realistic markdown files with various frontmatter states
- Sample configuration files

## Code Quality Standards

### Coverage Goals
- Target: >95% code coverage
- All major code paths tested
- Error conditions covered
- Edge cases included

### Test Quality
- Clear test names describing behavior
- Isolated tests (no dependencies between tests)
- Comprehensive assertions
- Proper setup and teardown

### Performance
- Fast unit tests (<100ms each)
- Slow tests marked with `@pytest.mark.slow`
- Parallel execution support

## Continuous Integration

The test suite is designed to work with CI/CD systems:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements-dev.txt
    pytest --cov=add_headings --cov-report=xml
    
- name: Code quality
  run: |
    flake8 add_headings.py tests/
    black --check add_headings.py tests/
    mypy add_headings.py
```

## Adding New Tests

When adding new functionality:

1. **Write tests first** (TDD approach)
2. **Cover all code paths** including error cases
3. **Use appropriate markers** (`@pytest.mark.unit`, etc.)
4. **Follow naming conventions** (`test_function_name_scenario`)
5. **Add fixtures** to `conftest.py` if reusable
6. **Update this README** if adding new test categories

### Test Template
```python
def test_new_functionality_success_case(self, processor):
    """Test new functionality with valid input."""
    # Arrange
    input_data = "test input"
    expected = "expected result"
    
    # Act
    result = processor.new_function(input_data)
    
    # Assert
    assert result == expected
    assert processor.stats['processed'] == 1

def test_new_functionality_error_case(self, processor):
    """Test new functionality error handling."""
    with pytest.raises(ValueError, match="Expected error message"):
        processor.new_function("invalid input")
```

## Troubleshooting

### Common Issues

**Tests fail with import errors:**
```bash
pip install -e .  # Install package in development mode
```

**Coverage reports missing:**
```bash
pip install pytest-cov coverage
```

**Windows path issues:**
- Tests account for Windows path separators
- Use `Path` objects instead of string concatenation

**Temporary file cleanup:**
- Tests use `tmp_path` fixture for automatic cleanup
- Manual cleanup in teardown methods if needed

### Debugging Tests
```bash
# Run with pdb debugger
pytest --pdb

# Run single test with verbose output
pytest -v -s tests/test_heading_processor.py::test_specific_function

# Show local variables in failures
pytest --tb=long

# Capture print statements
pytest -s
```

## Contributing

When contributing to the test suite:

1. Ensure all new code has corresponding tests
2. Run the full test suite before submitting
3. Update test documentation for new features
4. Follow the existing test patterns and naming conventions
5. Add appropriate test markers for categorization