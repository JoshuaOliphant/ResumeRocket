/**
 * Test script for section collapsing functionality in resume comparison view
 * 
 * This script uses Playwright to test the section collapsing/expanding feature.
 * It loads the resume comparison page and tests the following:
 * 1. Section identification (both Markdown headings and uppercase sections)
 * 2. Collapsing/expanding functionality
 * 3. Synchronization between original and customized views
 * 4. State preservation when switching view modes
 * 
 * Requirements:
 * - npm install playwright
 * - ResumeRocket server running on http://localhost:8080
 * - At least one resume comparison available
 */

const { chromium } = require('playwright');

// Configuration
const SERVER_URL = 'http://localhost:5000';
const LOGIN_CREDENTIALS = {
  email: 'test@example.com',
  password: 'password123'
};
const TEST_TIMEOUT = 30000; // 30 seconds

// Test suite
async function runTests() {
  console.log('Starting section collapsing functionality tests...');
  
  // Launch browser
  const browser = await chromium.launch({ 
    headless: false // Set to true for CI environments
  });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Step 1: Login to the application
    console.log('Logging in...');
    await page.goto(`${SERVER_URL}/login`);
    await page.fill('input[name="email"]', LOGIN_CREDENTIALS.email);
    await page.fill('input[name="password"]', LOGIN_CREDENTIALS.password);
    await page.click('button[type="submit"]');
    
    // Wait for dashboard to load
    await page.waitForURL('**/dashboard');
    console.log('Login successful');
    
    // Step 2: Navigate to a resume comparison page
    // This assumes you have at least one customized resume
    console.log('Finding a resume to test...');
    // Click on the first "Compare" button
    await page.click('a:has-text("Compare")');
    
    // Wait for comparison page to load
    await page.waitForSelector('.resume-html-content');
    console.log('Resume comparison page loaded');
    
    // Step 3: Wait for section collapsing to be processed
    // Give time for sections to be identified and processed
    await page.waitForTimeout(2000);
    
    // Step 4: Test section toggle buttons existence
    const sectionToggleButtons = await page.$$('.section-toggle');
    const toggleCount = sectionToggleButtons.length;
    console.log(`Found ${toggleCount} section toggle buttons`);
    
    if (toggleCount === 0) {
      throw new Error('No section toggle buttons found. Section collapsing may not be working.');
    }
    
    // Step 5: Test collapsing a section
    console.log('Testing section collapsing...');
    const firstToggleButton = sectionToggleButtons[0];
    
    // Get the section ID
    const sectionId = await firstToggleButton.getAttribute('data-section');
    const sectionTitle = await firstToggleButton.getAttribute('data-section-title');
    console.log(`Testing section: "${sectionTitle}" (ID: ${sectionId})`);
    
    // Check if content is initially visible
    const contentSelector = `#${sectionId}-content`;
    const isInitiallyVisible = await page.isVisible(contentSelector);
    console.log(`Section content initially visible: ${isInitiallyVisible}`);
    
    // Click to collapse
    await firstToggleButton.click();
    await page.waitForTimeout(500); // Wait for animation
    
    // Check if content is hidden after collapsing
    const isHiddenAfterCollapse = !(await page.isVisible(contentSelector));
    console.log(`Section hidden after collapse: ${isHiddenAfterCollapse}`);
    
    if (!isHiddenAfterCollapse) {
      throw new Error('Section did not collapse properly');
    }
    
    // Step 6: Test expanding a section
    console.log('Testing section expanding...');
    await firstToggleButton.click();
    await page.waitForTimeout(500); // Wait for animation
    
    // Check if content is visible after expanding
    const isVisibleAfterExpand = await page.isVisible(contentSelector);
    console.log(`Section visible after expand: ${isVisibleAfterExpand}`);
    
    if (!isVisibleAfterExpand) {
      throw new Error('Section did not expand properly');
    }
    
    // Step 7: Test synchronization between original and customized views
    console.log('Testing view synchronization...');
    // Find the corresponding section in the other view
    const otherPrefix = sectionId.startsWith('original') ? 'customized' : 'original';
    const sectionTitleEscaped = sectionTitle.replace(/"/g, '\\"');
    const otherToggleButton = await page.$(`button.section-toggle[data-section-title="${sectionTitleEscaped}"][data-section^="${otherPrefix}"]`);
    
    if (!otherToggleButton) {
      throw new Error('Corresponding section in other view not found');
    }
    
    const otherSectionId = await otherToggleButton.getAttribute('data-section');
    console.log(`Found corresponding section: ${otherSectionId}`);
    
    // Collapse the first section again
    await firstToggleButton.click();
    await page.waitForTimeout(500); // Wait for animation
    
    // Check if the other section collapsed too
    const otherContentSelector = `#${otherSectionId}-content`;
    const isOtherHidden = !(await page.isVisible(otherContentSelector));
    console.log(`Synchronized collapse: ${isOtherHidden}`);
    
    if (!isOtherHidden) {
      throw new Error('Section synchronization is not working properly');
    }
    
    // Step 8: Test state preservation when switching view modes
    console.log('Testing state preservation across view modes...');
    
    // Toggle to original-only view
    await page.click('#toggle-view-btn');
    await page.waitForTimeout(500);
    
    // Toggle to customized-only view
    await page.click('#toggle-view-btn');
    await page.waitForTimeout(500);
    
    // Toggle back to side-by-side view
    await page.click('#toggle-view-btn');
    await page.waitForTimeout(500);
    
    // Check if collapsed state is preserved
    const isStillHiddenAfterViewToggle = !(await page.isVisible(contentSelector));
    console.log(`State preserved after view toggle: ${isStillHiddenAfterViewToggle}`);
    
    if (!isStillHiddenAfterViewToggle) {
      throw new Error('Collapsed state not preserved when switching view modes');
    }
    
    // All tests passed!
    console.log('\n✅ All section collapsing tests passed!');
    
  } catch (error) {
    console.error(`\n❌ Test failed: ${error.message}`);
    // Take a screenshot on failure
    await page.screenshot({ path: 'test-failure.png' });
    console.log('Screenshot saved as test-failure.png');
    throw error;
  } finally {
    // Close browser
    await browser.close();
  }
}

// Run the tests
runTests().catch(err => {
  console.error('Test execution failed:', err);
  process.exit(1);
});