// Resume customization functionality
function customizeResume(resumeId, jobId) {
    // Show loading state
    const customizeBtn = document.getElementById('customize-btn');
    const originalText = customizeBtn.innerHTML;
    customizeBtn.innerHTML = 'Customizing...';
    customizeBtn.disabled = true;

    // Make API request
    fetch('/api/customize-resume', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            resume_id: resumeId,
            job_id: jobId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        // Redirect to the customized resume view
        window.location.href = `/customized-resume/${data.customized_resume.id}`;
    })
    .catch(error => {
        alert('Error customizing resume: ' + error.message);
        // Reset button state
        customizeBtn.innerHTML = originalText;
        customizeBtn.disabled = false;
    });
}
