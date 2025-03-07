document.addEventListener('DOMContentLoaded', function() {
    // Initialize SimpleMDE
    const resumeEditor = new SimpleMDE({
        element: document.getElementById('resume'),
        spellChecker: true,
        status: true,
        placeholder: "Paste your resume in Markdown format...",
    });

    // Handle form submission
    document.getElementById('resumeForm').addEventListener('htmx:beforeRequest', function(event) {
        // Get the current value from SimpleMDE
        const resumeTextarea = document.getElementById('resume');
        resumeTextarea.value = resumeEditor.value(); // Update the textarea with SimpleMDE content

        const resumeContent = resumeTextarea.value;
        const jobDescription = document.getElementById('jobDescription').value;

        // Validate inputs
        if (!resumeContent.trim() || !jobDescription.trim()) {
            alert('Please provide both resume content and job description.');
            event.preventDefault();
            return;
        }
    });

    document.getElementById('resumeForm').addEventListener('htmx:afterRequest', function(event) {
        try {
            const response = JSON.parse(event.detail.xhr.response);

            if (response.error) {
                alert(response.error);
                return;
            }

            // Update ATS Score
            const scoreDiv = document.getElementById('atsScore');
            const score = response.ats_score.score || 0;
            scoreDiv.style.width = `${score}%`;
            scoreDiv.textContent = `${score}%`;

            // Update matching keywords
            const matchingKeywords = document.getElementById('matchingKeywords');
            matchingKeywords.innerHTML = (response.ats_score.matching_keywords || [])
                .map(keyword => `<span class="badge bg-success">${keyword}</span>`)
                .join(' ') || '<span class="text-muted">No matching keywords found</span>';

            // Update missing keywords
            const missingKeywords = document.getElementById('missingKeywords');
            missingKeywords.innerHTML = (response.ats_score.missing_keywords || [])
                .map(keyword => `<span class="badge bg-danger">${keyword}</span>`)
                .join(' ') || '<span class="text-muted">No missing keywords found</span>';

            // Update AI suggestions
            const aiSuggestions = document.getElementById('aiSuggestions');
            aiSuggestions.innerHTML = (response.suggestions || [])
                .map(suggestion => `<li class="list-group-item bg-dark text-light">${suggestion}</li>`)
                .join('');

            // If no suggestions
            if (!response.suggestions || response.suggestions.length === 0) {
                aiSuggestions.innerHTML = '<li class="list-group-item bg-dark text-light">No suggestions available at this time.</li>';
            }
        } catch (error) {
            console.error('Error processing response:', error);
            alert('There was an error processing your resume. Please try again.');
        }
    });
});