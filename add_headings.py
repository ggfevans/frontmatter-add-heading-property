#!/usr/bin/env python3
"""
Obsidian Heading Property Script

Adds 'heading' property to frontmatter of all Markdown files in an Obsidian vault.
Supports various heading value rules based on file location and naming patterns.
"""

import os
import re
import yaml
import argparse
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import Counter


@dataclass
class Config:
    """Configuration for the heading script."""
    vault_path: Path
    dry_run: bool = False
    backup: bool = False
    verbose: bool = False
    skip_existing: bool = True
    title_case: bool = False
    preserve_case: bool = False
    exclude_dirs: List[str] = None
    include_patterns: List[str] = None
    
    def __post_init__(self):
        if self.exclude_dirs is None:
            self.exclude_dirs = []
        if self.include_patterns is None:
            self.include_patterns = []


class HeadingProcessor:
    """Main processor for adding headings to Obsidian markdown files."""
    
    # Common technical terms to preserve in title case
    PRESERVE_TERMS = {
        'API', 'APIs', 'UI', 'UX', 'CSS', 'HTML', 'JS', 'JSON', 'YAML', 
        'XML', 'SQL', 'HTTP', 'HTTPS', 'URL', 'URI', 'ID', 'iOS', 'macOS',
        'IDE', 'CLI', 'GUI', 'REST', 'GraphQL', 'OAuth', 'JWT', 'PDF',
        'PNG', 'JPG', 'GIF', 'SVG', 'MP3', 'MP4', 'ZIP', 'README'
    }
    
    # Daily note directory patterns
    DAILY_NOTE_PATTERNS = [
        r'00-INBOX[/\\]daily-notes[/\\]',
        r'99-ARCHIVE[/\\]\d{4}[/\\]\d{2}-\w+[/\\]',
        r'daily-notes[/\\]',
        r'journal[/\\]'
    ]
    
    # Template directory patterns
    TEMPLATE_PATTERNS = [
        r'04-TEMPLATES[/\\]',
        r'templates[/\\]',
        r'template[/\\]'
    ]
    
    # Organizational directory patterns
    ORG_DIR_PATTERN = re.compile(r'^\d{2}-[A-Z]+$')
    
    def __init__(self, config: Config):
        self.config = config
        self.stats = Counter()
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up logging configuration."""
        level = logging.DEBUG if self.config.verbose else logging.INFO
        format_str = '%(asctime)s - %(levelname)s - %(message)s' if self.config.verbose else '%(message)s'
        
        logging.basicConfig(
            level=level,
            format=format_str,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
    def process_vault(self):
        """Process all markdown files in the vault."""
        self.logger.info(f"Processing vault: {self.config.vault_path}")
        if self.config.dry_run:
            self.logger.info("🔍 DRY RUN MODE - No files will be modified")
            
        # Find all markdown files
        md_files = self._find_markdown_files()
        total_files = len(md_files)
        
        if total_files == 0:
            self.logger.warning("No markdown files found in vault")
            return
            
        self.logger.info(f"Found {total_files} markdown files")
        
        # Process each file
        for i, file_path in enumerate(md_files, 1):
            if self.config.verbose:
                self.logger.debug(f"Processing ({i}/{total_files}): {file_path}")
            self._process_file(file_path)
            
        # Print summary
        self._print_summary()
        
    def _find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the vault, respecting exclusions."""
        md_files = []
        
        for root, dirs, files in os.walk(self.config.vault_path):
            root_path = Path(root)
            
            # Check if directory should be excluded
            rel_path = root_path.relative_to(self.config.vault_path)
            if self._should_exclude_directory(rel_path):
                dirs.clear()  # Don't recurse into this directory
                continue
                
            # Find markdown files
            for file in files:
                if file.lower().endswith('.md'):
                    file_path = root_path / file
                    
                    # Skip canvas and excalidraw files
                    if file.endswith('.canvas') or file.endswith('.excalidraw.md'):
                        self.stats['skipped_special'] += 1
                        continue
                        
                    md_files.append(file_path)
                    
        return sorted(md_files)
        
    def _should_exclude_directory(self, rel_path: Path) -> bool:
        """Check if a directory should be excluded."""
        rel_str = str(rel_path).replace('\\', '/')
        
        # Always exclude .obsidian directory
        if '.obsidian' in rel_path.parts:
            return True
            
        # Check custom exclusions
        for exclude_dir in self.config.exclude_dirs:
            if exclude_dir in rel_str:
                return True
                
        return False
        
    def _process_file(self, file_path: Path):
        """Process a single markdown file."""
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8')
            
            # Parse frontmatter
            frontmatter, body = self._parse_frontmatter(content)
            
            # Check if heading already exists
            if frontmatter and 'heading' in frontmatter and self.config.skip_existing:
                self.logger.info(f"⚠ Skipped (has heading): {file_path.name}")
                self.stats['skipped_existing'] += 1
                return
                
            # Generate heading value
            heading_value = self._generate_heading_value(file_path)
            
            # Update frontmatter
            if frontmatter is None:
                frontmatter = {}
            frontmatter['heading'] = heading_value
            
            # Reconstruct file content
            new_content = self._reconstruct_content(frontmatter, body)
            
            # Write file (or simulate in dry run)
            if not self.config.dry_run:
                # Create backup if requested
                if self.config.backup:
                    backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                    shutil.copy2(file_path, backup_path)
                    
                file_path.write_text(new_content, encoding='utf-8')
                
            self.logger.info(f"✓ Added heading to: {file_path.name} → \"{heading_value}\"")
            self.stats['processed'] += 1
            
        except Exception as e:
            self.logger.error(f"✗ Error processing {file_path.name}: {str(e)}")
            self.stats['errors'] += 1
            
    def _parse_frontmatter(self, content: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """Parse YAML frontmatter from content."""
        if not content.strip():
            return None, content
            
        # Check for frontmatter delimiters
        if content.startswith('---\n') or content.startswith('---\r\n'):
            # Find closing delimiter
            lines = content.splitlines(keepends=True)
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    # Extract frontmatter
                    fm_text = ''.join(lines[1:i])
                    body = ''.join(lines[i+1:])
                    
                    try:
                        frontmatter = yaml.safe_load(fm_text) or {}
                        return frontmatter, body
                    except yaml.YAMLError as e:
                        self.logger.warning(f"Invalid YAML frontmatter: {e}")
                        return None, content
                        
        return None, content
        
    def _reconstruct_content(self, frontmatter: Dict[str, Any], body: str) -> str:
        """Reconstruct file content with updated frontmatter."""
        # Convert frontmatter to YAML
        fm_yaml = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Ensure proper formatting
        if not fm_yaml.endswith('\n'):
            fm_yaml += '\n'
            
        return f"---\n{fm_yaml}---\n{body}"
        
    def _generate_heading_value(self, file_path: Path) -> str:
        """Generate appropriate heading value based on file path and name."""
        filename = file_path.stem
        rel_path = file_path.relative_to(self.config.vault_path)
        rel_str = str(rel_path).replace('\\', '/')
        
        # Rule 1: Daily Notes
        if self._is_daily_note(rel_str):
            return f"Daily Note {filename}"
            
        # Rule 2: Project Summary files
        if filename.endswith('-summary'):
            project_name = filename[:-8]  # Remove '-summary'
            if self.config.title_case:
                project_name = self._to_title_case(project_name)
            return f"{project_name} - Summary"
            
        # Rule 3: Template files
        if self._is_template_file(rel_str, filename):
            return f"Template: {filename}"
            
        # Rule 4: Index files
        if filename.lower() == 'index':
            parent_name = file_path.parent.name
            if self.config.title_case:
                parent_name = self._to_title_case(parent_name)
            return f"{parent_name} - Index"
            
        # Rule 5: README files
        if filename.upper() == 'README':
            parent_name = file_path.parent.name
            if self.config.title_case:
                parent_name = self._to_title_case(parent_name)
            return f"{parent_name} - README"
            
        # Rule 6 & 7: Apply title case if enabled
        if self.config.title_case and not self.config.preserve_case:
            return self._to_title_case(filename)
            
        # Rule 8: Default - use filename as is
        return filename
        
    def _is_daily_note(self, rel_path: str) -> bool:
        """Check if file is in a daily notes directory."""
        for pattern in self.DAILY_NOTE_PATTERNS:
            if re.search(pattern, rel_path, re.IGNORECASE):
                return True
                
        # Check custom include patterns
        for pattern in self.config.include_patterns:
            if self._match_glob_pattern(rel_path, pattern):
                return True
                
        return False
        
    def _is_template_file(self, rel_path: str, filename: str) -> bool:
        """Check if file is a template."""
        # Check directory patterns
        for pattern in self.TEMPLATE_PATTERNS:
            if re.search(pattern, rel_path, re.IGNORECASE):
                return True
                
        # Check filename
        if 'template' in filename.lower():
            return True
            
        return False
        
    def _match_glob_pattern(self, path: str, pattern: str) -> bool:
        """Match a path against a glob pattern."""
        from fnmatch import fnmatch
        return fnmatch(path, pattern)
        
    def _to_title_case(self, text: str) -> str:
        """Convert text to title case with smart handling."""
        # Handle kebab-case and underscores
        text = text.replace('-', ' ').replace('_', ' ')
        
        # Remove organizational prefixes (01-, 02-, etc.)
        text = re.sub(r'^\d{2}-\s*', '', text)
        
        # Split into words
        words = text.split()
        
        # Process each word
        result_words = []
        for word in words:
            # Check if word should be preserved
            if word.upper() in self.PRESERVE_TERMS:
                result_words.append(word.upper())
            elif word in self.PRESERVE_TERMS:
                result_words.append(word)
            else:
                # Standard title case
                result_words.append(word.capitalize())
                
        return ' '.join(result_words)
        
    def _print_summary(self):
        """Print processing summary."""
        self.logger.info("\n" + "="*50)
        self.logger.info("SUMMARY")
        self.logger.info("="*50)
        self.logger.info(f"✓ Processed: {self.stats['processed']}")
        self.logger.info(f"⚠ Skipped (existing): {self.stats['skipped_existing']}")
        self.logger.info(f"⚠ Skipped (special): {self.stats['skipped_special']}")
        self.logger.info(f"✗ Errors: {self.stats['errors']}")
        
        total = sum(self.stats.values())
        self.logger.info(f"\nTotal files: {total}")


class ConfigFileLoader:
    """Load configuration from YAML file."""
    
    @staticmethod
    def load_config_file(vault_path: Path) -> Optional[Dict[str, Any]]:
        """Load .heading-config.yaml from vault root."""
        config_path = vault_path / '.heading-config.yaml'
        
        if not config_path.exists():
            return None
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.warning(f"Error loading config file: {e}")
            return None
            
    @staticmethod
    def merge_config(args: argparse.Namespace, file_config: Dict[str, Any]) -> Config:
        """Merge command-line arguments with file configuration."""
        # Start with command-line arguments
        config = Config(
            vault_path=Path(args.vault_path),
            dry_run=args.dry_run,
            backup=args.backup,
            verbose=args.verbose,
            skip_existing=args.skip_existing,
            title_case=args.title_case,
            preserve_case=args.preserve_case
        )
        
        # Parse exclude dirs
        if args.exclude_dirs:
            config.exclude_dirs = [d.strip() for d in args.exclude_dirs.split(',')]
            
        # Parse include patterns
        if args.include_patterns:
            config.include_patterns = [p.strip() for p in args.include_patterns.split(',')]
            
        # Merge with file config if available
        if file_config:
            # Update patterns from file
            if 'daily_note_patterns' in file_config:
                HeadingProcessor.DAILY_NOTE_PATTERNS.extend(file_config['daily_note_patterns'])
                
            if 'template_directories' in file_config:
                HeadingProcessor.TEMPLATE_PATTERNS.extend(file_config['template_directories'])
                
            if 'title_case' in file_config:
                tc_config = file_config['title_case']
                if 'preserve_terms' in tc_config:
                    HeadingProcessor.PRESERVE_TERMS.update(tc_config['preserve_terms'])
                    
            if 'exclude_patterns' in file_config:
                config.exclude_dirs.extend(file_config['exclude_patterns'])
                
        return config


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Add heading property to Obsidian markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/vault
  %(prog)s /path/to/vault --dry-run --verbose
  %(prog)s /path/to/vault --backup --title-case
  %(prog)s /path/to/vault --exclude-dirs "04-TEMPLATES,drafts"
        """
    )
    
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview changes without modifying files')
    parser.add_argument('--backup', action='store_true',
                       help='Create .bak files before modification')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--skip-existing', action='store_true', default=True,
                       help='Skip files with existing heading property (default: True)')
    parser.add_argument('--title-case', action='store_true',
                       help='Convert filenames to title case')
    parser.add_argument('--preserve-case', action='store_true',
                       help='Preserve original filename casing')
    parser.add_argument('--exclude-dirs', type=str,
                       help='Comma-separated list of directories to exclude')
    parser.add_argument('--include-patterns', type=str,
                       help='Additional patterns for daily note directories')
    
    args = parser.parse_args()
    
    # Validate vault path
    vault_path = Path(args.vault_path).resolve()
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        return 1
        
    if not vault_path.is_dir():
        print(f"Error: Vault path is not a directory: {vault_path}")
        return 1
        
    # Load configuration
    file_config = ConfigFileLoader.load_config_file(vault_path)
    config = ConfigFileLoader.merge_config(args, file_config or {})
    
    # Process vault
    processor = HeadingProcessor(config)
    processor.process_vault()
    
    return 0


if __name__ == '__main__':
    exit(main())