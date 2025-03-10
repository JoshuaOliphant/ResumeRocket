#!/usr/bin/env python3
"""
Test script for section collapsing functionality

This script opens the component test in a web browser for manual testing.
No external dependencies or server required.
"""

import os
import sys
import webbrowser
from pathlib import Path

# Get the path to the test file
script_dir = Path(__file__).resolve().parent
test_file_path = script_dir / "component_tests" / "test_section_collapsing.html"

# Convert to file:// URL
file_url = f"file://{test_file_path.absolute()}"

# Open in the default web browser
print(f"Opening test file: {test_file_path}")
print(f"URL: {file_url}")
print("\nThe test will open in your default web browser.")
print("Click the 'Run Tests' button to execute the tests.")

webbrowser.open(file_url)