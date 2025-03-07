document.addEventListener('DOMContentLoaded', function() {
    // Initialize SimpleMDE
    const resumeEditor = new SimpleMDE({
        element: document.getElementById('resume'),
        spellChecker: true,
        status: true,
        placeholder: "Paste your resume in Markdown format...",
    });

    // Handle upload type toggle
    const uploadTypeRadios = document.querySelectorAll('input[name="uploadType"]');
    const textInputSection = document.getElementById('textInputSection');
    const fileInputSection = document.getElementById('fileInputSection');

    uploadTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'text') {
                textInputSection.style.display = 'block';
                fileInputSection.style.display = 'none';
            } else {
                textInputSection.style.display = 'none';
                fileInputSection.style.display = 'block';
            }
        });
    });

    // Handle form submission
    document.getElementById('resumeForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const uploadType = document.querySelector('input[name="uploadType"]:checked').value;
        const jobDescription = document.getElementById('jobDescription').value;

        // Validate inputs
        if (uploadType === 'text' && !resumeEditor.value().trim()) {
            alert('Please enter your resume content');
            return;
        } else if (uploadType === 'file' && !document.getElementById('resume_file').files[0]) {
            alert('Please select a file to upload');
            return;
        }

        if (!jobDescription.trim()) {
            alert('Please provide a job description');
            return;
        }

        // Create FormData and append appropriate data
        const formData = new FormData();
        formData.append('job_description', jobDescription);

        if (uploadType === 'text') {
            formData.append('resume', resumeEditor.value());
        } else {
            const file = document.getElementById('resume_file').files[0];
            if (file.size > 5 * 1024 * 1024) { // 5MB
                alert('File size exceeds 5MB limit');
                return;
            }
            formData.append('resume_file', file);
        }

        // Send request
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => updateUI(data))
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error processing your resume. Please try again.');
        });
    });

    function updateUI(response) {
        try {
            if (response.error) {
                alert(response.error);
                return;
            }

            // Update ATS Score
            const scoreDiv = document.getElementById('atsScore');
            const score = response.ats_score.score || 0;
            scoreDiv.style.width = `${score}%`;
            scoreDiv.textContent = `${score}%`;
            scoreDiv.className = `progress-bar ${score > 70 ? 'bg-success' : score > 40 ? 'bg-warning' : 'bg-danger'}`;

            // Update matching keywords
            const matchingKeywords = document.getElementById('matchingKeywords');
            matchingKeywords.innerHTML = (response.ats_score.matching_keywords || [])
                .map(keyword => `<span class="badge bg-success m-1">${keyword}</span>`)
                .join('') || '<span class="text-muted">No matching keywords found</span>';

            // Update missing keywords
            const missingKeywords = document.getElementById('missingKeywords');
            missingKeywords.innerHTML = (response.ats_score.missing_keywords || [])
                .map(keyword => `<span class="badge bg-danger m-1">${keyword}</span>`)
                .join('') || '<span class="text-muted">No missing keywords found</span>';

            // Update AI suggestions
            const aiSuggestions = document.getElementById('aiSuggestions');
            if (response.suggestions && response.suggestions.length > 0) {
                const suggestions = response.suggestions.map(suggestion => {
                    // Add bold styling for headings (lines starting with numbers)
                    if (/^\d+\./.test(suggestion)) {
                        return `<li class="list-group-item bg-dark text-light fw-bold">${suggestion}</li>`;
                    }
                    return `<li class="list-group-item bg-dark text-light">${suggestion}</li>`;
                });
                aiSuggestions.innerHTML = suggestions.join('');
            } else {
                aiSuggestions.innerHTML = '<li class="list-group-item bg-dark text-light">No suggestions available at this time.</li>';
            }
        } catch (error) {
            console.error('Error processing response:', error);
            alert('There was an error processing your resume. Please try again.');
        }
    }
});