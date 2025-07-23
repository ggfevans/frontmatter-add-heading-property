"""
Pytest configuration and shared fixtures.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import yaml


@pytest.fixture
def temp_vault(tmp_path):
    """Create a temporary vault directory with basic structure."""
    # Create common Obsidian vault directories
    (tmp_path / ".obsidian").mkdir()
    (tmp_path / "00-INBOX").mkdir()
    (tmp_path / "00-INBOX" / "daily-notes").mkdir()
    (tmp_path / "01-PROJECTS").mkdir()
    (tmp_path / "02-AREAS").mkdir()
    (tmp_path / "03-RESOURCES").mkdir()
    (tmp_path / "04-TEMPLATES").mkdir()
    (tmp_path / "99-ARCHIVE").mkdir()
    (tmp_path / "99-ARCHIVE" / "2024").mkdir()
    (tmp_path / "99-ARCHIVE" / "2024" / "01-January").mkdir()
    
    return tmp_path


@pytest.fixture
def sample_markdown_files(temp_vault):
    """Create sample markdown files in the vault."""
    files = {}
    
    # Regular note
    regular_note = temp_vault / "01-PROJECTS" / "project-notes.md"
    regular_note.write_text("""---
title: Project Notes
created: 2024-01-15
tags: [project, notes]
---

# Project Overview

This is a sample project note.
""")
    files['regular_note'] = regular_note
    
    # Daily note
    daily_note = temp_vault / "00-INBOX" / "daily-notes" / "2024-01-15.md"
    daily_note.write_text("""# Daily Note

- Task 1
- Task 2
- Task 3
""")
    files['daily_note'] = daily_note
    
    # Template file
    template_file = temp_vault / "04-TEMPLATES" / "meeting-template.md"
    template_file.write_text("""---
type: template
---

# Meeting Notes Template

Date: {{date}}
Attendees: {{attendees}}

## Agenda

## Notes

## Action Items
""")
    files['template'] = template_file
    
    # Index file
    index_file = temp_vault / "01-PROJECTS" / "index.md"
    index_file.write_text("""# Projects Index

## Active Projects

- [[project-1]]
- [[project-2]]

## Completed Projects

- [[project-3]]
""")
    files['index'] = index_file
    
    # README file
    readme_file = temp_vault / "README.md"
    readme_file.write_text("""# My Obsidian Vault

This is my personal knowledge management system.
""")
    files['readme'] = readme_file
    
    # File with existing heading
    existing_heading = temp_vault / "02-AREAS" / "existing-note.md"
    existing_heading.write_text("""---
title: Existing Note
heading: Custom Heading Already Set
modified: 2024-01-10
---

# Content

This note already has a heading property.
""")
    files['existing_heading'] = existing_heading
    
    # Summary file
    summary_file = temp_vault / "01-PROJECTS" / "web-development-summary.md"
    summary_file.write_text("""# Web Development Project Summary

## Overview

This summarizes the web development project.
""")
    files['summary'] = summary_file
    
    # Special files (should be skipped)
    excalidraw_file = temp_vault / "03-RESOURCES" / "diagram.excalidraw.md"
    excalidraw_file.write_text("Excalidraw data...")
    files['excalidraw'] = excalidraw_file
    
    # File without frontmatter
    no_frontmatter = temp_vault / "03-RESOURCES" / "quick-note.md"
    no_frontmatter.write_text("""# Quick Note

Just a quick note without any frontmatter.
""")
    files['no_frontmatter'] = no_frontmatter
    
    # File with malformed frontmatter
    malformed = temp_vault / "02-AREAS" / "malformed.md"
    malformed.write_text("""---
title: Malformed
tags: [unclosed
invalid yaml here
---

# Content

This has invalid YAML frontmatter.
""")
    files['malformed'] = malformed
    
    return files


@pytest.fixture
def config_file(temp_vault):
    """Create a sample config file in the vault."""
    config_content = {
        'daily_note_patterns': [
            'personal/journal/*',
            'work/standup/*'
        ],
        'template_directories': [
            'my-templates/*',
            'shared-templates/*'
        ],
        'title_case': {
            'preserve_terms': ['PhD', 'USA', 'API', 'GitHub', 'iOS']
        },
        'exclude_patterns': [
            'private/*',
            '.trash/*',
            '*.backup'
        ]
    }
    
    config_path = temp_vault / '.heading-config.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(config_content, f)
    
    return config_path


@pytest.fixture
def mock_logger(monkeypatch):
    """Mock logger to capture log messages."""
    import logging
    
    class LogCapture:
        def __init__(self):
            self.messages = []
            
        def log(self, level, msg, *args, **kwargs):
            self.messages.append((level, msg % args if args else msg))
            
        def debug(self, msg, *args, **kwargs):
            self.log(logging.DEBUG, msg, *args, **kwargs)
            
        def info(self, msg, *args, **kwargs):
            self.log(logging.INFO, msg, *args, **kwargs)
            
        def warning(self, msg, *args, **kwargs):
            self.log(logging.WARNING, msg, *args, **kwargs)
            
        def error(self, msg, *args, **kwargs):
            self.log(logging.ERROR, msg, *args, **kwargs)
    
    return LogCapture()


@pytest.fixture
def preserve_class_attributes():
    """Preserve and restore class attributes that might be modified during tests."""
    from add_headings import HeadingProcessor
    
    # Store original values
    original_daily = HeadingProcessor.DAILY_NOTE_PATTERNS.copy()
    original_template = HeadingProcessor.TEMPLATE_PATTERNS.copy()
    original_preserve = HeadingProcessor.PRESERVE_TERMS.copy()
    
    yield
    
    # Restore original values
    HeadingProcessor.DAILY_NOTE_PATTERNS = original_daily
    HeadingProcessor.TEMPLATE_PATTERNS = original_template
    HeadingProcessor.PRESERVE_TERMS = original_preserve


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )