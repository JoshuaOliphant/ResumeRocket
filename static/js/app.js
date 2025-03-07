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

    // Handle form submission
    document.getElementById('resumeForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        console.log('Form submitted');

        try {
            const uploadType = document.querySelector('input[name="uploadType"]:checked').value;
            const jobDescriptionType = document.querySelector('input[name="jobDescriptionType"]:checked').value;
            const formData = new FormData();

            // Add resume data
            if (uploadType === 'text') {
                const resumeContent = resumeEditor.value().trim();
                if (!resumeContent) {
                    alert('Please enter your resume content');
                    return;
                }
                formData.append('resume', resumeContent);
                currentResumeContent = resumeContent;
            } else {
                const file = document.getElementById('resume_file').files[0];
                if (!file) {
                    alert('Please select a resume file');
                    return;
                }
                if (file.size > 5 * 1024 * 1024) {
                    alert('File size exceeds 5MB limit');
                    return;
                }
                formData.append('resume_file', file);
            }

            let endpoint;
            if (jobDescriptionType === 'text') {
                const jobDescription = document.getElementById('jobDescription').value.trim();
                if (!jobDescription) {
                    alert('Please enter a job description');
                    return;
                }
                formData.append('content', jobDescription);
                endpoint = '/api/job/url';  // Using URL endpoint for both cases for consistency
                formData.append('url', 'manual_entry');  // Dummy URL for text input
            } else {
                const jobUrl = document.getElementById('jobUrl').value.trim();
                if (!jobUrl) {
                    alert('Please enter a job posting URL');
                    return;
                }
                formData.append('url', jobUrl);
                endpoint = '/api/job/url';
            }

            console.log('Sending form request to:', endpoint);
            console.log('Form data has resume:', formData.has('resume'));
            console.log('Form data has resume_file:', formData.has('resume_file'));

            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Server error occurred');
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Store job description ID
            currentJobDescriptionId = data.job.id;

            // Store resume content if available
            if (data.resume_content) {
                currentResumeContent = data.resume_content;
            }

            // Show customize button
            document.getElementById('customizeResumeBtn').style.display = 'block';

            // Hide customized resume section until customization is performed
            document.getElementById('customizedResumeSection').style.display = 'none';

            // Update ATS Score
            const scoreDiv = document.getElementById('atsScore');
            const score = data.ats_score.score || 0;
            scoreDiv.style.width = `${score}%`;
            scoreDiv.textContent = `${score}%`;
            scoreDiv.className = `progress-bar ${score > 70 ? 'bg-success' : score > 40 ? 'bg-warning' : 'bg-danger'}`;

            // Update matching keywords
            const matchingKeywords = document.getElementById('matchingKeywords');
            matchingKeywords.innerHTML = (data.ats_score.matching_keywords || [])
                .map(keyword => `<span class="badge bg-success m-1">${keyword}</span>`)
                .join('') || '<span class="text-muted">No matching keywords found</span>';

            // Update missing keywords
            const missingKeywords = document.getElementById('missingKeywords');
            missingKeywords.innerHTML = (data.ats_score.missing_keywords || [])
                .map(keyword => `<span class="badge bg-danger m-1">${keyword}</span>`)
                .join('') || '<span class="text-muted">No missing keywords found</span>';

            // Update AI suggestions
            const aiSuggestions = document.getElementById('aiSuggestions');
            if (data.suggestions && data.suggestions.length > 0) {
                aiSuggestions.innerHTML = marked(data.suggestions.join('\n'));
            } else {
                aiSuggestions.innerHTML = '<li class="list-group-item bg-dark text-light">No suggestions available at this time.</li>';
            }

        } catch (error) {
            console.error('Error:', error);
            alert(error.message || 'There was an error processing your request. Please try again.');
        }
    });

    // Handle customize resume button click
    document.getElementById('customizeResumeBtn').addEventListener('click', async function() {
        console.log('Customize button clicked');
        console.log('Current job description ID:', currentJobDescriptionId);
        console.log('Current resume content length:', currentResumeContent ? currentResumeContent.length : 0);

        if (!currentJobDescriptionId || !currentResumeContent) {
            alert('Please analyze a resume first');
            return;
        }

        try {
            const response = await fetch('/api/customize-resume', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    resume_content: currentResumeContent,
                    job_description_id: currentJobDescriptionId
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Server error occurred');
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
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

        } catch (error) {
            console.error('Error:', error);
            alert(error.message || 'There was an error customizing your resume. Please try again.');
        }
    });
});