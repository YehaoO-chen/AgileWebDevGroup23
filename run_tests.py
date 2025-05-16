#!/usr/bin/env python
"""
Test Runner Script for ProcrastiNo Application.
Runs unit tests and selenium tests, and manages Chrome processes.
"""

import os
import sys
import argparse
import unittest
import subprocess
import tempfile
import shutil
import time
from datetime import datetime

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run ProcrastiNo tests')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--selenium', action='store_true', help='Run only selenium tests')
    parser.add_argument('--quiet', action='store_true', help='Run in quiet mode (less output)')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--report', action='store_true', help='Generate HTML test report')

    return parser.parse_args()

def kill_chrome_processes(quiet=False):
    """Kill Chrome processes that might interfere with tests."""
    if not quiet:
        print("Terminating Chrome processes...")
    
    try:
        # Windows approach - no platform check needed
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe', '/T'], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe', '/T'], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if not quiet:
            print("Chrome processes terminated.")
    except Exception as e:
        if not quiet:
            print(f"Warning: Could not terminate Chrome processes: {e}")

def clean_temp_dirs(quiet=False):
    """Clean up temporary Chrome user data directories from previous test runs."""
    temp_dir = tempfile.gettempdir()
    if not quiet:
        print(f"Cleaning temporary Chrome directories in {temp_dir}")
    
    # Look for temporary directories that may have been left by Selenium
    for item in os.listdir(temp_dir):
        item_path = os.path.join(temp_dir, item)
        # Look for directories that could be Chrome user data dirs
        if os.path.isdir(item_path) and ('chrome' in item.lower() or 'selenium' in item.lower()):
            try:
                shutil.rmtree(item_path, ignore_errors=True)
                if not quiet:
                    print(f"Removed temporary directory: {item_path}")
            except Exception as e:
                if not quiet:
                    print(f"Warning: Could not remove directory {item_path}: {e}")

def run_all_tests(args):
    """Run all tests based on provided arguments."""
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
        
        # Use unittest 
        unit_suite = unittest.defaultTestLoader.discover(unit_path, pattern='test_*.py')
        unit_result = unittest.TextTestRunner(verbosity=2).run(unit_suite)
        
        # Display test summary
        print(f"\nUnit Tests Complete: ran {unit_result.testsRun} tests")
        if unit_result.failures or unit_result.errors:
            print(f"Failures: {len(unit_result.failures)}, Errors: {len(unit_result.errors)}")
        else:
            print("All tests passed successfully!")
    
    # Run selenium tests
    if args.selenium or (not args.unit):
        # Always clean Chrome processes before Selenium tests
        kill_chrome_processes(args.quiet)
        clean_temp_dirs(args.quiet)
        
        print("\n=== Running Selenium Tests ===\n")
        
        try:
            # Use unittest
            selenium_suite = unittest.defaultTestLoader.discover(selenium_path, pattern='test_*.py')
            selenium_result = unittest.TextTestRunner(verbosity=2).run(selenium_suite)
            
            # Display test summary
            print(f"\nSelenium Tests Complete: ran {selenium_result.testsRun} tests")
            if selenium_result.failures or selenium_result.errors:
                print(f"Failures: {len(selenium_result.failures)}, Errors: {len(selenium_result.errors)}")
            else:
                print("All tests passed successfully!")
                
        except Exception as e:
            print(f"Error during Selenium tests: {e}")
            # Ensure Chrome processes are terminated on error
            kill_chrome_processes(args.quiet)
            return 1
        finally:
            # Always clean up Chrome processes after Selenium tests
            time.sleep(1)  # Give a moment for processes to close naturally
            kill_chrome_processes(args.quiet)
            print("\nTest execution completed.")
    
    return 0

if __name__ == '__main__':
    args = parse_args()
    try:
        exit_code = run_all_tests(args)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTests interrupted by user. Cleaning up...")
        kill_chrome_processes(args.quiet)
        sys.exit(130)  # Standard exit code for SIGINT