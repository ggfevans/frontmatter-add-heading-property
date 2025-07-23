"""
Tests for configuration handling.
"""

import pytest
from pathlib import Path
import yaml
import tempfile
from unittest.mock import Mock, patch
import argparse

from add_headings import Config, ConfigFileLoader, HeadingProcessor


class TestConfig:
    """Test suite for Config dataclass."""
    
    def test_config_initialization(self):
        """Test Config initialization with default values."""
        vault_path = Path("/test/vault")
        config = Config(vault_path=vault_path)
        
        assert config.vault_path == vault_path
        assert config.dry_run is False
        assert config.backup is False
        assert config.verbose is False
        assert config.skip_existing is True
        assert config.title_case is False
        assert config.preserve_case is False
        assert config.exclude_dirs == []
        assert config.include_patterns == []
    
    def test_config_custom_values(self):
        """Test Config initialization with custom values."""
        vault_path = Path("/test/vault")
        config = Config(
            vault_path=vault_path,
            dry_run=True,
            backup=True,
            verbose=True,
            skip_existing=False,
            title_case=True,
            preserve_case=True,
            exclude_dirs=["test1", "test2"],
            include_patterns=["*.md", "**/*.txt"]
        )
        
        assert config.vault_path == vault_path
        assert config.dry_run is True
        assert config.backup is True
        assert config.verbose is True
        assert config.skip_existing is False
        assert config.title_case is True
        assert config.preserve_case is True
        assert config.exclude_dirs == ["test1", "test2"]
        assert config.include_patterns == ["*.md", "**/*.txt"]
    
    def test_config_post_init(self):
        """Test Config post_init behavior."""
        config = Config(vault_path=Path("/test"))
        assert config.exclude_dirs == []
        assert config.include_patterns == []
        
        # Test with None values explicitly
        config = Config(
            vault_path=Path("/test"),
            exclude_dirs=None,
            include_patterns=None
        )
        assert config.exclude_dirs == []
        assert config.include_patterns == []


