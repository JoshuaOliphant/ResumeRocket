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
        // Get the current value from SimpleMDE and set it in the form
        const resumeContent = resumeEditor.value();
        const jobDescription = document.getElementById('jobDescription').value;

        // Validate inputs
        if (!resumeContent.trim() || !jobDescription.trim()) {
            alert('Please provide both resume content and job description.');
            event.preventDefault();
            return;
        }

        // Update the form data with the current SimpleMDE content
        const formData = new FormData(event.detail.elt);
        formData.set('resume', resumeContent);
        event.detail.xhr.send(formData);
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
            scoreDiv.style.width = `${response.ats_score.score}%`;
            scoreDiv.textContent = `${response.ats_score.score}%`;

            // Update matching keywords
            const matchingKeywords = document.getElementById('matchingKeywords');
            matchingKeywords.innerHTML = response.ats_score.matching_keywords
                .map(keyword => `<span class="badge bg-success">${keyword}</span>`)
                .join('');

            // Update missing keywords
            const missingKeywords = document.getElementById('missingKeywords');
            missingKeywords.innerHTML = response.ats_score.missing_keywords
                .map(keyword => `<span class="badge bg-danger">${keyword}</span>`)
                .join('');

            // Update AI suggestions
            const aiSuggestions = document.getElementById('aiSuggestions');
            aiSuggestions.innerHTML = response.suggestions
                .map(suggestion => `<li class="list-group-item bg-dark text-light">${suggestion}</li>`)
                .join('');
        } catch (error) {
            console.error('Error processing response:', error);
            alert('An error occurred while processing the response');
        }
    });
});