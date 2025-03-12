# Resume Customization Streaming Implementation

## Overview

This specification outlines the plan for implementing real-time streaming of the resume customization process. Currently, users must wait for the entire customization process to complete before seeing any results. By implementing a streaming approach similar to what we've done for AI suggestions, we can provide a more engaging user experience that shows the customization process in real-time.

## Current Implementation

The current resume customization process consists of these key steps:

1. **Initial Analysis**: Analyze the original resume against the job description using the ATS analyzer
2. **Planning Stage**: Generate an optimization plan with specific recommendations 
3. **Implementation Stage**: Apply the recommendations to create a customized resume
4. **Final Analysis**: Analyze the customized resume to calculate improvement score
5. **Comparison Generation**: Create a detailed comparison between original and customized versions

This process happens synchronously in a single request, and the user is redirected to a comparison view only after all steps are complete.

## Proposed Streaming Implementation

The streaming implementation will break this process into observable stages with real-time updates to the user. It will:

1. Maintain the same logical steps but expose progress and intermediate results
2. Stream partial results to the client as they become available
3. Allow users to see the customization unfold in real-time
4. Provide a more engaging experience, particularly for longer resumes or complex jobs

## Technical Approach

### 1. Backend Implementation

#### 1.1 Modified ResumeCustomizer Service

Create a streaming-enabled version of the customization process:

```python
def customize_resume_streaming(self, resume_content, job_description, customization_level=None, industry=None, selected_recommendations=None):
    """Streaming version of the resume customization process"""
    
    # Yield initial status update
    yield json.dumps({
        'type': 'status', 
        'stage': 'initialization',
        'message': 'Starting resume customization process...'
    }) + "\n"
    
    try:
        # Set customization level
        level = customization_level or self.default_level
        if level not in self.customization_levels:
            level = self.default_level
        
        # Stage 1a: Initial ATS Analysis
        yield json.dumps({
            'type': 'status', 
            'stage': 'analysis',
            'message': 'Analyzing original resume against job requirements...'
        }) + "\n"
        
        # Create ATS analyzer and run initial analysis
        original_ats_analyzer = EnhancedATSAnalyzer()
        ats_analysis = original_ats_analyzer.analyze(resume_content, job_description)
        
        # Send initial analysis results
        yield json.dumps({
            'type': 'analysis_complete', 
            'data': ats_analysis
        }) + "\n"
        
        # Stage 1b: Plan Improvements
        yield json.dumps({
            'type': 'status', 
            'stage': 'planning',
            'message': 'Generating optimization plan...'
        }) + "\n"
        
        # Generate optimization plan
        optimization_plan = self._analyze_and_plan_streaming(resume_content, job_description, ats_analysis, level, industry)
        last_chunk = None
        
        # Stream the planning process chunks
        for chunk in optimization_plan:
            if isinstance(chunk, dict):
                # This is the final result
                plan_result = chunk
                last_chunk = chunk
                yield json.dumps({
                    'type': 'planning_complete',
                    'data': {
                        'recommendation_count': len(plan_result['recommendations']),
                        'summary': plan_result['summary']
                    }
                }) + "\n"
                
                # Send each recommendation individually
                for idx, rec in enumerate(plan_result['recommendations']):
                    yield json.dumps({
                        'type': 'recommendation',
                        'id': idx,
                        'data': rec
                    }) + "\n"
            else:
                # This is a streaming text chunk
                yield json.dumps({
                    'type': 'planning_chunk',
                    'content': chunk
                }) + "\n"
        
        # Filter recommendations if needed
        if selected_recommendations and last_chunk:
            filtered_recommendations = []
            for idx, rec in enumerate(last_chunk['recommendations']):
                if str(idx) in selected_recommendations:
                    filtered_recommendations.append(rec)
            
            # Update the plan with only selected recommendations
            last_chunk['recommendations'] = filtered_recommendations
            last_chunk['summary'] = f"Implementing {len(filtered_recommendations)} of {len(last_chunk['recommendations'])} recommendations"
            
            yield json.dumps({
                'type': 'recommendations_filtered',
                'count': len(filtered_recommendations)
            }) + "\n"
        
        # Stage 2: Implement Improvements
        yield json.dumps({
            'type': 'status', 
            'stage': 'implementation',
            'message': 'Implementing optimizations...'
        }) + "\n"
        
        # Apply the improvements
        implementation_stream = self._implement_improvements_streaming(resume_content, job_description, 
                                                                last_chunk, ats_analysis, level, industry)
        customized_content = None
        
        # Stream the implementation process
        for chunk in implementation_stream:
            if isinstance(chunk, dict) and 'final_content' in chunk:
                # This is the final result with the full content
                customized_content = chunk['final_content']
                yield json.dumps({
                    'type': 'implementation_complete',
                    'sections_modified': chunk.get('sections_modified', [])
                }) + "\n"
            else:
                # This is a streaming text chunk
                yield json.dumps({
                    'type': 'implementation_chunk',
                    'content': chunk
                }) + "\n"
        
        # Stage 3: Final Analysis
        yield json.dumps({
            'type': 'status', 
            'stage': 'final_analysis',
            'message': 'Analyzing customized resume...'
        }) + "\n"
        
        # Perform final ATS analysis on the customized resume
        new_ats_analyzer = EnhancedATSAnalyzer()
        new_ats_analysis = new_ats_analyzer.analyze(customized_content, job_description)
        
        improvement = new_ats_analysis['score'] - ats_analysis['score']
        
        # Send final analysis results
        yield json.dumps({
            'type': 'final_analysis_complete',
            'data': {
                'original_score': ats_analysis['score'],
                'new_score': new_ats_analysis['score'],
                'improvement': improvement,
                'confidence': new_ats_analysis['confidence']
            }
        }) + "\n"
        
        # Generate comparison data
        yield json.dumps({
            'type': 'status', 
            'stage': 'comparison',
            'message': 'Generating detailed comparison...'
        }) + "\n"
        
        comparison_data = self._generate_detailed_comparison(resume_content, customized_content, 
                                                           ats_analysis, new_ats_analysis, 
                                                           last_chunk['recommendations'])
        
        # Send comparison results
        yield json.dumps({
            'type': 'comparison_complete',
            'data': comparison_data
        }) + "\n"
        
        # Send completed customization with full content
        yield json.dumps({
            'type': 'customization_complete',
            'data': {
                'original_content': resume_content,
                'customized_content': customized_content,
                'original_score': ats_analysis['score'],
                'new_score': new_ats_analysis['score'],
                'improvement': improvement,
                'optimization_plan': last_chunk,
                'comparison_data': comparison_data
            }
        }) + "\n"
        
    except Exception as e:
        logger.error(f"Error in streaming resume customization: {str(e)}")
        yield json.dumps({
            'type': 'error',
            'message': str(e)
        }) + "\n"
```

