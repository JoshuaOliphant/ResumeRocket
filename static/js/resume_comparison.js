/**
 * Resume Comparison Script
 * Handles the side-by-side comparison of original and customized resumes
 * with diff highlighting using the jsdiff library.
 */

// Initialize variables to store resume content
let originalContent = '';
let customizedContent = '';
let diffResults = null;
let modifiedSections = [];
let sectionStates = {}; // Store collapse state of sections

// Search functionality variables
let searchMatches = {
    original: [],
    customized: []
};
let currentMatchIndex = -1;
let currentSearchTerm = '';
let searchScope = 'both'; // 'both', 'original', or 'customized'

/**
 * Initialize the comparison view when the DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Resume comparison script loaded');
    
    // Get the resume content elements
    const originalElement = document.getElementById('original-resume');
    const customizedElement = document.getElementById('customized-resume');
    
    // Store the initial content
    if (originalElement && customizedElement) {
        originalContent = originalElement.innerHTML;
        customizedContent = customizedElement.innerHTML;
        
        // Run the diff analysis
        analyzeDiff();
    }
    
    // Set up event listeners
    setupEventListeners();
});

/**
 * Set up event listeners for UI controls
 */
function setupEventListeners() {
    // Toggle view button
    const toggleViewBtn = document.getElementById('toggle-view-btn');
    if (toggleViewBtn) {
        toggleViewBtn.addEventListener('click', toggleView);
    }
    
    // Show diff only button
    const showDiffBtn = document.getElementById('show-diff-btn');
    if (showDiffBtn) {
        showDiffBtn.addEventListener('click', toggleDiffOnly);
    }
    
    // Search functionality event listeners
    setupSearchEventListeners();
}

/**
 * Set up search-related event listeners
 */
function setupSearchEventListeners() {
    const searchInput = document.getElementById('resume-search-input');
    const clearSearchBtn = document.getElementById('clear-search-btn');
    const prevMatchBtn = document.getElementById('prev-match-btn');
    const nextMatchBtn = document.getElementById('next-match-btn');
    const searchScopeOptions = document.querySelectorAll('input[name="search-scope"]');
    
    if (searchInput) {
        // Add input event listener with debounce for real-time search
        let debounceTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                const searchTerm = this.value.trim();
                if (searchTerm.length >= 2) {
                    performSearch(searchTerm);
                } else if (searchTerm.length === 0) {
                    clearSearch();
                }
            }, 300); // 300ms debounce delay
        });
        
        // Add key event listener for Enter key navigation
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                if (e.shiftKey) {
                    goToPreviousMatch();
                } else {
                    goToNextMatch();
                }
            }
        });
    }
    
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', function() {
            if (searchInput) {
                searchInput.value = '';
                clearSearch();
                searchInput.focus();
            }
        });
    }
    
    if (prevMatchBtn) {
        prevMatchBtn.addEventListener('click', goToPreviousMatch);
    }
    
    if (nextMatchBtn) {
        nextMatchBtn.addEventListener('click', goToNextMatch);
    }
    
    // Add search scope change listeners
    if (searchScopeOptions.length > 0) {
        searchScopeOptions.forEach(option => {
            option.addEventListener('change', function() {
                if (this.checked) {
                    if (this.id === 'search-both') {
                        searchScope = 'both';
                    } else if (this.id === 'search-original') {
                        searchScope = 'original';
                    } else if (this.id === 'search-customized') {
                        searchScope = 'customized';
                    }
                    
                    // Re-run search with new scope if there's an active search
                    if (currentSearchTerm) {
                        performSearch(currentSearchTerm);
                    }
                }
            });
        });
    }
}

/**
 * Toggle between different view modes (side-by-side, original only, customized only)
 */
function toggleView() {
    const originalCol = document.querySelector('.col-md-6:first-child');
    const customizedCol = document.querySelector('.col-md-6:last-child');
    
    if (originalCol.classList.contains('col-md-6') && !customizedCol.classList.contains('d-none')) {
        // Switch to original only
        originalCol.classList.remove('col-md-6');
        originalCol.classList.add('col-md-12');
        customizedCol.classList.add('d-none');
        document.getElementById('toggle-view-btn').textContent = 'Show Customized';
    } else if (customizedCol.classList.contains('d-none')) {
        // Switch to customized only
        customizedCol.classList.remove('d-none');
        originalCol.classList.add('d-none');
        customizedCol.classList.remove('col-md-6');
        customizedCol.classList.add('col-md-12');
        document.getElementById('toggle-view-btn').textContent = 'Show Both';
    } else {
        // Switch back to side-by-side
        originalCol.classList.remove('d-none');
        customizedCol.classList.remove('col-md-12');
        originalCol.classList.remove('col-md-12');
        originalCol.classList.add('col-md-6');
        customizedCol.classList.add('col-md-6');
        document.getElementById('toggle-view-btn').textContent = 'Show Original';
    }
}

/**
 * Toggle showing only the differences or the full content
 */
