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