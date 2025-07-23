"""
Tests for utility functions and edge cases.
"""

import pytest
from pathlib import Path
import yaml
import logging
from unittest.mock import Mock, patch, call
import argparse
import sys

from add_headings import main, HeadingProcessor, Config


class TestMain:
    """Test suite for main function and CLI."""
    
    def test_main_invalid_vault_path(self, capsys):
        """Test main with non-existent vault path."""
        test_args = ['add_headings.py', '/non/existent/path']
        
        with patch.object(sys, 'argv', test_args):
            result = main()
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Error: Vault path does not exist" in captured.out
    
    def test_main_vault_path_is_file(self, tmp_path, capsys):
        """Test main with file instead of directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        test_args = ['add_headings.py', str(test_file)]
        
        with patch.object(sys, 'argv', test_args):
            result = main()
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Error: Vault path is not a directory" in captured.out
    
    @patch('add_headings.HeadingProcessor')
    def test_main_successful_run(self, mock_processor_class, tmp_path):
        """Test successful main execution."""
        test_args = ['add_headings.py', str(tmp_path)]
        
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        with patch.object(sys, 'argv', test_args):
            result = main()
        
        assert result == 0
        mock_processor_class.assert_called_once()
        mock_processor.process_vault.assert_called_once()
    
    @patch('add_headings.ConfigFileLoader.load_config_file')
    @patch('add_headings.HeadingProcessor')
    def test_main_with_config_file(self, mock_processor_class, mock_load_config, tmp_path):
        """Test main with config file loading."""
        test_args = ['add_headings.py', str(tmp_path), '--dry-run', '--verbose']
        
        mock_config = {
            'daily_note_patterns': ['test/*'],
            'exclude_patterns': ['exclude/*']
        }
        mock_load_config.return_value = mock_config
        
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        with patch.object(sys, 'argv', test_args):
            result = main()
        
        assert result == 0
        mock_load_config.assert_called_once_with(tmp_path)
        
        # Verify processor was created with merged config
        args, kwargs = mock_processor_class.call_args
        config = args[0]
        assert config.dry_run is True
        assert config.verbose is True
    
    def test_main_all_arguments(self, tmp_path):
        """Test main with all command line arguments."""
        test_args = [
            'add_headings.py',
            str(tmp_path),
            '--dry-run',
            '--backup',
            '--verbose',
            '--skip-existing',
            '--title-case',
            '--preserve-case',
            '--exclude-dirs', 'dir1,dir2',
            '--include-patterns', '*.md,*.txt'
        ]
        
        with patch.object(sys, 'argv', test_args):
            with patch('add_headings.HeadingProcessor') as mock_processor_class:
                mock_processor = Mock()
                mock_processor_class.return_value = mock_processor
                
                result = main()
                
                # Verify config was created correctly
                args, kwargs = mock_processor_class.call_args
                config = args[0]
                
                assert config.vault_path == tmp_path
                assert config.dry_run is True
                assert config.backup is True
                assert config.verbose is True
                assert config.skip_existing is True
                assert config.title_case is True
                assert config.preserve_case is True
                assert config.exclude_dirs == ['dir1', 'dir2']
                assert config.include_patterns == ['*.md', '*.txt']


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_vault(self, tmp_path, capsys):
        """Test processing empty vault."""
        config = Config(vault_path=tmp_path)
        processor = HeadingProcessor(config)
        
        processor.process_vault()
        
        captured = capsys.readouterr()
        assert "No markdown files found in vault" in captured.out
    
    def test_yaml_unicode_handling(self):
        """Test YAML handling with unicode characters."""
        config = Config(vault_path=Path("/test"))
        processor = HeadingProcessor(config)
        
        content = """---
title: Test with émojis 🎉
author: José García
tags: [测试, тест]
---

# Content with unicode: 你好世界
"""
        frontmatter, body = processor._parse_frontmatter(content)
        
        assert frontmatter['title'] == 'Test with émojis 🎉'
        assert frontmatter['author'] == 'José García'
        assert '测试' in frontmatter['tags']
        
        # Test reconstruction
        new_content = processor._reconstruct_content(frontmatter, body)
        assert 'émojis 🎉' in new_content
        assert 'José García' in new_content
    
    def test_malformed_frontmatter_variations(self):
        """Test various malformed frontmatter scenarios."""
        config = Config(vault_path=Path("/test"))
        processor = HeadingProcessor(config)
        
        # Missing closing delimiter
        content1 = """---
title: Test
tags: [test]

# Content without closing delimiter
"""
        fm1, body1 = processor._parse_frontmatter(content1)
        assert fm1 is None
        assert body1 == content1
        
        # Empty frontmatter
        content2 = """---
---

# Content
"""
        fm2, body2 = processor._parse_frontmatter(content2)
        assert fm2 == {}
        assert body2.strip() == "# Content"
        
        # Frontmatter with only whitespace
        content3 = """---
   
   
---

