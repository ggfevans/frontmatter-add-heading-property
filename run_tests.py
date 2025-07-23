#!/usr/bin/env python3
"""
Test runner script for add_headings.py test suite.
Provides convenient commands for running different types of tests.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description='Test runner for add_headings.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --unit             # Run unit tests only
  python run_tests.py --integration      # Run integration tests only
  python run_tests.py --coverage         # Run with coverage report
  python run_tests.py --fast             # Run fast tests only
  python run_tests.py --lint             # Run code quality checks
  python run_tests.py --all              # Run everything
        """
    )
    
    parser.add_argument('--unit', action='store_true',
                       help='Run unit tests only')
    parser.add_argument('--integration', action='store_true',
                       help='Run integration tests only')
    parser.add_argument('--coverage', action='store_true',
                       help='Run tests with coverage report')
    parser.add_argument('--fast', action='store_true',
                       help='Run fast tests only (exclude slow tests)')
    parser.add_argument('--lint', action='store_true',
                       help='Run code quality checks')
    parser.add_argument('--all', action='store_true',
                       help='Run all tests and quality checks')
    parser.add_argument('--parallel', action='store_true',
                       help='Run tests in parallel')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--stop-first', '-x', action='store_true',
                       help='Stop on first failure')
    
    args = parser.parse_args()
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    if script_dir != Path.cwd():
        print(f"Changing to script directory: {script_dir}")
        import os
        os.chdir(script_dir)
    
    success = True
    
    # Build pytest command
    pytest_cmd = ['python', '-m', 'pytest']
    
    if args.verbose:
        pytest_cmd.append('-v')
    
    if args.stop_first:
        pytest_cmd.append('-x')
    
    if args.parallel:
        pytest_cmd.extend(['-n', 'auto'])
    
    # Run specific test types
    if args.unit:
        success &= run_command(
            pytest_cmd + ['-m', 'unit'],
            'Unit Tests'
        )
    elif args.integration:
        success &= run_command(
            pytest_cmd + ['-m', 'integration'],
            'Integration Tests'
        )
    elif args.fast:
        success &= run_command(
            pytest_cmd + ['-m', 'not slow'],
            'Fast Tests'
        )
    elif args.coverage:
        success &= run_command(
            pytest_cmd + ['--cov=add_headings', '--cov-report=html', '--cov-report=term'],
            'Tests with Coverage'
        )
    elif args.lint:
        # Run linting tools
        success &= run_command(['python', '-m', 'flake8', 'add_headings.py', 'tests/'], 'Flake8 Linting')
        success &= run_command(['python', '-m', 'black', '--check', 'add_headings.py', 'tests/'], 'Black Formatting Check')
        success &= run_command(['python', '-m', 'isort', '--check-only', 'add_headings.py', 'tests/'], 'Import Sorting Check')
        success &= run_command(['python', '-m', 'mypy', 'add_headings.py'], 'Type Checking')
    elif args.all:
        # Run everything
        success &= run_command(pytest_cmd + ['--cov=add_headings'], 'All Tests with Coverage')
        success &= run_command(['python', '-m', 'flake8', 'add_headings.py', 'tests/'], 'Flake8 Linting')
        success &= run_command(['python', '-m', 'black', '--check', 'add_headings.py', 'tests/'], 'Black Formatting Check')
    else:
        # Default: run all tests
        success &= run_command(pytest_cmd, 'All Tests')
    
    # Print summary
    print(f"\n{'='*60}")
    if success:
        print("✅ All checks passed!")
        return 0
    else:
        print("❌ Some checks failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())