function toggleDiffOnly() {
    const diffOnlyActive = document.getElementById('show-diff-btn').classList.contains('active');
    
    if (diffOnlyActive) {
        // Show full content
        document.getElementById('show-diff-btn').classList.remove('active');
        document.getElementById('show-diff-btn').textContent = 'Show Diff Only';
        resetContent();
    } else {
        // Show only differences
        document.getElementById('show-diff-btn').classList.add('active');
        document.getElementById('show-diff-btn').textContent = 'Show Full Content';
        showOnlyDifferences();
    }
}

/**
 * Reset the content to show everything
 */
function resetContent() {
    const originalElement = document.getElementById('original-resume');
    const customizedElement = document.getElementById('customized-resume');
    
    if (originalElement && customizedElement) {
        originalElement.innerHTML = originalContent;
        customizedElement.innerHTML = customizedContent;
    }
    
    // Re-highlight differences
    highlightDifferences();
    
    // Re-add section badges
    addSectionBadges();
    
    // Process sections for collapsing/expanding
    processSectionsForCollapsing();
    
    // Restore previous collapse states
    restoreCollapseStates();
}

/**
 * Show only the sections with differences
 */
function showOnlyDifferences() {
    // This functionality would require more advanced parsing
    // For now, we'll just highlight the differences more prominently
    
    const originalElement = document.getElementById('original-resume');
    const customizedElement = document.getElementById('customized-resume');
    
    if (originalElement && customizedElement && diffResults) {
        // Clear the content
        originalElement.innerHTML = '';
        customizedElement.innerHTML = '';
        
        // Only show paragraphs with differences
        diffResults.forEach(part => {
            if (part.added) {
                customizedElement.innerHTML += `<div class="diff-added p-2 mb-2">${part.value}</div>`;
            } else if (part.removed) {
                originalElement.innerHTML += `<div class="diff-removed p-2 mb-2">${part.value}</div>`;
            }
        });
        
        // Process sections for collapsing/expanding
        processSectionsForCollapsing();
    }
}

/**
 * Analyze the differences between original and customized resumes
 */
function analyzeDiff() {
    // Check if the diff library is loaded
    if (typeof Diff === 'undefined') {
        console.error('Diff library not loaded');
        return;
    }
    
    // Clean the HTML content to get plain text for comparison
    const originalText = cleanHtmlContent(originalContent);
    const customizedText = cleanHtmlContent(customizedContent);
    
    // Use the diff library to compare the texts
    // Split by newlines to maintain paragraph structure
    diffResults = Diff.diffLines(originalText, customizedText);
    
    // Count changes
    const changes = countChangesFromDiff(diffResults);
    
    // Identify modified sections
    modifiedSections = identifyModifiedSections(originalText, customizedText, diffResults);
    
    // Update the summary
    updateChangeSummary(changes);
    
    // Highlight differences
    highlightDifferences();
    
    // Add section badges
    addSectionBadges();
    
    // Process sections for collapsing/expanding
    processSectionsForCollapsing();
}

/**
 * Clean HTML content to get plain text
 */
function cleanHtmlContent(htmlContent) {
    // Create a temporary div
    const temp = document.createElement('div');
    temp.innerHTML = htmlContent;
    
    // Return the text content
    return temp.textContent || temp.innerText || '';
}

/**
 * Count changes from diff results
 */
function countChangesFromDiff(diffResult) {
    if (!diffResult) return { added: 0, removed: 0, total: 0 };
    
    let added = 0;
    let removed = 0;
    
    diffResult.forEach(part => {
        if (part.added) {
            // Count words added
            const words = part.value.split(/\s+/).filter(w => w.length > 0);
            added += words.length;
        }
        if (part.removed) {
            // Count words removed
            const words = part.value.split(/\s+/).filter(w => w.length > 0);
            removed += words.length;
        }
    });
    
    return {
        added: added,
        removed: removed,
        total: added + removed
    };
}

/**
 * Identify which sections of the resume were modified
 */