# Content
"""
        fm3, body3 = processor._parse_frontmatter(content3)
        assert fm3 == {}
    
    def test_special_characters_in_filenames(self, tmp_path):
        """Test handling special characters in filenames."""
        config = Config(vault_path=tmp_path)
        processor = HeadingProcessor(config)
        
        # Test various special character scenarios
        test_cases = [
            ("file-with-dashes.md", "file-with-dashes"),
            ("file_with_underscores.md", "file_with_underscores"),
            ("file.with.dots.md", "file.with.dots"),
            ("file (with) parentheses.md", "file (with) parentheses"),
            ("file & ampersand.md", "file & ampersand"),
            ("file's apostrophe.md", "file's apostrophe"),
        ]
        
        for filename, expected_heading in test_cases:
            file_path = tmp_path / filename
            result = processor._generate_heading_value(file_path)
            assert result == expected_heading
    
    def test_very_long_frontmatter(self):
        """Test handling very long frontmatter."""
        config = Config(vault_path=Path("/test"))
        processor = HeadingProcessor(config)
        
        # Create frontmatter with many fields
        fm_dict = {f'field_{i}': f'value_{i}' for i in range(100)}
        fm_dict['heading'] = 'Test Heading'
        
        body = "# Content\n\nThis is the body."
        
        result = processor._reconstruct_content(fm_dict, body)
        
        # Verify all fields are present
        assert "field_0: value_0" in result
        assert "field_99: value_99" in result
        assert "heading: Test Heading" in result
        assert result.endswith("---\n# Content\n\nThis is the body.")
    
    def test_windows_path_handling(self):
        """Test proper handling of Windows paths."""
        config = Config(vault_path=Path("C:\\Users\\Test\\Vault"))
        processor = HeadingProcessor(config)
        
        # Test Windows path normalization
        test_path = Path("C:\\Users\\Test\\Vault\\00-INBOX\\daily-notes\\2024-01-15.md")
        result = processor._generate_heading_value(test_path)
        assert result == "Daily Note 2024-01-15"
        
        # Test mixed separators
        rel_path = "00-INBOX\\daily-notes/2024-01-15.md"
        assert processor._is_daily_note(rel_path) is True
    
    def test_concurrent_file_modification(self, tmp_path):
        """Test handling when file is modified during processing."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Original Content")
        
        config = Config(vault_path=tmp_path)
        processor = HeadingProcessor(config)
        
        # Simulate file being deleted during processing
        def side_effect(*args, **kwargs):
            test_file.unlink()
            raise FileNotFoundError("File was deleted")
        
        with patch.object(Path, 'read_text', side_effect=side_effect):
            processor._process_file(test_file)
        
        assert processor.stats['errors'] == 1
    
    def test_preserve_terms_case_sensitivity(self):
        """Test preserve terms with various case combinations."""
        config = Config(vault_path=Path("/test"))
        processor = HeadingProcessor(config)
        
        test_cases = [
            ("working-with-api", "Working With API"),
            ("the-ios-guide", "The iOS Guide"),
            ("html-and-css", "HTML And CSS"),
            ("readme-file", "README File"),
            ("api-API-Api", "API API API"),  # All variations should become uppercase
        ]
        
        for input_text, expected in test_cases:
            result = processor._to_title_case(input_text)
            assert result == expected
    
    def test_empty_frontmatter_values(self):
        """Test handling empty values in frontmatter."""
        config = Config(vault_path=Path("/test"))
        processor = HeadingProcessor(config)
        
        content = """---
title: 
tags: []
author: null
notes: ""
---

# Content
"""
        frontmatter, body = processor._parse_frontmatter(content)
        
        assert frontmatter['title'] == None
        assert frontmatter['tags'] == []
        assert frontmatter['author'] is None
        assert frontmatter['notes'] == ""
        
        # Add heading and reconstruct
        frontmatter['heading'] = 'Test Heading'
        new_content = processor._reconstruct_content(frontmatter, body)
        
        # Verify YAML is valid
        yaml.safe_load(new_content.split('---')[1])


class TestLogging:
    """Test logging functionality."""
    
    def test_verbose_logging(self, capsys):
        """Test verbose logging output."""
        config = Config(vault_path=Path("/test"), verbose=True)
        processor = HeadingProcessor(config)
        
        # Capture logger output
        processor.logger.debug("Debug message")
        processor.logger.info("Info message")
        
        # In verbose mode, format includes timestamp
        assert processor.logger.level == logging.DEBUG
    
    def test_normal_logging(self):
        """Test normal logging output."""
        config = Config(vault_path=Path("/test"), verbose=False)
        processor = HeadingProcessor(config)
        
        assert processor.logger.level == logging.INFO
    
    def test_summary_output(self, capsys):
        """Test summary statistics output."""
        config = Config(vault_path=Path("/test"))
        processor = HeadingProcessor(config)
        
        # Set some stats
        processor.stats['processed'] = 10
        processor.stats['skipped_existing'] = 5
        processor.stats['skipped_special'] = 2
        processor.stats['errors'] = 1
        
        processor._print_summary()
        
        captured = capsys.readouterr()
        assert "Processed: 10" in captured.out
        assert "Skipped (existing): 5" in captured.out
        assert "Skipped (special): 2" in captured.out
        assert "Errors: 1" in captured.out
        assert "Total files: 18" in captured.out