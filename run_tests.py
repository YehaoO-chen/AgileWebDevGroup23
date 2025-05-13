#!/usr/bin/env python
"""
Test Runner Script for ProcrastiNo Application.
Runs unit tests and selenium tests, and generates reports.
"""

import os
import sys
import argparse
import unittest
import pytest
from datetime import datetime

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run ProcrastiNo tests')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--selenium', action='store_true', help='Run only selenium tests')
    parser.add_argument('--report', action='store_true', help='Generate HTML report')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    return parser.parse_args()

def run_all_tests(args):
    """Run all tests based on provided arguments."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Use OS-specific path separator
    unit_path = os.path.join('tests', 'unit')
    selenium_path = os.path.join('tests', 'selenium')
    
    # Ensure tests directory exists
    if not os.path.exists('tests'):
        print("Error: 'tests' directory not found.")
        return 1
    
    # Run unit tests
    if args.unit or (not args.selenium):
        print("\n=== Running Unit Tests ===\n")
        
        if args.verbose:
            unittest_args = ['-v']
        else:
            unittest_args = []
        
        # Use unittest or pytest based on requirements
        if args.report or args.coverage:
            # Use pytest for reports
            pytest_args = [unit_path]
            
            if args.verbose:
                pytest_args.append('-v')
            
            if args.report:
                report_file = f'test-report-unit-{timestamp}.html'
                pytest_args.extend(['--html', report_file])
                print(f"HTML report will be generated at: {report_file}")
            
            if args.coverage:
                pytest_args.extend(['--cov=app', '--cov-report', 'term', '--cov-report', f'html:coverage-unit-{timestamp}'])
                print(f"Coverage report will be generated at: coverage-unit-{timestamp}/")
            
            # Run pytest
            pytest.main(pytest_args)
        else:
            # Use unittest
            unit_suite = unittest.defaultTestLoader.discover(unit_path, pattern='test_*.py')
            unittest.TextTestRunner(verbosity=2 if args.verbose else 1).run(unit_suite)
    
    # Run selenium tests
    if args.selenium or (not args.unit):
        print("\n=== Running Selenium Tests ===\n")
        
        if args.report or args.coverage:
            # Use pytest for reports
            pytest_args = [selenium_path]
            
            if args.verbose:
                pytest_args.append('-v')
            
            if args.report:
                report_file = f'test-report-selenium-{timestamp}.html'
                pytest_args.extend(['--html', report_file])
                print(f"HTML report will be generated at: {report_file}")
            
            if args.coverage:
                pytest_args.extend(['--cov=app', '--cov-report', 'term', '--cov-report', f'html:coverage-selenium-{timestamp}'])
                print(f"Coverage report will be generated at: coverage-selenium-{timestamp}/")
            
            # Run pytest
            pytest.main(pytest_args)
        else:
            # Use unittest
            selenium_suite = unittest.defaultTestLoader.discover(selenium_path, pattern='test_*.py')
            unittest.TextTestRunner(verbosity=2 if args.verbose else 1).run(selenium_suite)
    
    return 0

if __name__ == '__main__':
    args = parse_args()
    sys.exit(run_all_tests(args))