function identifyModifiedSections(originalText, customizedText, diffResult) {
    // Split texts into lines
    const originalLines = originalText.split('\n');
    const customizedLines = customizedText.split('\n');
    
    // Identify section headers (lines starting with # or ##, or all-uppercase lines)
    const markdownHeaderRegex = /^(#{1,3})\s+(.+)$/;
    const uppercaseSectionRegex = /^([A-Z][A-Z\s]+[A-Z])$/;
    
    // Extract sections from original text
    const originalSections = [];
    let currentSection = null;
    
    originalLines.forEach((line, index) => {
        const markdownMatch = line.match(markdownHeaderRegex);
        const uppercaseMatch = line.match(uppercaseSectionRegex);
        
        if (markdownMatch || uppercaseMatch) {
            const title = markdownMatch ? markdownMatch[2].trim() : uppercaseMatch[1].trim();
            const level = markdownMatch ? markdownMatch[1].length : 1;
            
            currentSection = {
                level: level,
                title: title,
                startLine: index,
                endLine: originalLines.length - 1, // Default to end of document
                modified: false
            };
            
            // Update end line of previous section if exists
            if (originalSections.length > 0) {
                originalSections[originalSections.length - 1].endLine = index - 1;
            }
            
            originalSections.push(currentSection);
        }
    });
    
    // Extract sections from customized text
    const customizedSections = [];
    currentSection = null;
    
    customizedLines.forEach((line, index) => {
        const markdownMatch = line.match(markdownHeaderRegex);
        const uppercaseMatch = line.match(uppercaseSectionRegex);
        
        if (markdownMatch || uppercaseMatch) {
            const title = markdownMatch ? markdownMatch[2].trim() : uppercaseMatch[1].trim();
            const level = markdownMatch ? markdownMatch[1].length : 1;
            
            currentSection = {
                level: level,
                title: title,
                startLine: index,
                endLine: customizedLines.length - 1, // Default to end of document
                modified: false
            };
            
            // Update end line of previous section if exists
            if (customizedSections.length > 0) {
                customizedSections[customizedSections.length - 1].endLine = index - 1;
            }
            
            customizedSections.push(currentSection);
        }
    });
    
    // Determine which sections were modified by checking if any diff parts
    // fall within the section boundaries
    let originalLineCounter = 0;
    let customizedLineCounter = 0;
    
    diffResult.forEach(part => {
        const partLines = part.value.split('\n');
        const lineCount = partLines.length;
        
        if (part.added) {
            // Check which customized sections this addition falls into
            const startLine = customizedLineCounter;
            const endLine = customizedLineCounter + lineCount - 1;
            
            customizedSections.forEach(section => {
                // If any part of the diff overlaps with the section, mark it as modified
                if ((startLine <= section.endLine && endLine >= section.startLine)) {
                    section.modified = true;
                }
            });
            
            customizedLineCounter += lineCount;
        } else if (part.removed) {
            // Check which original sections this removal falls into
            const startLine = originalLineCounter;
            const endLine = originalLineCounter + lineCount - 1;
            
            originalSections.forEach(section => {
                // If any part of the diff overlaps with the section, mark it as modified
                if ((startLine <= section.endLine && endLine >= section.startLine)) {
                    section.modified = true;
                }
            });
            
            originalLineCounter += lineCount;
        } else {
            // Unchanged part, just update line counters
            originalLineCounter += lineCount;
            customizedLineCounter += lineCount;
        }
    });
    
    // Get list of modified section titles
    const modifiedSectionTitles = [];
    
    // Add from original sections
    originalSections.forEach(section => {
        if (section.modified && !modifiedSectionTitles.includes(section.title)) {
            modifiedSectionTitles.push(section.title);
        }
    });
    
    // Add from customized sections
    customizedSections.forEach(section => {
        if (section.modified && !modifiedSectionTitles.includes(section.title)) {
            modifiedSectionTitles.push(section.title);
        }
    });
    
    return {
        originalSections,
        customizedSections,
        modifiedSectionTitles
    };
}

/**
 * Add badges to section headers to indicate which were modified
 */
function addSectionBadges() {
    if (!modifiedSections || !modifiedSections.modifiedSectionTitles) return;
    
    const originalHtmlElement = document.getElementById('original-resume-html');
    const customizedHtmlElement = document.getElementById('customized-resume-html');
    
    if (!originalHtmlElement || !customizedHtmlElement) return;
    
    // Add badges to section headers in original content
    modifiedSections.originalSections.forEach(section => {
        if (section.modified) {
            // Find all h tags that could be this section
            const headers = originalHtmlElement.querySelectorAll('h1, h2, h3, h4, h5, h6');
            
            headers.forEach(header => {
                if (header.textContent.trim() === section.title) {
                    // Check if badge already exists
                    if (!header.querySelector('.section-badge')) {
                        const badge = document.createElement('span');
                        badge.className = 'badge bg-warning ms-2 section-badge';
                        badge.title = 'This section was modified';
                        badge.textContent = 'Modified';
                        header.appendChild(badge);
                    }
                }
            });
        }
    });
    
    // Add badges to section headers in customized content
    modifiedSections.customizedSections.forEach(section => {
        if (section.modified) {
            // Find all h tags that could be this section
            const headers = customizedHtmlElement.querySelectorAll('h1, h2, h3, h4, h5, h6');
            
            headers.forEach(header => {
                if (header.textContent.trim() === section.title) {
                    // Check if badge already exists
                    if (!header.querySelector('.section-badge')) {
                        const badge = document.createElement('span');
                        badge.className = 'badge bg-success ms-2 section-badge';
                        badge.title = 'This section was improved';
                        badge.textContent = 'Improved';
                        header.appendChild(badge);
                    }
                }
            });
        }
    });
}

/**
 * Process sections for collapsing/expanding
 * Adds toggle buttons to section headers and makes sections collapsible
 */
function processSectionsForCollapsing() {
    console.log("Processing sections for collapsing/expanding...");
    
    const originalHtmlElement = document.getElementById('original-resume-html');
    const customizedHtmlElement = document.getElementById('customized-resume-html');
    
    if (!originalHtmlElement || !customizedHtmlElement) {
        console.error("Could not find resume HTML elements:", {
            originalHtmlElement: Boolean(originalHtmlElement),
            customizedHtmlElement: Boolean(customizedHtmlElement)
        });
        return;
    }
    
    console.log("Original HTML content length:", originalHtmlElement.innerHTML.length);
    console.log("Customized HTML content length:", customizedHtmlElement.innerHTML.length);
    
    // Process headers in both views
    console.log("Processing markdown headers...");
    const originalHeaderCount = processHeadersForCollapsing(originalHtmlElement, 'original');
    const customizedHeaderCount = processHeadersForCollapsing(customizedHtmlElement, 'customized');
    console.log(`Found ${originalHeaderCount} headers in original, ${customizedHeaderCount} in customized`);
    
    // Handle all-uppercase sections for both views
    console.log("Processing uppercase sections...");
    const originalUppercaseCount = processUppercaseSectionsForCollapsing(originalHtmlElement, 'original');
    const customizedUppercaseCount = processUppercaseSectionsForCollapsing(customizedHtmlElement, 'customized');
    console.log(`Found ${originalUppercaseCount} uppercase sections in original, ${customizedUppercaseCount} in customized`);
    
    console.log("Section processing complete");
}

/**
 * Process markdown headers for collapsing
 */
function processHeadersForCollapsing(container, prefix) {
    // Find all h1-h3 tags that could be section headers
    const headers = container.querySelectorAll('h1, h2, h3');
    console.log(`Found ${headers.length} h1-h3 headers in ${prefix} view`);
    
    if (headers.length === 0) {
        // Try to show some of the HTML to diagnose the issue
        console.log(`${prefix} HTML sample:`, container.innerHTML.substring(0, 200) + '...');
    }
    
    let processedCount = 0;
    
    headers.forEach((header, index) => {
        // Skip if already processed
        if (header.querySelector('.section-toggle')) {
            console.log(`Header ${index} already processed, skipping`);
            return;
        }
        
        const headerText = header.textContent.trim();
        console.log(`Processing header: "${headerText}"`);
        
        const sectionId = `${prefix}-section-${index}`;
        const sectionContent = collectSectionContent(header);
        
        console.log(`Found ${sectionContent.length} content elements for this section`);
        
        if (sectionContent.length > 0) {
            // Create the section wrapper
            const sectionWrapper = document.createElement('div');
            sectionWrapper.classList.add('resume-section');
            sectionWrapper.id = sectionId;
            
            // Create toggle button
            const toggleButton = document.createElement('button');
            toggleButton.classList.add('section-toggle', 'btn', 'btn-sm');
            toggleButton.setAttribute('type', 'button');
            toggleButton.setAttribute('data-section', sectionId);
            toggleButton.setAttribute('data-section-title', headerText);
            toggleButton.innerHTML = '<i class="bi bi-chevron-down"></i>';
            toggleButton.title = 'Toggle section';
            
            // Add the toggle button to the header
            header.classList.add('d-flex', 'align-items-center', 'justify-content-between');
            header.prepend(toggleButton);
            
            // Create content container
            const contentContainer = document.createElement('div');
            contentContainer.classList.add('section-content');
            contentContainer.id = `${sectionId}-content`;
            
            // Move content into container
            sectionContent.forEach(element => {
                contentContainer.appendChild(element);
            });
            
            // Insert header and content container after the original header
            header.parentNode.insertBefore(sectionWrapper, header.nextSibling);
            sectionWrapper.appendChild(header);
            sectionWrapper.appendChild(contentContainer);
            
            // Set up event listener for toggle
            toggleButton.addEventListener('click', function() {
                toggleSection(sectionId);
            });
            
            processedCount++;
            console.log(`Successfully processed section: ${headerText}`);
        } else {
            console.log(`No content for section: ${headerText}, skipping`);
        }
    });
    
    return processedCount;
}

/**
 * Process all-uppercase text sections for collapsing
 */
function processUppercaseSectionsForCollapsing(container, prefix) {
    // Find all p tags that could be uppercase section headers
    const paragraphs = container.querySelectorAll('p');
    console.log(`Found ${paragraphs.length} paragraphs in ${prefix} view`);
    
    if (paragraphs.length === 0) {
        console.log(`No paragraphs found in ${prefix} view`);
        return 0;
    }
    
    let processedCount = 0;
    
    paragraphs.forEach((paragraph, index) => {
        const text = paragraph.textContent.trim();
        // Check if the paragraph text is all uppercase and at least 3 characters
        if (text === text.toUpperCase() && text.length >= 3 && text === text.replace(/[^A-Z\s]/g, '')) {
            console.log(`Found uppercase paragraph: "${text}"`);
            
            // Skip if already processed
            if (paragraph.querySelector('.section-toggle')) {
                console.log(`Paragraph ${index} already processed, skipping`);
                return;
            }
            
            const sectionId = `${prefix}-uppercase-section-${index}`;
            const sectionContent = collectSectionContent(paragraph);
            
            console.log(`Found ${sectionContent.length} content elements for this uppercase section`);
            
            if (sectionContent.length > 0) {
                // Create the section wrapper
                const sectionWrapper = document.createElement('div');
                sectionWrapper.classList.add('resume-section');
                sectionWrapper.id = sectionId;
                
                // Make the paragraph look like a header
                paragraph.classList.add('fw-bold', 'fs-5', 'd-flex', 'align-items-center', 'justify-content-between');
                
                // Create toggle button
                const toggleButton = document.createElement('button');
                toggleButton.classList.add('section-toggle', 'btn', 'btn-sm');
                toggleButton.setAttribute('type', 'button');
                toggleButton.setAttribute('data-section', sectionId);
                toggleButton.setAttribute('data-section-title', text);
                toggleButton.innerHTML = '<i class="bi bi-chevron-down"></i>';
                toggleButton.title = 'Toggle section';
                
                // Add the toggle button to the paragraph
                paragraph.prepend(toggleButton);
                
                // Create content container
                const contentContainer = document.createElement('div');
                contentContainer.classList.add('section-content');
                contentContainer.id = `${sectionId}-content`;
                
                // Move content into container
                sectionContent.forEach(element => {
                    contentContainer.appendChild(element);
                });
                
                // Insert paragraph and content container after the original paragraph
                paragraph.parentNode.insertBefore(sectionWrapper, paragraph.nextSibling);
                sectionWrapper.appendChild(paragraph);
                sectionWrapper.appendChild(contentContainer);
                
                // Set up event listener for toggle
                toggleButton.addEventListener('click', function() {
                    toggleSection(sectionId);
                });
                
                processedCount++;
                console.log(`Successfully processed uppercase section: ${text}`);
            } else {
                console.log(`No content for uppercase section: ${text}, skipping`);
            }
        }
    });
    
    return processedCount;
}

/**
 * Collect all content elements that belong to a section
 */
function collectSectionContent(header) {
    console.log(`Collecting content for section with tag ${header.tagName} and text "${header.textContent.trim()}"`);
    
    const content = [];
    let nextElement = header.nextElementSibling;
    
    // Get the header level to determine when to stop collecting
    const headerTagName = header.tagName;
    console.log(`Header tag: ${headerTagName}`);
    
    if (!nextElement) {
        console.log('No next element found after header');
        return content;
    }
    
    let count = 0;
    while (nextElement && count < 20) { // Limit to prevent infinite loops
        count++;
        
        console.log(`Examining element: ${nextElement.tagName}, text: "${nextElement.textContent.substring(0, 30).trim()}${nextElement.textContent.length > 30 ? '...' : ''}"`);
        
        // Stop when we hit another header of the same or higher level
        if (nextElement.tagName && 
            (nextElement.tagName === headerTagName || isHigherLevelHeader(nextElement.tagName, headerTagName))) {
            console.log(`Stopping at element with tag ${nextElement.tagName} (same or higher level than ${headerTagName})`);
            break;
        }
        
        // Store the element for moving later
        const elementToMove = nextElement;
        nextElement = nextElement.nextElementSibling;
        content.push(elementToMove);
    }
    
    console.log(`Collected ${content.length} content elements for this section`);
    return content;
}

/**
 * Check if one header is of higher level than another
 */
function isHigherLevelHeader(headerTag1, headerTag2) {
    const headerLevels = {
        'H1': 1,
        'H2': 2,
        'H3': 3,
        'H4': 4,
        'H5': 5,
        'H6': 6
    };
    
    return headerLevels[headerTag1] <= headerLevels[headerTag2];
}

/**
 * Toggle the visibility of a section
 */
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const content = document.getElementById(`${sectionId}-content`);
    const toggle = section.querySelector('.section-toggle');
    const title = toggle.getAttribute('data-section-title');
    
    if (!content) return;
    
    // Get the other section if it exists (to keep both sides in sync)
    const otherPrefix = sectionId.startsWith('original') ? 'customized' : 'original';
    let otherSectionToggle = null;
    
    // Find the matching section in the other view by section title
    const otherToggles = document.querySelectorAll(`.section-toggle[data-section-title="${title.replace(/"/g, '\\"')}"]`);
    otherToggles.forEach(btn => {
        if (btn.getAttribute('data-section').startsWith(otherPrefix)) {
            otherSectionToggle = btn;
        }
    });
    
    // Toggle this section
    if (content.style.display === 'none') {
        // Expand
        content.style.display = 'block';
        content.style.maxHeight = content.scrollHeight + 'px';
        toggle.innerHTML = '<i class="bi bi-chevron-down"></i>';
        // Store state
        sectionStates[title] = 'expanded';
    } else {
        // Collapse
        content.style.maxHeight = '0px';
        setTimeout(() => {
            content.style.display = 'none';
        }, 300); // Match the transition time
        toggle.innerHTML = '<i class="bi bi-chevron-right"></i>';
        // Store state
        sectionStates[title] = 'collapsed';
    }
    
    // Toggle the matching section in the other view if it exists
    if (otherSectionToggle) {
        const otherSectionId = otherSectionToggle.getAttribute('data-section');
        const otherSection = document.getElementById(otherSectionId);
        const otherContent = document.getElementById(`${otherSectionId}-content`);
        
        if (otherContent) {
            if (content.style.display === 'none') {
                // Other should collapse too
                otherContent.style.maxHeight = '0px';
                setTimeout(() => {
                    otherContent.style.display = 'none';
                }, 300);
                otherSectionToggle.innerHTML = '<i class="bi bi-chevron-right"></i>';
            } else {
                // Other should expand too
                otherContent.style.display = 'block';
                otherContent.style.maxHeight = otherContent.scrollHeight + 'px';
                otherSectionToggle.innerHTML = '<i class="bi bi-chevron-down"></i>';
            }
        }
    }
}

