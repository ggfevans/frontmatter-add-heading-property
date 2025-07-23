"""
Tests for HeadingProcessor class.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from collections import Counter
import tempfile
import shutil

from add_headings import HeadingProcessor, Config


class TestHeadingProcessor:
    """Test suite for HeadingProcessor class."""
    
    @pytest.fixture
    def config(self, tmp_path):
        """Create a basic config for testing."""
        return Config(
            vault_path=tmp_path,
            dry_run=False,
            backup=False,
            verbose=False,
            skip_existing=True,
            title_case=False,
            preserve_case=False,
            exclude_dirs=[],
            include_patterns=[]
        )
    
    @pytest.fixture
    def processor(self, config):
        """Create a HeadingProcessor instance."""
        return HeadingProcessor(config)
    
    def test_init(self, config):
        """Test HeadingProcessor initialization."""
        processor = HeadingProcessor(config)
        assert processor.config == config
        assert isinstance(processor.stats, Counter)
        assert processor.stats['processed'] == 0
        assert processor.stats['errors'] == 0
    
    def test_parse_frontmatter_with_valid_yaml(self, processor):
        """Test parsing valid YAML frontmatter."""
        content = """---
title: Test Document
tags: [test, sample]
---

# Main Content

This is the body.
"""
        frontmatter, body = processor._parse_frontmatter(content)
        
        assert frontmatter == {'title': 'Test Document', 'tags': ['test', 'sample']}
        assert body.strip() == "# Main Content\n\nThis is the body."
    
    def test_parse_frontmatter_without_frontmatter(self, processor):
        """Test parsing content without frontmatter."""
        content = """# Main Content

This is the body without frontmatter.
"""
        frontmatter, body = processor._parse_frontmatter(content)
        
        assert frontmatter is None
        assert body == content
    
    def test_parse_frontmatter_with_invalid_yaml(self, processor):
        """Test parsing invalid YAML frontmatter."""
        content = """---
