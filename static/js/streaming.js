/**
 * ResumeRocket Streaming Support
 * Handles streaming responses from the Anthropic API
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check for streaming-enabled elements
    const streamElements = document.querySelectorAll('[data-stream]');
    
    streamElements.forEach(element => {
        setupStreamingElement(element);
    });
});

/**
 * Set up a streaming-enabled element
 * @param {HTMLElement} element - The element to set up for streaming
 */
function setupStreamingElement(element) {
    // Get the form that will trigger streaming
    const formId = element.getAttribute('data-stream-form');
    const form = document.getElementById(formId);
    
    if (!form) {
        console.error(`Streaming form not found: ${formId}`);
        return;
    }
    
    // Get the endpoint to use for streaming
    const endpoint = element.getAttribute('data-stream-endpoint');
    
    if (!endpoint) {
        console.error('No streaming endpoint specified');
        return;
    }
    
    // Get the container for the streaming content
    const containerId = element.getAttribute('data-stream-container');
    const container = document.getElementById(containerId);
    
    if (!container) {
        console.error(`Streaming container not found: ${containerId}`);
        return;
    }
    
    // Set up form submit handler
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        console.log('Form submitted with streaming enabled');
        console.log('Form ID:', form.id);
        console.log('Form elements:', form.elements);
        
        // Show loading indicator
        const loadingIndicator = document.querySelector('.htmx-indicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'inline-block';
        }
        
        // Clear previous content
        container.innerHTML = '';
        
        // Create a placeholder for ATS results
        const atsResultsContainer = document.createElement('div');
        atsResultsContainer.id = 'ats-results-container';
        atsResultsContainer.innerHTML = '<div class="mb-4 flex items-center text-gray-700 dark:text-gray-300"><svg class="animate-spin h-5 w-5 mr-3 text-accent-dark" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Analyzing resume...</div>';
        container.appendChild(atsResultsContainer);
        
        // Create a placeholder for streaming content
        const streamContainer = document.createElement('div');
        streamContainer.id = 'stream-container';
        streamContainer.innerHTML = '<div class="mb-6"><h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">AI Suggestions</h3><div class="stream-content"></div></div>';
        container.appendChild(streamContainer);
        
        const streamContent = streamContainer.querySelector('.stream-content');
        
        // Get form data
        const formData = new FormData(form);
        
        // Add CSRF token if not already in form
        if (!formData.get('csrf_token')) {
            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
            formData.append('csrf_token', csrfToken);
        }
        
        // Check if we need to handle the resume text differently based on form type
        if (formData.get('uploadType') === 'text') {
            // If using text input, make sure it's properly named as 'resume'
            const resumeContent = formData.get('resume');
            if (!resumeContent) {
                // For SimpleMDE editor, we need to get the content from the editor
                const editor = document.querySelector('.CodeMirror').CodeMirror;
                if (editor) {
                    formData.set('resume', editor.getValue());
                }
            }
        } else if (formData.get('uploadType') === 'file' || formData.has('resume_file')) {
            // We need to handle the file properly in the backend
            // For now, we'll just ensure the form has the right fields
        }
        
        // Ensure we have a job ID or job description/URL
        if (!formData.get('job_id')) {
            // If no job ID, we might need to extract from the job URL or text
            const jobUrl = formData.get('job_url');
            const jobDescription = formData.get('job_description');
            
            // Keep the existing fields, the backend will handle them
        }
        
        // Log form data for debugging
        console.log('Streaming to endpoint:', endpoint);
        console.log('Form data entries:');
        for (let pair of formData.entries()) {
            console.log(pair[0], (pair[1] instanceof File) ? `File: ${pair[1].name}` : pair[1]);
        }
        
        // Start the fetch request
        fetch(endpoint, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrf_token')
            }
        })
        .then(response => {
            // Check if the response is valid
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            // Get a reader from the response body stream
            const reader = response.body.getReader();
            let decoder = new TextDecoder();
            let buffer = '';
            
            // Process the stream
            function processStream({ done, value }) {
                // If we're done, hide loading indicator
                if (done) {
                    if (loadingIndicator) {
                        loadingIndicator.style.display = 'none';
                    }
                    return;
                }
                
                // Decode the current chunk and add it to our buffer
                buffer += decoder.decode(value, { stream: true });
                
                // Process complete JSON objects from the buffer
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep the last incomplete line in the buffer
                
                lines.forEach(line => {
                    if (line.trim() === '') return;
                    
                    try {
                        const data = JSON.parse(line);
                        
                        if (data.type === 'ats_results') {
                            // Store resume and job IDs
                            if (data.data.resume_id && data.data.job_id) {
                                // Update form fields if they exist
                                const resumeIdField = document.getElementById('customize-resume-id');
                                const jobIdField = document.getElementById('customize-job-id');
                                
                                if (resumeIdField) resumeIdField.value = data.data.resume_id;
                                if (jobIdField) jobIdField.value = data.data.job_id;
                                
                                // Dispatch event for other components that need these IDs
                                const event = new CustomEvent('streamingResumeProcessed', {
                                    detail: {
                                        resume_id: data.data.resume_id,
                                        job_id: data.data.job_id
                                    }
                                });
                                window.dispatchEvent(event);
                            }
                            
                            // Process ATS results
                            processATSResults(data.data, atsResultsContainer);
                        } else if (data.type === 'stream_start') {
                            // Stream started, update the UI (keeping the existing heading)
                            // We've already added the "AI Suggestions" heading when creating the streamContainer
                            // Just need to add the content area for the markdown
                            const existingContent = streamContent.innerHTML;
                            if (!existingContent.includes('markdown-content')) {
                                streamContent.innerHTML = '<div class="bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-700 p-4 mb-4"><div class="markdown-content text-gray-800 dark:text-gray-200"></div></div>';
                            }
                        } else if (data.type === 'chunk') {
                            // Append content chunk to the stream
                            const contentElement = streamContent.querySelector('.markdown-content');
                            if (contentElement) {
                                contentElement.innerHTML += data.content;
                                // Auto-scroll the whole page to follow the content
                                window.scrollTo({
                                    top: document.body.scrollHeight,
                                    behavior: 'smooth'
                                });
                            }
                        } else if (data.type === 'stream_end') {
                            // Stream ended, finalize the UI
                            if (loadingIndicator) {
                                loadingIndicator.style.display = 'none';
                            }
                            
                            // Add stream-complete class to stop cursor blinking
                            const streamContentElement = streamContent.querySelector('.card');
                            if (streamContentElement) {
                                streamContentElement.classList.add('stream-complete');
                            }
                            
                            // Add customization controls at the end of streaming
                            addCustomizationControls(atsResultsContainer);
                        }
                    } catch (e) {
                        console.error('Error parsing streaming response:', e, line);
                    }
                });
                
                // Read the next chunk
                return reader.read().then(processStream);
            }
            
            // Start processing the stream
            return reader.read().then(processStream);
        })
        .catch(error => {
            console.error('Streaming error:', error);
            
            // Try to get more detailed error info if possible
            let errorMessage = error.message;
            
            if (error.response) {
                // Try to parse the response as JSON
                error.response.text().then(text => {
                    try {
                        const errorJson = JSON.parse(text);
                        if (errorJson.error) {
                            errorMessage = errorJson.error;
                        }
                    } catch (e) {
                        errorMessage = text || error.message;
                    }
                    
                    container.innerHTML += `<div class="alert alert-danger">Error: ${errorMessage}</div>`;
                }).catch(() => {
                    container.innerHTML += `<div class="alert alert-danger">Error: ${errorMessage}</div>`;
                });
            } else {
                container.innerHTML += `<div class="alert alert-danger">Error: ${errorMessage}</div>`;
            }
            
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
        });
    });
}