/**
 * Restore the collapse states after content reloading
 */
function restoreCollapseStates() {
    // For each stored section state
    Object.keys(sectionStates).forEach(title => {
        // Find all toggles for this section title
        const toggles = document.querySelectorAll(`.section-toggle[data-section-title="${title.replace(/"/g, '\\"')}"]`);
        
        toggles.forEach(toggle => {
            const sectionId = toggle.getAttribute('data-section');
            const content = document.getElementById(`${sectionId}-content`);
            
            if (content && sectionStates[title] === 'collapsed') {
                // Apply collapsed state
                content.style.display = 'none';
                content.style.maxHeight = '0px';
                toggle.innerHTML = '<i class="bi bi-chevron-right"></i>';
            }
        });
    });
}

/**
 * Escape special characters for use in regex
 */
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Perform search across both resume versions
 */
function performSearch(searchTerm) {
    // Store the current search term
    currentSearchTerm = searchTerm;
    
    // Clear previous search results
    clearSearchHighlights();
    
    // Reset match data
    searchMatches = {
        original: [],
        customized: []
    };
    currentMatchIndex = -1;
    
    // Get the containers to search in
    const originalHtmlElement = document.getElementById('original-resume-html');
    const customizedHtmlElement = document.getElementById('customized-resume-html');
    
    if (!originalHtmlElement || !customizedHtmlElement) {
        console.error('Resume content containers not found');
        return;
    }
    
    if (searchScope === 'both' || searchScope === 'original') {
        // Search original resume
        searchMatches.original = searchInContainer(originalHtmlElement, searchTerm);
    }
    
    if (searchScope === 'both' || searchScope === 'customized') {
        // Search customized resume
        searchMatches.customized = searchInContainer(customizedHtmlElement, searchTerm);
    }
    
    // Total match count
    const totalMatches = searchMatches.original.length + searchMatches.customized.length;
    
    // Update UI with search results
    const searchResultsInfo = document.getElementById('search-results-info');
    const searchCount = document.getElementById('search-count');
    const prevMatchBtn = document.getElementById('prev-match-btn');
    const nextMatchBtn = document.getElementById('next-match-btn');
    const matchPosition = document.getElementById('match-position');
    
    if (searchResultsInfo && searchCount) {
        if (totalMatches > 0) {
            searchResultsInfo.classList.remove('d-none');
            searchCount.textContent = `${totalMatches} match${totalMatches !== 1 ? 'es' : ''}`;
            
            // Enable navigation buttons
            if (prevMatchBtn) prevMatchBtn.disabled = totalMatches <= 1;
            if (nextMatchBtn) nextMatchBtn.disabled = totalMatches <= 1;
            
            // Set initial match position
            if (matchPosition) matchPosition.textContent = 'Match 0 of ' + totalMatches;
            
            // Go to first match
            goToNextMatch();
        } else {
            searchResultsInfo.classList.remove('d-none');
            searchCount.textContent = 'No matches';
            
            // Disable navigation buttons
            if (prevMatchBtn) prevMatchBtn.disabled = true;
            if (nextMatchBtn) nextMatchBtn.disabled = true;
            
            // Clear match position
            if (matchPosition) matchPosition.textContent = 'Match 0 of 0';
        }
    }
}