title: Test Document
invalid: [unclosed bracket
---

# Main Content
"""
        frontmatter, body = processor._parse_frontmatter(content)
        
        assert frontmatter is None
        assert body == content
    
    def test_parse_frontmatter_empty_content(self, processor):
        """Test parsing empty content."""
        frontmatter, body = processor._parse_frontmatter("")
        assert frontmatter is None
        assert body == ""
    
    def test_reconstruct_content(self, processor):
        """Test reconstructing content with updated frontmatter."""
        frontmatter = {'title': 'Test', 'heading': 'New Heading'}
        body = "# Content\n\nThis is the body."
        
        result = processor._reconstruct_content(frontmatter, body)
        
        assert result.startswith("---\n")
        assert "title: Test" in result
        assert "heading: New Heading" in result
        assert result.endswith("---\n# Content\n\nThis is the body.")
    
    def test_generate_heading_value_daily_note(self, processor):
        """Test heading generation for daily notes."""
        # Test various daily note paths
        test_cases = [
            (Path("vault/00-INBOX/daily-notes/2024-01-15.md"), "Daily Note 2024-01-15"),
            (Path("vault/99-ARCHIVE/2024/01-January/2024-01-15.md"), "Daily Note 2024-01-15"),
            (Path("vault/daily-notes/2024-01-15.md"), "Daily Note 2024-01-15"),
            (Path("vault/journal/2024-01-15.md"), "Daily Note 2024-01-15"),
        ]
        
        for file_path, expected in test_cases:
            processor.config.vault_path = Path("vault")
            result = processor._generate_heading_value(file_path)
            assert result == expected
    
    def test_generate_heading_value_project_summary(self, processor):
        """Test heading generation for project summary files."""
        processor.config.vault_path = Path("vault")
        
        # Without title case
        file_path = Path("vault/projects/my-project-summary.md")
        result = processor._generate_heading_value(file_path)
        assert result == "my-project - Summary"
        
        # With title case
        processor.config.title_case = True
        result = processor._generate_heading_value(file_path)
        assert result == "My Project - Summary"
    
    def test_generate_heading_value_template(self, processor):
        """Test heading generation for template files."""
        processor.config.vault_path = Path("vault")
        
        test_cases = [
            (Path("vault/04-TEMPLATES/meeting-template.md"), "Template: meeting-template"),
            (Path("vault/templates/project-template.md"), "Template: project-template"),
            (Path("vault/my-template.md"), "Template: my-template"),
        ]
        
        for file_path, expected in test_cases:
            result = processor._generate_heading_value(file_path)
            assert result == expected
    
    def test_generate_heading_value_index(self, processor):
        """Test heading generation for index files."""
        processor.config.vault_path = Path("vault")
        
        # Without title case
        file_path = Path("vault/projects/index.md")
        result = processor._generate_heading_value(file_path)
        assert result == "projects - Index"
        
        # With title case
        processor.config.title_case = True
        result = processor._generate_heading_value(file_path)
        assert result == "Projects - Index"
    
    def test_generate_heading_value_readme(self, processor):
        """Test heading generation for README files."""
        processor.config.vault_path = Path("vault")
        
        # Without title case
        file_path = Path("vault/projects/README.md")
        result = processor._generate_heading_value(file_path)
        assert result == "projects - README"
        
        # With title case and organizational prefix
        processor.config.title_case = True
        file_path = Path("vault/01-projects/README.md")
        result = processor._generate_heading_value(file_path)
        assert result == "Projects - README"
    
    def test_generate_heading_value_default(self, processor):
        """Test heading generation for regular files."""
        processor.config.vault_path = Path("vault")
        
        # Without title case
        file_path = Path("vault/notes/my-note.md")
        result = processor._generate_heading_value(file_path)
        assert result == "my-note"
        
        # With title case
        processor.config.title_case = True
        result = processor._generate_heading_value(file_path)
        assert result == "My Note"
    
    def test_is_daily_note(self, processor):
        """Test daily note detection."""
        test_cases = [
            ("00-INBOX/daily-notes/2024-01-15.md", True),
            ("99-ARCHIVE/2024/01-January/2024-01-15.md", True),
            ("daily-notes/note.md", True),
            ("journal/entry.md", True),
            ("projects/meeting-notes.md", False),
            ("templates/daily-template.md", False),
        ]
        
        for path, expected in test_cases:
            result = processor._is_daily_note(path)
            assert result == expected, f"Path {path} should be {expected}"
    
    def test_is_template_file(self, processor):
        """Test template file detection."""
        test_cases = [
            ("04-TEMPLATES/meeting.md", "meeting", True),
            ("templates/project.md", "project", True),
            ("notes/meeting-template.md", "meeting-template", True),
            ("notes/template-example.md", "template-example", True),
            ("notes/regular-note.md", "regular-note", False),
        ]
        
        for rel_path, filename, expected in test_cases:
            result = processor._is_template_file(rel_path, filename)
            assert result == expected
    
    def test_to_title_case(self, processor):
        """Test title case conversion."""
        test_cases = [
            ("my-note", "My Note"),
            ("my_note", "My Note"),
            ("01-projects", "Projects"),
            ("api-documentation", "API Documentation"),
            ("ios-development", "iOS Development"),
            ("html-css-guide", "HTML CSS Guide"),
            ("README", "README"),
            ("test-API-guide", "Test API Guide"),
        ]
        
        for input_text, expected in test_cases:
            result = processor._to_title_case(input_text)
            assert result == expected
    
    def test_should_exclude_directory(self, processor):
        """Test directory exclusion logic."""
        # Test .obsidian exclusion
        assert processor._should_exclude_directory(Path(".obsidian"))
        assert processor._should_exclude_directory(Path("notes/.obsidian/config"))
        
        # Test custom exclusions
        processor.config.exclude_dirs = ["archive", "trash"]
        assert processor._should_exclude_directory(Path("archive/old"))
        assert processor._should_exclude_directory(Path("projects/trash"))
        assert not processor._should_exclude_directory(Path("notes/important"))
    
    def test_find_markdown_files(self, tmp_path):
        """Test finding markdown files in vault."""
        # Create test directory structure
        (tmp_path / "notes").mkdir()
        (tmp_path / ".obsidian").mkdir()
        (tmp_path / "templates").mkdir()
        
        # Create test files
        (tmp_path / "notes" / "note1.md").write_text("# Note 1")
        (tmp_path / "notes" / "note2.md").write_text("# Note 2")
        (tmp_path / ".obsidian" / "config.md").write_text("Config")
        (tmp_path / "templates" / "template.md").write_text("Template")
        (tmp_path / "notes" / "drawing.excalidraw.md").write_text("Drawing")
        
        config = Config(vault_path=tmp_path)
        processor = HeadingProcessor(config)
        
        md_files = processor._find_markdown_files()
        
        # Should find 3 files (excluding .obsidian and excalidraw)
        assert len(md_files) == 3
        
        file_names = [f.name for f in md_files]
        assert "note1.md" in file_names
        assert "note2.md" in file_names
        assert "template.md" in file_names
        assert "config.md" not in file_names
        assert "drawing.excalidraw.md" not in file_names
    
    def test_process_file_new_heading(self, tmp_path):
        """Test processing a file without existing heading."""
        # Create test file
        test_file = tmp_path / "test-note.md"
        test_file.write_text("""---
title: Test Note
tags: [test]
---

# Content

This is a test note.
""")
        
        config = Config(vault_path=tmp_path)
        processor = HeadingProcessor(config)
        
        processor._process_file(test_file)
        
        # Check file was updated
        content = test_file.read_text()
        assert "heading: test-note" in content
        assert processor.stats['processed'] == 1
    
    def test_process_file_existing_heading(self, tmp_path):
        """Test processing a file with existing heading."""
        # Create test file with existing heading
        test_file = tmp_path / "test-note.md"
        test_file.write_text("""---
title: Test Note
heading: Existing Heading
---

# Content
""")
        
        config = Config(vault_path=tmp_path, skip_existing=True)
        processor = HeadingProcessor(config)
        
        processor._process_file(test_file)
        
        # Check file was not modified
        content = test_file.read_text()
        assert "heading: Existing Heading" in content
        assert "heading: test-note" not in content
        assert processor.stats['skipped_existing'] == 1
    
    def test_process_file_no_frontmatter(self, tmp_path):
        """Test processing a file without frontmatter."""
        # Create test file without frontmatter
        test_file = tmp_path / "test-note.md"
        test_file.write_text("# Content\n\nThis is a test note.")
        
        config = Config(vault_path=tmp_path)
        processor = HeadingProcessor(config)
        
        processor._process_file(test_file)
        
        # Check frontmatter was added
        content = test_file.read_text()
        assert content.startswith("---\n")
        assert "heading: test-note" in content
        assert processor.stats['processed'] == 1
    
    def test_process_file_with_backup(self, tmp_path):
        """Test processing a file with backup enabled."""
        # Create test file
        test_file = tmp_path / "test-note.md"
        original_content = "# Original Content"
        test_file.write_text(original_content)
        
        config = Config(vault_path=tmp_path, backup=True)
        processor = HeadingProcessor(config)
        
        processor._process_file(test_file)
        
        # Check backup was created
        backup_file = tmp_path / "test-note.md.bak"
        assert backup_file.exists()
        assert backup_file.read_text() == original_content
    
    def test_process_file_dry_run(self, tmp_path):
        """Test processing in dry run mode."""
        # Create test file
        test_file = tmp_path / "test-note.md"
        original_content = "# Content"
        test_file.write_text(original_content)
        
        config = Config(vault_path=tmp_path, dry_run=True)
        processor = HeadingProcessor(config)
        
        processor._process_file(test_file)
        
        # Check file was not modified
        assert test_file.read_text() == original_content
        assert processor.stats['processed'] == 1
    
    def test_process_file_error_handling(self, tmp_path):
        """Test error handling during file processing."""
        config = Config(vault_path=tmp_path)
        processor = HeadingProcessor(config)
        
        # Try to process non-existent file
        fake_file = tmp_path / "non-existent.md"
        processor._process_file(fake_file)
        
        assert processor.stats['errors'] == 1
    
    def test_match_glob_pattern(self, processor):
        """Test glob pattern matching."""
        test_cases = [
            ("daily-notes/2024-01-15.md", "**/daily-notes/*.md", True),
            ("archive/2024/note.md", "archive/**/*.md", True),
            ("notes/test.md", "templates/*.md", False),
            ("project/sub/file.md", "project/*/*.md", True),
        ]
        
        for path, pattern, expected in test_cases:
            result = processor._match_glob_pattern(path, pattern)
            assert result == expected
    
    def test_process_vault_integration(self, tmp_path):
        """Integration test for processing entire vault."""
        # Create test vault structure
        (tmp_path / "notes").mkdir()
        (tmp_path / "daily-notes").mkdir()
        (tmp_path / "04-TEMPLATES").mkdir()
        
        # Create various test files
        (tmp_path / "notes" / "note1.md").write_text("# Note 1")
        (tmp_path / "notes" / "note2.md").write_text("""---
heading: Existing
---

# Note 2""")
        (tmp_path / "daily-notes" / "2024-01-15.md").write_text("# Daily")
        (tmp_path / "04-TEMPLATES" / "template.md").write_text("# Template")
        (tmp_path / "notes" / "project-summary.md").write_text("# Summary")
        
        config = Config(vault_path=tmp_path)
        processor = HeadingProcessor(config)
        
        processor.process_vault()
        
        # Check results
        assert processor.stats['processed'] == 4  # All except the one with existing heading
        assert processor.stats['skipped_existing'] == 1
        
        # Verify specific headings
        note1_content = (tmp_path / "notes" / "note1.md").read_text()
        assert "heading: note1" in note1_content
        
        daily_content = (tmp_path / "daily-notes" / "2024-01-15.md").read_text()
        assert "heading: Daily Note 2024-01-15" in daily_content
        
        template_content = (tmp_path / "04-TEMPLATES" / "template.md").read_text()
        assert "heading: Template: template" in template_content
        
        summary_content = (tmp_path / "notes" / "project-summary.md").read_text()
        assert "heading: project - Summary" in summary_content