#### 1.2 Streaming Analysis and Planning Method

```python
def _analyze_and_plan_streaming(self, resume_content, job_description, ats_analysis, level, industry=None):
    """Streaming version of the resume analysis and planning stage"""
    try:
        # Prepare industry-specific context if applicable
        industry_context = ""
        if industry and industry in self.industry_contexts:
            industry_context = self.industry_contexts[industry]
        
        # Create system prompt for analysis and planning
        system_prompt = f"""
        You are ResumeOptimizer, an expert ATS (Applicant Tracking System) resume analyst and optimizer. Your task is to analyze a resume against a job description and create a detailed optimization plan.
        
        The customization level is set to: {level.upper()}
        
        {industry_context}
        
        Follow these guidelines:
        1. Analyze how well the resume matches the job requirements
        2. Identify specific areas for improvement
        3. Generate actionable, specific recommendations
        4. Maintain the candidate's authentic experience and skills
        5. Focus on content alignment and ATS optimization
        6. Preserve the resume's overall structure and format
        
        Create an optimization plan with the following structure:
        1. A summary of the resume's current alignment with the job
        2. A job requirements analysis highlighting key skills, experiences, and qualifications
        3. A list of specific, actionable recommendations with:
           - Clear before/after examples
           - Rationale for each change
           - Implementation instructions
           - ATS impact explanation
        """
        
        # User prompt combining resume and job description
        user_prompt = f"""
        ## Resume Content
        ```
        {resume_content}
        ```
        
        ## Job Description
        ```
        {job_description}
        ```
        
        ## Current ATS Analysis
        - Overall Score: {ats_analysis['score']}
        - Matching Keywords: {', '.join(ats_analysis['matching_keywords'][:10])}
        - Missing Keywords: {', '.join(ats_analysis['missing_keywords'][:10])}
        
        Please analyze this resume against the job description and create a detailed optimization plan.
        """
        
        # Stream the response from Claude
        with self.client.messages.stream(
            model=self.model,
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        ) as stream:
            # Process the streaming text
            response_text = ""
            for text in stream.text_stream:
                # Yield each text chunk
                yield text
                response_text += text
        
        # Process the completed response
        # Parse the recommendations from the response
        recommendations = self._extract_recommendations_from_text(response_text)
        
        # Extract the summary from the response
        summary = self._extract_summary_from_text(response_text)
        
        # Extract job analysis
        job_analysis = self._extract_job_analysis_from_text(response_text)
        
        # Return the complete plan
        plan_result = {
            'recommendations': recommendations,
            'summary': summary,
            'job_analysis': job_analysis,
            'raw_analysis': response_text
        }
        
        yield plan_result
        
    except Exception as e:
        logger.error(f"Error in streaming analysis and planning: {str(e)}")
        yield f"Error in analysis: {str(e)}"
        yield {"error": str(e)}
```

#### 1.3 Streaming Implementation Method

```python
def _implement_improvements_streaming(self, resume_content, job_description, optimization_plan, ats_analysis, level, industry=None):
    """Streaming version of implementing the recommended improvements"""
    try:
        # Prepare recommendations text
        recommendations_text = ""
        for idx, rec in enumerate(optimization_plan['recommendations']):
            recommendations_text += f"\nRecommendation {idx+1}: {rec['title']}\n"
            recommendations_text += f"- Before: {rec['before']}\n"
            recommendations_text += f"- After: {rec['after']}\n"
            recommendations_text += f"- Rationale: {rec['rationale']}\n"
            
        # Create system prompt for implementation
        system_prompt = f"""
        You are ResumeCustomizer, an expert at optimizing resumes for ATS systems. Your task is to implement specific recommendations to improve a resume.
        
        The customization level is: {level.upper()}
        
        Follow these guidelines:
        1. Implement ONLY the provided recommendations
        2. Maintain the resume's original format and structure
        3. Preserve the candidate's authentic experience and qualifications
        4. Make targeted, precise changes as specified in the recommendations
        5. Ensure all modifications align with the job requirements
        6. Avoid introducing errors or inconsistencies
        
        Return the complete, modified resume content. Do not omit any sections.
        """
        
        # User prompt with resume and recommendations
        user_prompt = f"""
        ## Original Resume
        ```
        {resume_content}
        ```
        
        ## Job Description
        ```
        {job_description}
        ```
        
        ## Recommendations to Implement
        {recommendations_text}
        
        ## Analysis Summary
        {optimization_plan['summary']}
        
        Please implement these specific recommendations and return the complete, optimized resume.
        """
        
        # Stream the response from Claude
        with self.client.messages.stream(
            model=self.model,
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        ) as stream:
            # Process the streaming text
            response_text = ""
            for text in stream.text_stream:
                # Yield each text chunk
                yield text
                response_text += text
        
        # Process the completed response
        # Extract the complete resume content
        customized_content = self._extract_resume_content(response_text)
        
        # Identify modified sections
        modified_sections = self._identify_modified_sections(resume_content, customized_content)
        
        # Return the final result
        yield {
            'final_content': customized_content,
            'sections_modified': modified_sections
        }
        
    except Exception as e:
        logger.error(f"Error in streaming implementation: {str(e)}")
        yield f"Error in implementation: {str(e)}"
        yield {"error": str(e)}
```

#### 1.4 New API Endpoint

```python
@resume_bp.route('/api/customize_resume_streaming', methods=['POST'])
@login_required
def customize_resume_streaming():
    """Streaming resume customization endpoint"""
    # Get form data
    resume_id = request.form.get('resume_id')
    job_id = request.form.get('job_id')
    customization_level = request.form.get('customization_level', 'balanced')
    industry = request.form.get('industry')
    selected_recommendations = request.form.getlist('selected_recommendations')
    
    # Validate inputs
    try:
        resume_id = int(resume_id) if resume_id else None
        job_id = int(job_id) if job_id else None
    except ValueError:
        return jsonify({'error': 'Invalid resume or job ID'}), 400
    
    if not resume_id or not job_id:
        return jsonify({'error': 'Missing resume or job information'}), 400
    
    # Load resume from database
    original_resume = CustomizedResume.query.get(resume_id)
    if not original_resume:
        return jsonify({'error': 'Resume not found'}), 404
    
    # Check permissions
    if original_resume.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'You do not have permission to customize this resume'}), 403
    
    # Load job description
    job = JobDescription.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job description not found'}), 404
    
    # Get original content
    resume_content = original_resume.original_content
    file_format = original_resume.file_format
    
    # Define the streaming generator function
    def generate():
        # First generate a unique ID for this customization session
        session_id = str(uuid.uuid4())
        yield json.dumps({
            'type': 'session_start',
            'session_id': session_id
        }) + "\n"
        
        # Stream the customization process
        for chunk in resume_customizer.customize_resume_streaming(
            resume_content,
            job.content,
            customization_level=customization_level,
            industry=industry,
            selected_recommendations=selected_recommendations
        ):
            yield chunk
            
        # When customization is complete, the final chunk will have been sent
        # We can also create the resume object in the database
        try:
            # Check if we received a full customization result
            # This would be handled by a client-side callback after receiving
            # the 'customization_complete' event
            pass
            
        except Exception as e:
            logger.error(f"Error saving customized resume: {str(e)}")
            yield json.dumps({
                'type': 'error',
                'message': f"Error saving resume: {str(e)}"
            }) + "\n"
    
    # Return streaming response
    return Response(stream_with_context(generate()),
                    content_type='application/json; charset=utf-8')
```