/**
 * Search for text in a container and highlight matches
 */
function searchInContainer(container, searchTerm) {
    const matches = [];
    
    if (!container || !searchTerm || searchTerm.length < 2) return matches;
    
    // Escape special characters in the search term for regex
    const escSearchTerm = escapeRegExp(searchTerm);
    
    // Create a regex that matches the search term (case insensitive)
    const regex = new RegExp(escSearchTerm, 'gi');
    
    // Get all text nodes in the container
    const textNodes = getTextNodesIn(container);
    
    // Keep track of replaced nodes to avoid double-processing
    const processedNodes = new Set();
    
    // Process each text node
    textNodes.forEach(node => {
        if (processedNodes.has(node)) return;
        
        const text = node.nodeValue;
        if (!text || regex.test(text) === false) return;
        
        // Reset regex lastIndex
        regex.lastIndex = 0;
        
        const parent = node.parentNode;
        const originalHTML = parent.innerHTML;
        
        // Split text into segments with or without matches
        const segments = [];
        let lastIndex = 0;
        let match;
        
        // Create a new regex for each iteration to avoid lastIndex issues
        const matchRegex = new RegExp(escSearchTerm, 'gi');
        while ((match = matchRegex.exec(text)) !== null) {
            // Add text before match
            if (match.index > lastIndex) {
                segments.push({
                    text: text.slice(lastIndex, match.index),
                    isMatch: false
                });
            }
            
            // Add match
            segments.push({
                text: match[0],
                isMatch: true,
                position: {
                    container: container.id,
                    node: Array.from(container.querySelectorAll('*')).indexOf(parent),
                    start: match.index,
                    end: match.index + match[0].length
                }
            });
            
            // Store match info for navigation
            matches.push({
                container: container.id,
                element: parent,
                matchText: match[0],
                startOffset: match.index,
                endOffset: matchRegex.lastIndex
            });
            
            lastIndex = matchRegex.lastIndex;
        }
        
        // Add remaining text after last match
        if (lastIndex < text.length) {
            segments.push({
                text: text.slice(lastIndex),
                isMatch: false
            });
        }
        
        // If we found matches, replace the node with highlighted content
        if (segments.length > 1) {
            let html = '';
            segments.forEach(segment => {
                if (segment.isMatch) {
                    html += `<span class="search-highlight" data-match-container="${container.id}" data-match-index="${matches.length - 1}">${segment.text}</span>`;
                } else {
                    html += segment.text;
                }
            });
            
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            
            // Replace the original content with the highlighted version
            while (tempDiv.firstChild) {
                parent.insertBefore(tempDiv.firstChild, node);
                processedNodes.add(tempDiv.firstChild);
            }
            
            // Remove the original node
            parent.removeChild(node);
        }
    });
    
    return matches;
}

