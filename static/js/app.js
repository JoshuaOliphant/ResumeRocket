document.addEventListener('DOMContentLoaded', function() {
    // Initialize SimpleMDE
    const resumeEditor = new SimpleMDE({
        element: document.getElementById('resume'),
        spellChecker: true,
        status: true,
        placeholder: "Paste your resume in Markdown format...",
    });

    let currentJobDescriptionId = null;
    let currentResumeContent = null;

    // Handle resume upload type toggle
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

    // Handle job description type toggle
    const jobDescriptionTypeRadios = document.querySelectorAll('input[name="jobDescriptionType"]');
    const jobTextSection = document.getElementById('jobTextSection');
    const jobUrlSection = document.getElementById('jobUrlSection');

    jobDescriptionTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'text') {
                jobTextSection.style.display = 'block';
                jobUrlSection.style.display = 'none';
            } else {
                jobTextSection.style.display = 'none';
                jobUrlSection.style.display = 'block';
            }
        });
    });

    // Handle customize resume button click
    document.getElementById('customizeResumeBtn').addEventListener('click', function() {
        console.log('Customize button clicked');
        console.log('Current job description ID:', currentJobDescriptionId);
        console.log('Current resume content length:', currentResumeContent ? currentResumeContent.length : 0);

        if (!currentJobDescriptionId || !currentResumeContent) {
            alert('Please analyze a resume first');
            return;
        }

        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resume_content: currentResumeContent,
                job_description_id: currentJobDescriptionId
            })
        };

        fetch('/api/customize-resume', options)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errorData => {
                        throw new Error(errorData.error || 'Server error occurred');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                // Show customized resume section
                const customizedSection = document.getElementById('customizedResumeSection');
                customizedSection.style.display = 'block';

                // Update content
                const contentDiv = document.getElementById('customizedResumeContent');
                contentDiv.innerHTML = marked(data.customized_resume.customized_content);

                // Update score improvement
                const improvement = data.improvement.toFixed(1);
                document.getElementById('scoreImprovement').textContent = `+${improvement}%`;

                // Highlight the improvement in green if positive
                const improvementSpan = document.getElementById('scoreImprovement');
                improvementSpan.className = improvement > 0 ? 'text-success' : 'text-warning';
            })
            .catch(error => {
                console.error('Error:', error);
                alert(error.message || 'There was an error customizing your resume. Please try again.');
            });
    });

    // Handle form submission
    document.getElementById('resumeForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const uploadType = document.querySelector('input[name="uploadType"]:checked').value;
        const jobDescriptionType = document.querySelector('input[name="jobDescriptionType"]:checked').value;

        // Create FormData for both text and file submissions
        const formData = new FormData();

        // Add resume data
        if (uploadType === 'text') {
            const resumeContent = resumeEditor.value().trim();
            console.log('Resume content length:', resumeContent.length);
            formData.append('resume', resumeContent);
            currentResumeContent = resumeContent;
        } else {
            const file = document.getElementById('resume_file').files[0];
            if (file.size > 5 * 1024 * 1024) { // 5MB
                alert('File size exceeds 5MB limit');
                return;
            }
            formData.append('resume_file', file);
        }

        // Add job description data
        if (jobDescriptionType === 'text') {
            formData.append('job_description', document.getElementById('jobDescription').value.trim());
            sendRequest('/api/job/text', formData);
        } else {
            const jobUrl = document.getElementById('jobUrl').value.trim();
            formData.append('url', jobUrl);
            sendRequest('/api/job/url', formData);
        }
    });

    function sendRequest(endpoint, formData) {
        console.log('Sending request to:', endpoint);
        console.log('Form data has resume:', formData.has('resume'));
        console.log('Form data has resume_file:', formData.has('resume_file'));

        const options = {
            method: 'POST',
            body: formData
        };

        fetch(endpoint, options)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errorData => {
                        throw new Error(errorData.error || 'Server error occurred');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                // Store current job description ID
                currentJobDescriptionId = data.job.id;

                // If file was uploaded, store the parsed content
                if (formData.has('resume_file')) {
                    currentResumeContent = data.resume_content;
                }

                updateUI(data);
            })
            .catch(error => {
                console.error('Error:', error);
                alert(error.message || 'There was an error processing your request. Please try again.');
            });
    }

    function updateUI(response) {
        try {
            if (response.error) {
                alert(response.error);
                return;
            }

            // Show customize button
            document.getElementById('customizeResumeBtn').style.display = 'block';

            // Hide customized resume section until customization is performed
            document.getElementById('customizedResumeSection').style.display = 'none';

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
                aiSuggestions.innerHTML = marked(response.suggestions.join('\n'));
            } else {
                aiSuggestions.innerHTML = '<li class="list-group-item bg-dark text-light">No suggestions available at this time.</li>';
            }

        } catch (error) {
            console.error('Error processing response:', error);
            alert('There was an error processing your request. Please try again.');
        }
    }
});