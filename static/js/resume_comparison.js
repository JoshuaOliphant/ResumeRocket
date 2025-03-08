/**
 * Resume Comparison Script
 * Handles the side-by-side comparison of original and customized resumes
 * with diff highlighting using the jsdiff library.
 */

// Initialize variables to store resume content
let originalContent = '';
let customizedContent = '';
let diffResults = null;

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
    
    // Update the summary
    updateChangeSummary(changes);
    
    // Highlight differences
    highlightDifferences();
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
 * Update the change summary in the UI
 */
function updateChangeSummary(changes) {
    const changesCountElement = document.getElementById('changes-count');
    const summaryDetailsElement = document.getElementById('summary-details');
    
    if (changesCountElement) {
        changesCountElement.textContent = `${changes.total} changes`;
    }
    
    if (summaryDetailsElement) {
        summaryDetailsElement.innerHTML = `
            <span class="text-success">${changes.added} additions</span>, 
            <span class="text-danger">${changes.removed} removals</span>
        `;
    }
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