/**
 * Add customization controls to the results view
 * @param {HTMLElement} container - The container with ATS results
 */
function addCustomizationControls(container) {
    // Find the placeholder for controls
    const placeholder = document.getElementById('customize-controls-placeholder');
    if (!placeholder) return;
    
    // Get the resume and job IDs from the container dataset
    const resumeId = container.dataset.resumeId;
    const jobId = container.dataset.jobId;
    
    if (!resumeId || !jobId) {
        console.error('Resume ID or Job ID not found', resumeId, jobId);
        return;
    }
    
    // Create the controls HTML
    const html = `
    <div class="mt-6 pt-6 border-t dark:border-gray-700">
        <form id="customizeForm" action="/customize-resume" method="post">
            <input type="hidden" name="csrf_token" value="${document.querySelector('meta[name="csrf-token"]').content}">
            <input type="hidden" name="resume_id" id="customize-resume-id" value="${resumeId}">
            <input type="hidden" name="job_id" id="customize-job-id" value="${jobId}">
            <input type="hidden" name="use_streaming" value="true">
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label for="customization_level" class="block text-gray-700 dark:text-gray-300 font-semibold mb-2">
                        Customization Level
                    </label>
                    <select class="w-full px-3 py-2 border rounded-md 
                                text-gray-700 bg-white dark:bg-gray-700 
                                border-gray-300 dark:border-gray-600
                                dark:text-white focus:outline-none 
                                focus:ring-2 focus:ring-accent-light" 
                            id="customization_level" name="customization_level">
                        <option value="conservative">Conservative - Minimal changes</option>
                        <option value="balanced" selected>Balanced - Default level</option>
                        <option value="extensive">Extensive - More aggressive optimization</option>
                    </select>
                    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        Choose how extensively you want your resume customized
                    </p>
                </div>
                <div>
                    <label for="industry" class="block text-gray-700 dark:text-gray-300 font-semibold mb-2">
                        Target Industry (Optional)
                    </label>
                    <select class="w-full px-3 py-2 border rounded-md 
                                text-gray-700 bg-white dark:bg-gray-700 
                                border-gray-300 dark:border-gray-600
                                dark:text-white focus:outline-none 
                                focus:ring-2 focus:ring-accent-light" 
                            id="industry" name="industry">
                        <option value="">No specific industry</option>
                        <option value="technology">Technology</option>
                        <option value="healthcare">Healthcare</option>
                        <option value="finance">Finance</option>
                        <option value="marketing">Marketing</option>
                        <option value="education">Education</option>
                        <option value="manufacturing">Manufacturing</option>
                        <option value="retail">Retail</option>
                    </select>
                    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        Selecting an industry will optimize terminology for that field
                    </p>
                </div>
            </div>
            
            <div class="flex flex-col sm:flex-row justify-between gap-3 mt-3">
                <button type="submit" id="customize-btn" 
                        class="px-5 py-2 bg-accent-dark hover:bg-opacity-90 
                              text-black font-semibold rounded-md
                              focus:outline-none focus:ring-2 focus:ring-offset-2 
                              focus:ring-accent-light transition">
                    <span class="inline-block htmx-indicator mr-2 hidden" id="customize-loading-indicator" role="status" aria-hidden="true">
                        <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    </span>
                    Customize Resume for Job
                </button>
                
                <a href="/review-recommendations/${resumeId}/${jobId}" 
                   class="px-4 py-2 border border-accent-dark text-accent-dark dark:text-accent-light
                          dark:border-accent-light hover:bg-accent-dark hover:text-black
                          font-medium rounded-md text-center transition">
                    Review Recommendations First
                </a>
            </div>
        </form>
    </div>
    `;
    
    // Add the controls to the placeholder
    placeholder.innerHTML = html;
    
    // Add event handler to the customize form
    const customizeForm = document.getElementById('customizeForm');
    if (customizeForm) {
        customizeForm.addEventListener('submit', function(e) {
            // Add the streaming flag
            const streamingField = document.createElement('input');
            streamingField.type = 'hidden';
            streamingField.name = 'use_streaming';
            streamingField.value = 'true';
            this.appendChild(streamingField);
        });
    }
    
    // Scroll to show the new controls
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth'
    });
}

