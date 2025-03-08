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
    
    // Identify section headers (lines starting with # or ##)
    const sectionRegex = /^(#{1,3})\s+(.+)$/;
    
    // Extract sections from original text
    const originalSections = [];
    let currentSection = null;
    
    originalLines.forEach((line, index) => {
        const match = line.match(sectionRegex);
        if (match) {
            currentSection = {
                level: match[1].length,
                title: match[2].trim(),
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
        const match = line.match(sectionRegex);
        if (match) {
            currentSection = {
                level: match[1].length,
                title: match[2].trim(),
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
    
    const originalElement = document.getElementById('original-resume');
    const customizedElement = document.getElementById('customized-resume');
    
    if (!originalElement || !customizedElement) return;
    
    // Add badges to section headers in original content
    const originalContent = originalElement.innerHTML;
    let modifiedOriginalContent = originalContent;
    
    modifiedSections.originalSections.forEach(section => {
        if (section.modified) {
            // Create regex to find the section header
            const headerRegex = new RegExp(`(^|>)(#{1,3}\\s+${escapeRegExp(section.title)})(\\s|$|<)`, 'gm');
            
            // Replace with header + badge
            modifiedOriginalContent = modifiedOriginalContent.replace(
                headerRegex, 
                `$1$2 <span class="badge bg-warning ms-2" title="This section was modified">Modified</span>$3`
            );
        }
    });
    
    originalElement.innerHTML = modifiedOriginalContent;
    
    // Add badges to section headers in customized content
    const customizedContent = customizedElement.innerHTML;
    let modifiedCustomizedContent = customizedContent;
    
    modifiedSections.customizedSections.forEach(section => {
        if (section.modified) {
            // Create regex to find the section header
            const headerRegex = new RegExp(`(^|>)(#{1,3}\\s+${escapeRegExp(section.title)})(\\s|$|<)`, 'gm');
            
            // Replace with header + badge
            modifiedCustomizedContent = modifiedCustomizedContent.replace(
                headerRegex, 
                `$1$2 <span class="badge bg-success ms-2" title="This section was improved">Improved</span>$3`
            );
        }
    });
    
    customizedElement.innerHTML = modifiedCustomizedContent;
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