### 2. Frontend Implementation

#### 2.1 Streaming UI Components

Create dedicated UI components to display the streaming process:

1. **Progress Tracker**: Show which stage of the process is active
2. **Dynamic Content Areas**: Update in real-time with streaming content
3. **Recommendation Collector**: Build up the list of recommendations as they arrive
4. **Analysis Dashboard**: Update with metrics as they become available

#### 2.2 JavaScript Handler for Streaming

```javascript
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
    progressSection.className = 'progress-section mb-4';
    progressSection.innerHTML = `
        <h5>Customization Progress</h5>
        <div class="progress-tracker">
            <div class="progress-step" data-stage="initialization">1. Initialization</div>
            <div class="progress-step" data-stage="analysis">2. Analysis</div>
            <div class="progress-step" data-stage="planning">3. Planning</div>
            <div class="progress-step" data-stage="implementation">4. Implementation</div>
            <div class="progress-step" data-stage="final_analysis">5. Final Analysis</div>
            <div class="progress-step" data-stage="comparison">6. Comparison</div>
        </div>
        <div class="current-status mt-2">Starting customization process...</div>
    `;
    
    const analyticsSection = document.createElement('div');
    analyticsSection.className = 'analytics-section mb-4';
    analyticsSection.innerHTML = `
        <h5>Resume Analysis</h5>
        <div class="card bg-dark border-secondary p-3">
            <div id="analytics-content">
                <div class="d-flex justify-content-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    const recommendationsSection = document.createElement('div');
    recommendationsSection.className = 'recommendations-section mb-4';
    recommendationsSection.innerHTML = `
        <h5>Optimization Recommendations</h5>
        <div class="card bg-dark border-secondary p-3">
            <div id="planning-stream" class="planning-content mb-3 streaming-content"></div>
            <div id="recommendations-list" class="recommendations-list"></div>
        </div>
    `;
    
    const implementationSection = document.createElement('div');
    implementationSection.className = 'implementation-section mb-4';
    implementationSection.innerHTML = `
        <h5>Implementation</h5>
        <div class="card bg-dark border-secondary p-3">
            <div id="implementation-stream" class="implementation-content streaming-content"></div>
        </div>
    `;
    
    const resultsSection = document.createElement('div');
    resultsSection.className = 'results-section mb-4';
    resultsSection.innerHTML = `
        <h5>Final Results</h5>
        <div class="card bg-dark border-secondary p-3">
            <div id="results-content">
                <div class="text-center py-3">
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
        
        // Get form data
        const formData = new FormData(form);
        
        // Start fetch request
        fetch('/api/customize_resume_streaming', {
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
                // Save to database and show next steps
                saveCustomizedResume(data.data);
                break;
                
            case 'error':
                displayError(data.message);
                break;
        }
    }
    
    // Helper functions for updating the UI...
    // (implementation of updateProgressTracker, updateStatusMessage, etc.)
}

/**
 * Save the customized resume to the database
 */
function saveCustomizedResume(data) {
    // Create a form to submit the data
    const saveForm = document.createElement('form');
    saveForm.method = 'POST';
    saveForm.action = '/save_customized_resume';
    
    // Add CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrf_token';
    csrfInput.value = csrfToken;
    saveForm.appendChild(csrfInput);
    
    // Add the data
    for (const [key, value] of Object.entries(data)) {
        if (typeof value === 'object') {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = JSON.stringify(value);
            saveForm.appendChild(input);
        } else {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = value;
            saveForm.appendChild(input);
        }
    }
    
    // Submit the form
    document.body.appendChild(saveForm);
    saveForm.submit();
}
```

### 3. Database and Saving Changes

To properly save the customized resume after streaming, we'll need an additional endpoint:

```python
@resume_bp.route('/save_customized_resume', methods=['POST'])
@login_required
def save_customized_resume():
    """Save a customized resume after streaming completion"""
    # Get data from form
    original_content = request.form.get('original_content')
    customized_content = request.form.get('customized_content')
    original_score = float(request.form.get('original_score', 0))
    new_score = float(request.form.get('new_score', 0))
    improvement = float(request.form.get('improvement', 0))
    resume_id = request.form.get('original_id')
    job_id = request.form.get('job_id')
    customization_level = request.form.get('customization_level', 'balanced')
    industry = request.form.get('industry')
    
    # Parse JSON data
    try:
        optimization_plan = json.loads(request.form.get('optimization_plan', '{}'))
        comparison_data = json.loads(request.form.get('comparison_data', '{}'))
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    # Validate inputs
    try:
        resume_id = int(resume_id) if resume_id else None
        job_id = int(job_id) if job_id else None
    except ValueError:
        return jsonify({'error': 'Invalid resume or job ID'}), 400
    
    if not resume_id or not job_id:
        return jsonify({'error': 'Missing resume or job information'}), 400
    
    # Load original resume
    original_resume = CustomizedResume.query.get(resume_id)
    if not original_resume:
        return jsonify({'error': 'Original resume not found'}), 404
    
    # Check permissions
    if original_resume.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'You do not have permission to save this resume'}), 403
    
    # Load job
    job = JobDescription.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job description not found'}), 404
    
    # Create new customized resume
    new_customized_resume = CustomizedResume(
        original_id=resume_id,
        job_description_id=job_id,
        user_id=current_user.id,
        title=f"{original_resume.title} (Customized for {job.title})",
        original_content=original_content,
        customized_content=customized_content,
        file_format=original_resume.file_format,
        ats_score=new_score,
        original_ats_score=original_score,
        improvement=improvement,
        confidence=0.8,  # Default confidence value
        customization_level=customization_level,
        industry=industry,
        optimization_data=json.dumps(optimization_plan),
        comparison_data=json.dumps(comparison_data)
    )
    
    # Save to database
    db.session.add(new_customized_resume)
    db.session.commit()
    
    # Redirect to comparison view
    return redirect(url_for('resume.compare_resume', resume_id=new_customized_resume.id))
```

## User Interface

### Progress Tracking

The streaming interface will show clear progress through each stage of the customization process:

1. **Progress Bar**: Visual indication of completion percentage
2. **Stage Indicators**: Highlight the current active stage
3. **Status Messages**: Text updates on what's happening

### Real-time Streaming Content

For planning and implementation stages, users will see:

1. **Live Text Generation**: Claude's thought process as it analyzes and plans
2. **Recommendation Cards**: Each recommendation appearing as it's generated
3. **Dynamic Updates**: Analytics and scores updating in real-time

### Completion Actions

When customization is complete:

1. **Review Controls**: Options to review, download, or share the customized resume
2. **Comparison Preview**: Quick before/after view of key changes
3. **Save Confirmation**: Notification that the resume has been saved

## Prompts

### Analysis and Planning Prompt

```
You are ResumeOptimizer, an expert ATS (Applicant Tracking System) resume analyst and optimizer. Your task is to analyze a resume against a job description and create a detailed optimization plan.

The customization level is set to: {LEVEL}

{INDUSTRY_CONTEXT}

Follow these guidelines:
1. Analyze how well the resume matches the job requirements
2. Identify specific areas for improvement
3. Generate actionable, specific recommendations
4. Maintain the candidate's authentic experience and skills
5. Focus on content alignment and ATS optimization
6. Preserve the resume's overall structure and format

Create an optimization plan with the following structure:
1. A summary of the resume's current alignment with the job
2. A job requirements analysis highlighting key skills, experiences, and qualifications
3. A list of specific, actionable recommendations with:
   - Clear before/after examples
   - Rationale for each change
   - Implementation instructions
   - ATS impact explanation
```

### Implementation Prompt

```
You are ResumeCustomizer, an expert at optimizing resumes for ATS systems. Your task is to implement specific recommendations to improve a resume.

The customization level is: {LEVEL}

Follow these guidelines:
1. Implement ONLY the provided recommendations
2. Maintain the resume's original format and structure
3. Preserve the candidate's authentic experience and qualifications
4. Make targeted, precise changes as specified in the recommendations
5. Ensure all modifications align with the job requirements
6. Avoid introducing errors or inconsistencies

Return the complete, modified resume content. Do not omit any sections.
```

## Next Steps

To implement this streaming approach:

1. Update ResumeCustomizer to support streaming for each stage
2. Create the new API endpoint for streaming customization
3. Implement the client-side JavaScript to handle the streaming responses
4. Design and build the streaming UI components
5. Add the save functionality to persist the customized resume

The changes should be tested with various resume formats and job descriptions to ensure the streaming works reliably across different scenarios.