/**
 * Get all text nodes within a container
 */
function getTextNodesIn(container) {
    const textNodes = [];
    const walk = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null, false);
    
    let node;
    while (node = walk.nextNode()) {
        // Skip if node's parent is already a search highlight or in a script/style tag
        const parent = node.parentNode;
        if (parent.classList && parent.classList.contains('search-highlight')) continue;
        if (parent.nodeName === 'SCRIPT' || parent.nodeName === 'STYLE') continue;
        
        textNodes.push(node);
    }
    
    return textNodes;
}

/**
 * Go to the next search match
 */
function goToNextMatch() {
    if (!searchMatches) return;
    
    const totalMatches = searchMatches.original.length + searchMatches.customized.length;
    if (totalMatches === 0) return;
    
    // Increment current match index
    currentMatchIndex = (currentMatchIndex + 1) % totalMatches;
    
    // Navigate to the current match
    navigateToMatch(currentMatchIndex);
}

/**
 * Go to the previous search match
 */
function goToPreviousMatch() {
    if (!searchMatches) return;
    
    const totalMatches = searchMatches.original.length + searchMatches.customized.length;
    if (totalMatches === 0) return;
    
    // Decrement current match index
    currentMatchIndex = (currentMatchIndex - 1 + totalMatches) % totalMatches;
    
    // Navigate to the current match
    navigateToMatch(currentMatchIndex);
}

