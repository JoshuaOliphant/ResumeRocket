/**
 * ResumeRocket Resume Customization Streaming
 * Handles streaming customization of resumes
 */

document.addEventListener('DOMContentLoaded', function() {
    setupResumeCustomizationStreaming();
});

/**
 * Handle streaming resume customization
 */
function setupResumeCustomizationStreaming() {
    // Get form and required elements
    const form = document.getElementById('customizeForm');
    if (!form) return;
    
    const resultsContainer = document.getElementById('streaming-results');
    if (!resultsContainer) return;
    
    // Create content sections
    const progressSection = document.createElement('div');
    progressSection.className = 'mb-6';
    progressSection.innerHTML = `
        <h5 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Customization Progress</h5>
        <div class="progress-tracker">
            <div class="progress-step" data-stage="initialization">1. Initialization</div>
            <div class="progress-step" data-stage="analysis">2. Analysis</div>
            <div class="progress-step" data-stage="planning">3. Planning</div>
            <div class="progress-step" data-stage="implementation">4. Implementation</div>
            <div class="progress-step" data-stage="final_analysis">5. Final Analysis</div>
            <div class="progress-step" data-stage="comparison">6. Comparison</div>
        </div>
        <div class="current-status mt-3 text-sm text-gray-700 dark:text-gray-300">Starting customization process...</div>
    `;
    
    const analyticsSection = document.createElement('div');
    analyticsSection.className = 'mb-6';
    analyticsSection.innerHTML = `
        <h5 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Resume Analysis</h5>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-sm">
            <div id="analytics-content">
                <div class="flex justify-center items-center py-8">
                    <svg class="animate-spin h-8 w-8 text-accent-light" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                </div>
            </div>
        </div>
    `;
    
    const recommendationsSection = document.createElement('div');
    recommendationsSection.className = 'mb-6';
    recommendationsSection.innerHTML = `
        <h5 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Optimization Recommendations</h5>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-sm">
            <div id="planning-stream" class="planning-content mb-4 streaming-content"></div>
            <div id="recommendations-list" class="recommendations-list"></div>
        </div>
    `;
    
    const implementationSection = document.createElement('div');
    implementationSection.className = 'mb-6';
    implementationSection.innerHTML = `
        <h5 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Implementation</h5>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-sm">
            <div id="implementation-stream" class="implementation-content streaming-content"></div>
        </div>
    `;
    
    const resultsSection = document.createElement('div');
    resultsSection.className = 'mb-6';
    resultsSection.innerHTML = `
        <h5 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Final Results</h5>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-sm">
            <div id="results-content">
                <div class="text-center py-6 text-gray-600 dark:text-gray-400">
                    <p>Waiting for customization to complete...</p>
                </div>
            </div>
        </div>
    `;
    
    // Add sections to container
    resultsContainer.innerHTML = '';
    resultsContainer.appendChild(progressSection);
    resultsContainer.appendChild(analyticsSection);
    resultsContainer.appendChild(recommendationsSection);
    resultsContainer.appendChild(implementationSection);
    resultsContainer.appendChild(resultsSection);
    
    // Track streaming state
    let sessionId = null;
    let customizationComplete = false;
    let resumeData = {
        original_content: null,
        customized_content: null,
        original_score: 0,
        new_score: 0,
        improvement: 0,
        recommendations: []
    };
    
    // Set up form submission handler
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show streaming UI
        resultsContainer.classList.remove('d-none');
        
        // Initialize progress tracker immediately to show something is happening
        updateProgressTracker('initialization');
        updateStatusMessage('Starting customization process...');
        
        // Get form data
        const formData = new FormData(form);
        
        // Add CSRF token if not already present
        if (!formData.get('csrf_token')) {
            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
            formData.append('csrf_token', csrfToken);
        }
        
        // Get API URL from form data attribute or use default
        const apiUrl = form.getAttribute('data-api-url') || '/api/customize_resume_streaming';
        console.log("Using API URL:", apiUrl);
        
        // Start fetch request
        fetch(apiUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrf_token')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            // Get reader from response body
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            
            // Function to process stream
            function processStream({ done, value }) {
                // If we're done, return
                if (done) {
                    console.log('Stream complete');
                    
                    // Finalize UI if needed
                    if (!customizationComplete) {
                        displayCompletionStatus();
                    }
                    
                    return;
                }
                
                // Decode chunk and add to buffer
                buffer += decoder.decode(value, { stream: true });
                
                // Process complete JSON objects
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep last incomplete line in buffer
                
                lines.forEach(line => {
                    if (!line.trim()) return;
                    
                    try {
                        const data = JSON.parse(line);
                        handleStreamEvent(data);
                    } catch (e) {
                        console.error('Error parsing streaming data:', e, line);
                    }
                });
                
                // Continue reading
                return reader.read().then(processStream);
            }
            
            // Start processing
            return reader.read().then(processStream);
        })
        .catch(error => {
            console.error('Streaming error:', error);
            
            // Show error in UI
            const statusElement = document.querySelector('.current-status');
            if (statusElement) {
                statusElement.textContent = `Error: ${error.message}`;
                statusElement.classList.add('text-danger');
            }
        });
    });

    /**
     * Handle streaming events
     */
    function handleStreamEvent(data) {
        console.log('Stream event:', data.type);
        
        switch (data.type) {
            case 'session_start':
                sessionId = data.session_id;
                break;
                
            case 'status':
                updateProgressTracker(data.stage);
                updateStatusMessage(data.message);
                break;
                
            case 'analysis_complete':
                updateAnalytics(data.data);
                break;
                
            case 'planning_chunk':
                appendPlanningChunk(data.content);
                break;
                
            case 'planning_complete':
                updatePlanningComplete(data.data);
                break;
                
            case 'recommendation':
                addRecommendation(data.id, data.data);
                // Save for later
                resumeData.recommendations.push(data.data);
                break;
                
            case 'recommendations_filtered':
                updateFilteredRecommendations(data.count);
                break;
                
            case 'implementation_chunk':
                appendImplementationChunk(data.content);
                break;
                
            case 'implementation_complete':
                // Mark sections as complete
                markImplementationComplete(data.sections_modified);
                break;
                
            case 'final_analysis_complete':
                updateFinalAnalytics(data.data);
                // Save scores
                resumeData.original_score = data.data.original_score;
                resumeData.new_score = data.data.new_score;
                resumeData.improvement = data.data.improvement;
                break;
                
            case 'comparison_complete':
                // Update comparison data
                updateComparisonData(data.data);
                break;
                
            case 'customization_complete':
                customizationComplete = true;
                resumeData = {
                    ...resumeData,
                    original_content: data.data.original_content,
                    customized_content: data.data.customized_content,
                    optimization_plan: data.data.optimization_plan,
                    comparison_data: data.data.comparison_data
                };
                displayFinalResults(data.data);
                // Show save button
                displaySaveOptions(data.data);
                break;
                
            case 'error':
                displayError(data.message);
                break;
        }
    }

    /**
     * Update the progress tracker
     */
    function updateProgressTracker(stage) {
        // Find all steps in the tracker
        const steps = document.querySelectorAll('.progress-step');
        
        // Reset all steps
        steps.forEach(step => {
            step.classList.remove('active', 'completed');
        });
        
        // Mark current stage and earlier stages
        let foundCurrent = false;
        steps.forEach(step => {
            const stepStage = step.getAttribute('data-stage');
            
            if (stepStage === stage) {
                step.classList.add('active');
                foundCurrent = true;
            } else if (!foundCurrent) {
                step.classList.add('completed');
            }
        });
    }

    /**
     * Update the status message
     */
    function updateStatusMessage(message) {
        const statusElement = document.querySelector('.current-status');
        if (statusElement) {
            statusElement.textContent = message;
        }
    }

    /**
     * Update the analytics section
     */
    function updateAnalytics(atsResults) {
        const analyticsContent = document.getElementById('analytics-content');
        if (!analyticsContent) return;
        
        let html = '';
        
        // Create score display
        html += `
        <div class="mb-6">
            <div class="flex justify-between items-center mb-2">
                <span class="text-gray-900 dark:text-white font-medium">ATS Score</span>
                <span class="text-accent-dark dark:text-accent-light font-medium">${atsResults.score.toFixed(1)}%</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mb-4">
                <div class="bg-accent-light h-2.5 rounded-full" style="width: ${atsResults.score}%"></div>
            </div>
        </div>
        `;
        
        // Add keywords
        const matchingKeywords = atsResults.matching_keywords || [];
        const missingKeywords = atsResults.missing_keywords || [];
        
        html += `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <h6 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Matching Keywords</h6>
                <div class="flex flex-wrap gap-2">
                    ${matchingKeywords.slice(0, 20).map(kw => `<span class="px-2 py-0.5 text-xs font-medium rounded-full bg-accent-light/80 text-white">${kw}</span>`).join('')}
                    ${matchingKeywords.length > 20 ? `<span class="px-2 py-0.5 text-xs font-medium rounded-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300">+${matchingKeywords.length - 20} more</span>` : ''}
                </div>
            </div>
            <div>
                <h6 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Missing Keywords</h6>
                <div class="flex flex-wrap gap-2">
                    ${missingKeywords.slice(0, 20).map(kw => `<span class="px-2 py-0.5 text-xs font-medium rounded-full bg-orange-200 dark:bg-orange-900/40 text-orange-800 dark:text-orange-200">${kw}</span>`).join('')}
                    ${missingKeywords.length > 20 ? `<span class="px-2 py-0.5 text-xs font-medium rounded-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300">+${missingKeywords.length - 20} more</span>` : ''}
                </div>
            </div>
        </div>
        `;
        
        analyticsContent.innerHTML = html;
    }

    /**
     * Append a planning chunk to the planning stream
     */
    function appendPlanningChunk(content) {
        const planningStream = document.getElementById('planning-stream');
        if (!planningStream) return;
        
        // If first chunk, clear loading indicator
        if (planningStream.innerHTML === '') {
            planningStream.innerHTML = '<div class="typed-text"></div>';
        }
        
        const typedText = planningStream.querySelector('.typed-text');
        if (typedText) {
            typedText.innerHTML += content;
            
            // Auto-scroll to follow content
            typedText.scrollTop = typedText.scrollHeight;
        }
    }

    /**
     * Update when planning is complete
     */
    function updatePlanningComplete(data) {
        const planningStream = document.getElementById('planning-stream');
        if (planningStream) {
            const typedText = planningStream.querySelector('.typed-text');
            if (typedText) {
                typedText.classList.add('complete');
            }
        }
        
        // Update the recommendations count
        const recommendationsSection = document.querySelector('.recommendations-section h5');
        if (recommendationsSection) {
            recommendationsSection.textContent = `Optimization Recommendations (${data.recommendation_count})`;
        }
    }

    /**
     * Add a recommendation to the list
     */
    function addRecommendation(id, data) {
        const recommendationsList = document.getElementById('recommendations-list');
        if (!recommendationsList) return;
        
        // Create recommendation card
        const card = document.createElement('div');
        card.className = 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm mb-4 overflow-hidden';
        card.innerHTML = `
        <div class="bg-gray-100 dark:bg-gray-700 px-4 py-3 flex justify-between items-center">
            <h6 class="font-medium text-gray-900 dark:text-white m-0">${data.section}</h6>
        </div>
        <div class="p-4">
            <h6 class="font-medium text-gray-900 dark:text-white">${data.what}</h6>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">${data.why}</p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                    <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                        <div class="bg-gray-200 dark:bg-gray-700 px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300">Before</div>
                        <div class="p-3 bg-gray-50 dark:bg-gray-800">
                            <pre class="text-xs whitespace-pre-wrap text-gray-700 dark:text-gray-300">${data.before_text}</pre>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                        <div class="bg-accent-light/20 dark:bg-accent-dark/30 px-3 py-1 text-sm font-medium text-accent-dark dark:text-accent-light">After</div>
                        <div class="p-3 bg-accent-light/5 dark:bg-accent-dark/5">
                            <pre class="text-xs whitespace-pre-wrap text-gray-700 dark:text-gray-300">${data.after_text}</pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;
        
        recommendationsList.appendChild(card);
        
        // Scroll to the latest recommendation
        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Update filtered recommendations count
     */
    function updateFilteredRecommendations(count) {
        updateStatusMessage(`Implementing ${count} selected recommendations...`);
    }

    /**
     * Append an implementation chunk
     */
    function appendImplementationChunk(content) {
        const implementationStream = document.getElementById('implementation-stream');
        if (!implementationStream) return;
        
        // If first chunk, clear loading indicator
        if (implementationStream.innerHTML === '') {
            implementationStream.innerHTML = '<div class="typed-text"></div>';
        }
        
        const typedText = implementationStream.querySelector('.typed-text');
        if (typedText) {
            typedText.innerHTML += content;
            
            // Auto-scroll to follow content
            typedText.scrollTop = typedText.scrollHeight;
        }
    }

    /**
     * Mark implementation as complete
     */
    function markImplementationComplete(sectionsModified) {
        const implementationStream = document.getElementById('implementation-stream');
        if (implementationStream) {
            const typedText = implementationStream.querySelector('.typed-text');
            if (typedText) {
                typedText.classList.add('complete');
            }
            
            // Add modified sections list
            if (sectionsModified && sectionsModified.length > 0) {
                const sectionsInfo = document.createElement('div');
                sectionsInfo.className = 'mt-3 pt-3 border-top';
                sectionsInfo.innerHTML = `
                <h6>Sections Modified</h6>
                <div class="d-flex flex-wrap gap-2">
                    ${sectionsModified.map(section => `<span class="badge bg-info">${section}</span>`).join('')}
                </div>
                `;
                implementationStream.appendChild(sectionsInfo);
            }
        }
    }

    /**
     * Update final analytics data
     */
    function updateFinalAnalytics(data) {
        const resultsContent = document.getElementById('results-content');
        if (!resultsContent) return;
        
        let html = `
        <div class="mb-4">
            <h5>Improvement Summary</h5>
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span>Original ATS Score</span>
                <span>${data.original_score.toFixed(1)}%</span>
            </div>
            <div class="progress mb-3">
                <div class="progress-bar bg-secondary" role="progressbar" style="width: ${data.original_score}%"></div>
            </div>
            
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span>New ATS Score</span>
                <span>${data.new_score.toFixed(1)}%</span>
            </div>
            <div class="progress mb-3">
                <div class="progress-bar bg-success" role="progressbar" style="width: ${data.new_score}%"></div>
            </div>
            
            <div class="alert ${data.improvement > 0 ? 'alert-success' : 'alert-warning'}">
                <strong>${data.improvement > 0 ? 'Improvement' : 'Change'}: ${data.improvement.toFixed(1)}%</strong>
                <div class="small">${getImprovementMessage(data.improvement)}</div>
            </div>
        </div>
        `;
        
        resultsContent.innerHTML = html;
    }

    /**
     * Get appropriate message based on improvement score
     */
    function getImprovementMessage(improvement) {
        if (improvement >= 15) {
            return 'Excellent improvement! The resume is now significantly better aligned with the job requirements.';
        } else if (improvement >= 10) {
            return 'Great improvement! The resume is now much better aligned with the job requirements.';
        } else if (improvement >= 5) {
            return 'Good improvement! The resume is now better aligned with the job requirements.';
        } else if (improvement > 0) {
            return 'Some improvement detected. The resume is now slightly better aligned with the job requirements.';
        } else {
            return 'The customization maintained the overall quality of the resume.';
        }
    }

    /**
     * Update comparison data
     */
    function updateComparisonData(data) {
        const resultsContent = document.getElementById('results-content');
        if (!resultsContent) return;
        
        // Add comparison highlights 
        const comparisonSection = document.createElement('div');
        comparisonSection.className = 'mt-4';
        
        // Keywords changes
        const addedKeywords = data.added_keywords || [];
        const removedKeywords = data.removed_keywords || [];
        
        let html = `
        <h5>Keyword Changes</h5>
        <div class="row mb-4">
            <div class="col-md-6">
                <h6>Added Keywords (${addedKeywords.length})</h6>
                <div class="d-flex flex-wrap gap-1">
                    ${addedKeywords.slice(0, 15).map(kw => `<span class="badge bg-success">${kw}</span>`).join(' ')}
                    ${addedKeywords.length > 15 ? `<span class="badge bg-secondary">+${addedKeywords.length - 15} more</span>` : ''}
                </div>
            </div>
            <div class="col-md-6">
                <h6>Removed Keywords (${removedKeywords.length})</h6>
                <div class="d-flex flex-wrap gap-1">
                    ${removedKeywords.slice(0, 15).map(kw => `<span class="badge bg-warning">${kw}</span>`).join(' ')}
                    ${removedKeywords.length > 15 ? `<span class="badge bg-secondary">+${removedKeywords.length - 15} more</span>` : ''}
                </div>
            </div>
        </div>
        `;
        
        // Section improvements
        if (data.section_improvements) {
            html += `<h5>Section Improvements</h5><div class="mb-4">`;
            
            for (const [section, scores] of Object.entries(data.section_improvements)) {
                const improvement = scores.improvement || 0;
                
                html += `
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <span>${section.charAt(0).toUpperCase() + section.slice(1)}</span>
                        <span class="${improvement > 0 ? 'text-success' : improvement < 0 ? 'text-danger' : 'text-muted'}">
                            ${improvement > 0 ? '+' : ''}${improvement.toFixed(1)}%
                        </span>
                    </div>
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar bg-secondary" role="progressbar" 
                            style="width: ${scores.original.toFixed(1)}%" 
                            title="Original: ${scores.original.toFixed(1)}%"></div>
                    </div>
                    <div class="progress mt-1" style="height: 8px;">
                        <div class="progress-bar bg-success" role="progressbar" 
                            style="width: ${scores.new.toFixed(1)}%" 
                            title="New: ${scores.new.toFixed(1)}%"></div>
                    </div>
                </div>
                `;
            }
            
            html += `</div>`;
        }
        
        comparisonSection.innerHTML = html;
        resultsContent.appendChild(comparisonSection);
    }

    /**
     * Display final customization results
     */
    function displayFinalResults(data) {
        // Mark all steps as completed
        updateProgressTracker('comparison');
        document.querySelectorAll('.progress-step').forEach(step => {
            step.classList.add('completed');
            step.classList.remove('active');
        });
        
        updateStatusMessage('Resume customization complete!');
    }

    /**
     * Display save options
     */
    function displaySaveOptions(data) {
        const resultsContent = document.getElementById('results-content');
        if (!resultsContent) return;
        
        // Create form to save the customized resume
        const saveForm = document.createElement('form');
        saveForm.action = '/save_customized_resume';
        saveForm.method = 'POST';
        saveForm.className = 'mt-4 pt-3 border-top';
        
        // Add CSRF token
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        
        saveForm.innerHTML = `
        <input type="hidden" name="csrf_token" value="${csrfToken}">
        <input type="hidden" name="original_content" value="${escapeHtml(data.original_content)}">
        <input type="hidden" name="customized_content" value="${escapeHtml(data.customized_content)}">
        <input type="hidden" name="original_score" value="${data.original_score}">
        <input type="hidden" name="new_score" value="${data.new_score}">
        <input type="hidden" name="improvement" value="${data.improvement}">
        <input type="hidden" name="original_id" value="${form.elements['resume_id'].value}">
        <input type="hidden" name="job_id" value="${form.elements['job_id'].value}">
        <input type="hidden" name="customization_level" value="${form.elements['customization_level'].value}">
        <input type="hidden" name="industry" value="${form.elements['industry'] ? form.elements['industry'].value : ''}">
        <input type="hidden" name="optimization_plan" value='${JSON.stringify(data.optimization_plan)}'>
        <input type="hidden" name="comparison_data" value='${JSON.stringify(data.comparison_data)}'>
        
        <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Save and Review</h5>
            <button type="submit" class="btn btn-primary">
                Save Customized Resume
            </button>
        </div>
        <p class="text-muted small">Save your customized resume to view side-by-side comparison, download in different formats, or make further edits.</p>
        `;
        
        resultsContent.appendChild(saveForm);
    }

    /**
     * Display an error message
     */
    function displayError(message) {
        updateStatusMessage(`Error: ${message}`);
        
        const statusElement = document.querySelector('.current-status');
        if (statusElement) {
            statusElement.classList.add('text-danger');
        }
        
        // Clear all spinners
        document.querySelectorAll('.spinner-border').forEach(spinner => {
            spinner.remove();
        });
    }

    /**
     * Display a completion status when the stream ends
     */
    function displayCompletionStatus() {
        updateStatusMessage('Customization process completed, but some data may be missing.');
        
        const implementationStream = document.getElementById('implementation-stream');
        if (implementationStream) {
            const typedText = implementationStream.querySelector('.typed-text');
            if (typedText) {
                typedText.classList.add('complete');
            }
        }
    }

    /**
     * Helper function to escape HTML for inserting into attributes
     */
    function escapeHtml(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}