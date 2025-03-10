# Component Tests for ResumeRocket

This directory contains standalone HTML/JS tests for individual UI components of the ResumeRocket application.
These tests can be run directly in a web browser without requiring the full application environment, making them
ideal for quick validation of UI functionality.

## Available Tests

### Section Collapsing Test (`test_section_collapsing.html`)

Tests the section collapsing/expanding functionality for resume sections, verifying:

1. Proper detection of section headers
2. Addition of toggle buttons to section headers
3. Collapsing/expanding behavior when clicking toggle buttons

## Running Tests

### Method 1: Using the Python Runner Script

```bash
# From project root
python test_scripts/run_section_collapsing_test.py
```

This will open the test page in your default web browser.

### Method 2: Opening Directly in Browser

Simply open the HTML test file directly in any web browser:

1. Navigate to the test file location
2. Double-click the `.html` file or drag it into a browser window

## Test Structure

Each component test follows the same structure:

1. **HTML Test Fixture**: Sample HTML content that mimics the real application
2. **Component Code**: The actual component code copied from the application
3. **Test Script**: Code that runs tests against the component
4. **Results Display**: Interface showing test results and logs

## Contributing

When adding a new component test:

1. Create a new HTML file following the existing pattern
2. Include only the minimal code needed to test the component
3. Ensure the test runs independently without requiring a server
4. Update this README.md with details about the new test