/**
 * Navigate to a specific match by index
 */
function navigateToMatch(index) {
    // Remove active match highlighting from all matches
    const allHighlights = document.querySelectorAll('.search-highlight');
    allHighlights.forEach(highlight => {
        highlight.classList.remove('search-active-match', 'search-match-pulse');
    });
    
    // Calculate which array and index to use
    let matchObj = null;
    if (index < searchMatches.original.length) {
        matchObj = searchMatches.original[index];
    } else {
        matchObj = searchMatches.customized[index - searchMatches.original.length];
    }
    
    if (!matchObj) return;
    
    // Find the highlight element for this match
    const highlightElement = document.querySelector(`.search-highlight[data-match-container="${matchObj.container}"][data-match-index="${index < searchMatches.original.length ? index : index - searchMatches.original.length}"]`);
    
    if (highlightElement) {
        // Add active match class
        highlightElement.classList.add('search-active-match', 'search-match-pulse');
        
        // Scroll to the match
        highlightElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
        
        // If match is in a collapsed section, expand it
        const parentSection = findParentSection(highlightElement);
        if (parentSection) {
            const content = document.getElementById(parentSection.id + '-content');
            const toggle = parentSection.querySelector('.section-toggle');
            
            if (content && toggle && content.style.display === 'none') {
                // Expand the section
                content.style.display = 'block';
                content.style.maxHeight = content.scrollHeight + 'px';
                toggle.innerHTML = '<i class="bi bi-chevron-down"></i>';
                
                // Update section state
                const title = toggle.getAttribute('data-section-title');
                sectionStates[title] = 'expanded';
                
                // Also expand the matching section in the other view if needed
                const otherPrefix = parentSection.id.startsWith('original') ? 'customized' : 'original';
                const otherToggles = document.querySelectorAll(`.section-toggle[data-section-title="${title.replace(/"/g, '\\"')}"]`);
                otherToggles.forEach(btn => {
                    if (btn.getAttribute('data-section').startsWith(otherPrefix)) {
                        const otherSectionId = btn.getAttribute('data-section');
                        const otherContent = document.getElementById(`${otherSectionId}-content`);
                        
                        if (otherContent && otherContent.style.display === 'none') {
                            otherContent.style.display = 'block';
                            otherContent.style.maxHeight = otherContent.scrollHeight + 'px';
                            btn.innerHTML = '<i class="bi bi-chevron-down"></i>';
                        }
                    }
                });
            }
        }
        
        // Update match position display
        const matchPosition = document.getElementById('match-position');
        if (matchPosition) {
            const totalMatches = searchMatches.original.length + searchMatches.customized.length;
            matchPosition.textContent = `Match ${index + 1} of ${totalMatches}`;
        }
    }
}

/**
 * Find the parent section of an element
 */
function findParentSection(element) {
    let current = element;
    while (current) {
        if (current.classList && current.classList.contains('resume-section')) {
            return current;
        }
        current = current.parentElement;
    }
    return null;
}

/**
 * Clear all search highlights
 */
