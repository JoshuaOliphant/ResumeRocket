document.addEventListener('DOMContentLoaded', function() {
    // Initialize SimpleMDE
    const resumeEditor = new SimpleMDE({
        element: document.getElementById('resume'),
        spellChecker: true,
        status: true,
        placeholder: "Paste your resume in Markdown format...",
    });

    // Handle form submission
    document.getElementById('resumeForm').addEventListener('htmx:afterRequest', function(event) {
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
    });
});