/**
 * Process and render ATS analysis results
 * @param {Object} results - The ATS analysis results
 * @param {HTMLElement} container - The container element to render in
 */
function processATSResults(results, container) {
    let html = '';
    
    // Create score display
    html += `
    <div class="mb-6">
        <div class="flex justify-between items-center mb-2">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">ATS Score</h3>
            ${results.confidence ? `<span class="text-sm text-gray-500 dark:text-gray-400">(Confidence: ${results.confidence})</span>` : ''}
        </div>
        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-6 overflow-hidden">
            <div class="h-full bg-accent-dark text-center text-black font-semibold leading-6 rounded-full"
                style="width: ${results.score}%">
                ${results.score.toFixed(1)}%
            </div>
        </div>
        ${results.job_type ? `<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Detected Job Type: ${results.job_type.charAt(0).toUpperCase() + results.job_type.slice(1)}</p>` : ''}
    </div>
    `;
    
    // Add section scores if present
    if (results.section_scores) {
        html += `
        <div class="mb-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">Section Scores</h3>
            <div class="space-y-3">
        `;
        
        for (const [section, score] of Object.entries(results.section_scores)) {
            html += `
            <div>
                <div class="flex justify-between items-center mb-1">
                    <span class="text-gray-700 dark:text-gray-300">${section.charAt(0).toUpperCase() + section.slice(1)}</span>
                    <span class="text-gray-700 dark:text-gray-300">${score.toFixed(1)}%</span>
                </div>
                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden">
                    <div class="h-full bg-blue-500 dark:bg-blue-600 rounded-full"
                        style="width: ${score}%"></div>
                </div>
            </div>
            `;
        }
        
        html += '</div></div>';
    }
    
    // Add matching keywords
    html += `
    <div class="mb-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">Matching Keywords</h3>
        <div class="flex flex-wrap gap-2">
            ${results.matching_keywords.map(keyword => `
                <span class="px-2.5 py-1 text-sm bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-100 rounded-full">
                    ${keyword}
                </span>
            `).join('')}
        </div>
    </div>
    `;
    
    // Add missing keywords
    html += `
    <div class="mb-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">Missing Keywords</h3>
        <div class="flex flex-wrap gap-2">
            ${results.missing_keywords.map(keyword => `
                <span class="px-2.5 py-1 text-sm bg-accent-light dark:bg-accent-dark text-black dark:text-black rounded-full">
                    ${keyword}
                </span>
            `).join('')}
        </div>
    </div>
    `;
    
    // Add suggestions if present
    if (results.suggestions && results.suggestions.length > 0) {
        html += `
        <div class="mb-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">ATS Improvement Suggestions</h3>
            <div class="space-y-2 border dark:border-gray-700 rounded-md divide-y dark:divide-gray-700">
                ${results.suggestions.map(suggestion => `
                    <div class="p-3 bg-white dark:bg-gray-800 first:rounded-t-md last:rounded-b-md">
                        <p class="text-gray-800 dark:text-gray-200">
                            <span class="font-semibold">${suggestion.title}</span>: ${suggestion.content}
                        </p>
                    </div>
                `).join('')}
            </div>
        </div>
        `;
    }
    
    // Create a placeholder for the customize controls - they'll be added after streaming completes
    html += '<div id="customize-controls-placeholder"></div>';
    
    // Update the container content
    container.innerHTML = html;
    
    // Store the resume and job IDs for later use
    if (results.resume_id && results.job_id) {
        container.dataset.resumeId = results.resume_id;
        container.dataset.jobId = results.job_id;
    }
}