function clearSearchHighlights() {
    const originalHtml = document.getElementById('original-resume-html');
    const customizedHtml = document.getElementById('customized-resume-html');
    
    if (originalHtml) {
        // Replace all highlighted spans with their text content
        const highlights = originalHtml.querySelectorAll('.search-highlight');
        highlights.forEach(highlight => {
            const textNode = document.createTextNode(highlight.textContent);
            highlight.parentNode.replaceChild(textNode, highlight);
        });
    }
    
    if (customizedHtml) {
        // Replace all highlighted spans with their text content
        const highlights = customizedHtml.querySelectorAll('.search-highlight');
        highlights.forEach(highlight => {
            const textNode = document.createTextNode(highlight.textContent);
            highlight.parentNode.replaceChild(textNode, highlight);
        });
    }
}

/**
 * Clear all search results and highlights
 */
function clearSearch() {
    // Clear highlights
    clearSearchHighlights();
    
    // Reset match data
    searchMatches = {
        original: [],
        customized: []
    };
    currentMatchIndex = -1;
    currentSearchTerm = '';
    
    // Update UI
    const searchResultsInfo = document.getElementById('search-results-info');
    if (searchResultsInfo) {
        searchResultsInfo.classList.add('d-none');
    }
    
    // Disable navigation buttons
    const prevMatchBtn = document.getElementById('prev-match-btn');
    const nextMatchBtn = document.getElementById('next-match-btn');
    if (prevMatchBtn) prevMatchBtn.disabled = true;
    if (nextMatchBtn) nextMatchBtn.disabled = true;
}

/**
 * Update the change summary in the UI
 */
function updateChangeSummary(changes) {
    const changesCountElement = document.getElementById('changes-count');
    const summaryDetailsElement = document.getElementById('summary-details');
    const changeSummaryElement = document.getElementById('change-summary');
    
    if (changesCountElement) {
        // Animate the count from 0 to the total number of changes
        animateCount(changesCountElement, 0, changes.total);
    }
    
    if (summaryDetailsElement && modifiedSections && modifiedSections.modifiedSectionTitles) {
        let summaryHTML = `
            <span class="text-success fade-in-up delay-1">${changes.added} additions</span>, 
            <span class="text-danger fade-in-up delay-2">${changes.removed} removals</span>
        `;
        
        // Add section summary if we have modified sections
        if (modifiedSections.modifiedSectionTitles.length > 0) {
            summaryHTML += `<div class="mt-2 fade-in-up delay-3">Modified sections: `;
            
            modifiedSections.modifiedSectionTitles.forEach((title, index) => {
                // Add staggered delay for each badge
                const delay = Math.min(index + 4, 10); // Cap at delay-10
                summaryHTML += `<span class="badge bg-info me-1 fade-in-up delay-${delay}">${title}</span>`;
            });
            
            summaryHTML += `</div>`;
        }
        
        summaryDetailsElement.innerHTML = summaryHTML;
    }
    
    // Add highlight pulse animation to the summary card
    if (changeSummaryElement) {
        // Remove any existing animation class first
        changeSummaryElement.classList.remove('highlight-pulse');
        
        // Force a reflow to restart the animation
        void changeSummaryElement.offsetWidth;
        
        // Add the animation class
        changeSummaryElement.classList.add('highlight-pulse');
    }
}

/**
 * Animate counting from start to end
 */
function animateCount(element, start, end) {
    // If the difference is small, don't animate
    if (end - start < 5) {
        element.textContent = `${end} changes`;
        return;
    }
    
    // Duration in milliseconds
    const duration = 1000;
    // Number of steps
    const steps = 20;
    // Time per step
    const stepTime = duration / steps;
    
    let current = start;
    const increment = (end - start) / steps;
    
    // Clear any existing interval
    if (element.countInterval) {
        clearInterval(element.countInterval);
    }
    
    // Start the animation
    element.countInterval = setInterval(() => {
        current += increment;
        
        // Round to nearest integer
        const rounded = Math.round(current);
        
        // Update the element
        element.textContent = `${rounded} changes`;
        
        // Check if we've reached the end
        if (rounded >= end) {
            clearInterval(element.countInterval);
            element.textContent = `${end} changes`;
        }
    }, stepTime);
}

/**
 * Highlight the differences in the UI using the diff library
 */
function highlightDifferences() {
    if (!diffResults) return;

    const originalElement = document.getElementById('original-resume');
    const customizedElement = document.getElementById('customized-resume');
    
    if (!originalElement || !customizedElement) return;
    
    // Make a copy of the original content
    const originalClean = cleanHtmlContent(originalContent);
    const customizedClean = cleanHtmlContent(customizedContent);
    
    // Apply spans for word-by-word diff (this is a more detailed approach)
    const wordDiff = Diff.diffWords(originalClean, customizedClean);
    
    // Build HTML with diff highlighting for both sides
    let originalHtml = '';
    let customizedHtml = '';
    
    wordDiff.forEach(part => {
        if (part.added) {
            // Added parts only show in customized
            customizedHtml += `<span class="diff-added">${part.value}</span>`;
        } else if (part.removed) {
            // Removed parts only show in original
            originalHtml += `<span class="diff-removed">${part.value}</span>`;
        } else {
            // Unchanged parts show in both
            originalHtml += part.value;
            customizedHtml += part.value;
        }
    });
    
    // Update the content with highlighting
    originalElement.innerHTML = originalHtml;
    customizedElement.innerHTML = customizedHtml;
}