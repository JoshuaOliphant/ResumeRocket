# JavaScript Tests for ResumeRocket

This directory contains end-to-end tests for JavaScript-based features in the ResumeRocket application.

## Prerequisites

- Node.js (v14 or higher)
- A running ResumeRocket server (on http://localhost:8080 by default)
- Valid user credentials for the application

## Installation

```bash
cd test_scripts/js_tests
npm install
```

This will install the required dependencies, including Playwright.

## Running Tests

### Test Section Collapsing Feature

This test validates the collapsing/expanding functionality for resume sections:

```bash
node test_section_collapsing.js
```

Before running, make sure:
1. The ResumeRocket server is running on localhost:8080
2. You have updated the test credentials in the script if needed
3. You have at least one resume with a customized version to compare

The test will:
- Login to the application
- Navigate to a resume comparison page
- Test the section collapsing/expanding functionality
- Verify synchronization between original and customized views
- Test state preservation when switching view modes

## Configuration

You can modify the following variables in each test script:

- `SERVER_URL`: The URL where the ResumeRocket server is running
- `LOGIN_CREDENTIALS`: Test user email and password
- `TEST_TIMEOUT`: Maximum time to wait for operations to complete

## Troubleshooting

If tests fail:
1. Check that the server is running
2. Verify your test credentials are correct
3. Ensure you have resume comparisons available in the test account
4. Review the screenshot (test-failure.png) generated on failure