class TestConfigFileLoader:
    """Test suite for ConfigFileLoader."""
    
    def test_load_config_file_exists(self, tmp_path):
        """Test loading existing config file."""
        # Create config file
        config_content = {
            'daily_note_patterns': ['custom-daily/*'],
            'template_directories': ['my-templates/*'],
            'title_case': {
                'preserve_terms': ['API', 'iOS']
            },
            'exclude_patterns': ['archive/*', 'trash/*']
        }
        
        config_path = tmp_path / '.heading-config.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(config_content, f)
        
        result = ConfigFileLoader.load_config_file(tmp_path)
        
        assert result == config_content
        assert result['daily_note_patterns'] == ['custom-daily/*']
        assert result['template_directories'] == ['my-templates/*']
    
    def test_load_config_file_not_exists(self, tmp_path):
        """Test loading non-existent config file."""
        result = ConfigFileLoader.load_config_file(tmp_path)
        assert result is None
    
    def test_load_config_file_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML config file."""
        config_path = tmp_path / '.heading-config.yaml'
        config_path.write_text("invalid: yaml: content: [unclosed")
        
        with patch('logging.warning') as mock_warning:
            result = ConfigFileLoader.load_config_file(tmp_path)
            assert result is None
            mock_warning.assert_called_once()
    
    def test_merge_config_no_file_config(self):
        """Test merging config without file config."""
        args = argparse.Namespace(
            vault_path="/test/vault",
            dry_run=True,
            backup=True,
            verbose=True,
            skip_existing=False,
            title_case=True,
            preserve_case=False,
            exclude_dirs="test1,test2",
            include_patterns="*.md,*.txt"
        )
        
        config = ConfigFileLoader.merge_config(args, {})
        
        assert config.vault_path == Path("/test/vault")
        assert config.dry_run is True
        assert config.backup is True
        assert config.verbose is True
        assert config.skip_existing is False
        assert config.title_case is True
        assert config.preserve_case is False
        assert config.exclude_dirs == ["test1", "test2"]
        assert config.include_patterns == ["*.md", "*.txt"]
    
    def test_merge_config_with_file_config(self):
        """Test merging config with file config."""
        args = argparse.Namespace(
            vault_path="/test/vault",
            dry_run=False,
            backup=False,
            verbose=False,
            skip_existing=True,
            title_case=False,
            preserve_case=False,
            exclude_dirs="cli-exclude",
            include_patterns=None
        )
        
        file_config = {
            'daily_note_patterns': ['file-daily/*'],
            'template_directories': ['file-templates/*'],
            'title_case': {
                'preserve_terms': ['Docker', 'GitHub']
            },
            'exclude_patterns': ['file-exclude/*']
        }
        
        # Store original patterns
        original_daily = HeadingProcessor.DAILY_NOTE_PATTERNS.copy()
        original_template = HeadingProcessor.TEMPLATE_PATTERNS.copy()
        original_preserve = HeadingProcessor.PRESERVE_TERMS.copy()
        
        try:
            config = ConfigFileLoader.merge_config(args, file_config)
            
            # Check basic config
            assert config.exclude_dirs == ["cli-exclude", "file-exclude/*"]
            
            # Check patterns were extended
            assert 'file-daily/*' in HeadingProcessor.DAILY_NOTE_PATTERNS
            assert 'file-templates/*' in HeadingProcessor.TEMPLATE_PATTERNS
            assert 'Docker' in HeadingProcessor.PRESERVE_TERMS
            assert 'GitHub' in HeadingProcessor.PRESERVE_TERMS
            
        finally:
            # Restore original patterns
            HeadingProcessor.DAILY_NOTE_PATTERNS = original_daily
            HeadingProcessor.TEMPLATE_PATTERNS = original_template
            HeadingProcessor.PRESERVE_TERMS = original_preserve
    
    def test_merge_config_empty_args(self):
        """Test merging config with empty/None argument values."""
        args = argparse.Namespace(
            vault_path="/test/vault",
            dry_run=False,
            backup=False,
            verbose=False,
            skip_existing=True,
            title_case=False,
            preserve_case=False,
            exclude_dirs=None,
            include_patterns=None
        )
        
        config = ConfigFileLoader.merge_config(args, {})
        
        assert config.exclude_dirs == []
        assert config.include_patterns == []
    
    def test_merge_config_whitespace_handling(self):
        """Test proper handling of whitespace in comma-separated values."""
        args = argparse.Namespace(
            vault_path="/test/vault",
            dry_run=False,
            backup=False,
            verbose=False,
            skip_existing=True,
            title_case=False,
            preserve_case=False,
            exclude_dirs=" dir1 , dir2,  dir3  ",
            include_patterns="  *.md  ,  **/*.txt "
        )
        
        config = ConfigFileLoader.merge_config(args, {})
        
        assert config.exclude_dirs == ["dir1", "dir2", "dir3"]
        assert config.include_patterns == ["*.md", "**/*.txt"]
    
    def test_config_file_integration(self, tmp_path):
        """Integration test for loading and using config file."""
        # Create a comprehensive config file
        config_content = {
            'daily_note_patterns': [
                'personal/journal/*',
                'work/daily/*'
            ],
            'template_directories': [
                'custom-templates/*',
                'shared/templates/*'
            ],
            'title_case': {
                'preserve_terms': ['PhD', 'USA', 'UK']
            },
            'exclude_patterns': [
                'private/*',
                'backup/*',
                '*.tmp'
            ]
        }
        
        config_path = tmp_path / '.heading-config.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(config_content, f)
        
        # Create args
        args = argparse.Namespace(
            vault_path=str(tmp_path),
            dry_run=True,
            backup=False,
            verbose=True,
            skip_existing=True,
            title_case=True,
            preserve_case=False,
            exclude_dirs="temp,cache",
            include_patterns="notes/*"
        )
        
        # Load and merge config
        file_config = ConfigFileLoader.load_config_file(tmp_path)
        config = ConfigFileLoader.merge_config(args, file_config)
        
        # Verify merged config
        assert config.vault_path == tmp_path
        assert config.dry_run is True
        assert config.title_case is True
        assert "temp" in config.exclude_dirs
        assert "cache" in config.exclude_dirs
        assert "private/*" in config.exclude_dirs
        assert "backup/*" in config.exclude_dirs
        assert "*.tmp" in config.exclude_dirs
        assert config.include_patterns == ["notes/*"]