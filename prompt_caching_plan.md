# Claude API Prompt Caching Implementation Plan

## Overview

This plan outlines strategies to optimize Anthropic Claude API usage in ResumeRocket by implementing the new prompt caching feature. This implementation will significantly reduce API costs and improve response times while maintaining functionality.

## Current Implementation Assessment

ResumeRocket currently uses a local file-based caching mechanism that:
1. Generates MD5 hash keys for API requests
2. Saves responses to JSON files in a local directory
3. Retrieves cached responses for identical requests

While effective, this approach can be significantly improved using Anthropic's built-in prompt caching feature, which offers:
- 90% cost reduction for cached tokens
- Improved latency for API responses
- Server-side caching that works across instances

## Implementation Plan

### Phase 1: Setup and Configuration

1. **Update Anthropic SDK**
   - Ensure we're using the latest Anthropic Python SDK version that supports prompt caching
   - Update requirements and environment setup

2. **Configure Environment Variables**
   - Add environment variables for controlling prompt caching:
     ```
     # Enable/disable Anthropic prompt caching (defaults to true)
     USE_ANTHROPIC_CACHE=true
     
     # Maintain local caching as fallback (defaults to true)
     USE_LOCAL_CACHE=true
     
     # Prefix for cache IDs to isolate environments
     CACHE_PREFIX=prod_
     ```

3. **Create a Shared API Client Wrapper**
   - Develop a centralized `ClaudeClient` class to handle all API interactions
   - Implement proper configuration for both local and Anthropic caching
   - Include logging and metrics collection for cache hits/misses

### Phase 2: Core Services Refactoring

1. **Update ResumeCustomizer Service**

   The `ResumeCustomizer` class handles the most complex Claude interactions. Optimize its structure:

   ```python
   def _analyze_and_plan(self, resume_content, job_description, ats_analysis, level, industry=None):
       # Create system prompt
       system_prompt = """..."""
       
       # Add industry-specific guidance if provided
       if industry and industry.lower() in self.industry_guidance:
           system_prompt += f"\n\nINDUSTRY-SPECIFIC GUIDANCE ({industry.upper()}):\n"
           system_prompt += self.industry_guidance[industry.lower()]
       
       # Set intensity factor based on customization level
       # [existing intensity level code...]
       
       # Create user message with resume and job
       user_message = f"""..."""
       
       # Call Claude API with proper cache_control
       response = self.client.messages.create(
           model=self.model,
           max_tokens=8192,
           system=[
               {
                   "type": "text", 
                   "text": system_prompt,
                   "cache_control": {"type": "ephemeral"}  # Cache system prompt
               }
           ],
           messages=[
               {"role": "user", "content": user_message}
           ]
       )
       
       # Process response...
   ```

2. **Update AISuggestions Service**

   Modify the `get_suggestions` and `get_suggestions_stream` methods to use Anthropic's prompt caching:

   ```python
   def get_suggestions(self, resume_text, job_description):
       """Get AI-powered suggestions for resume improvement (non-streaming)"""
       try:
           # Create the system prompt
           system_prompt = "You are an ATS expert analyzing resumes against job descriptions..."
           
           # Create the user prompt
           user_message = self._create_suggestions_prompt(resume_text, job_description)
           
           # Call API with cache_control
           response = self.client.messages.create(
               model=self.model,
               max_tokens=8192,
               system=[
                   {
                       "type": "text", 
                       "text": system_prompt,
                       "cache_control": {"type": "ephemeral"}
                   }
               ],
               messages=[
                   {"role": "user", "content": user_message}
               ]
           )
           
           # Process and return results...
   ```

3. **Handle Streaming Responses**

   For streaming responses, implement a simulated streaming approach for cached results:

   ```python
   def get_suggestions_stream(self, resume_text, job_description):
       """Get AI-powered suggestions with streaming response"""
       try:
           # Create system prompt with cache_control
           system_prompt = "You are an ATS expert analyzing resumes against job descriptions..."
           
           # Create user message
           user_message = self._create_suggestions_prompt(resume_text, job_description)
           
           # Track whether we're using a cached response
           using_cached = False
           cache_key = self._generate_cache_key(
               model=self.model,
               system=system_prompt,
               messages=[{"role": "user", "content": user_message}],
               max_tokens=8192
           )
           
           # Check local cache first if enabled
           if self.use_local_cache:
               cached_response = self._get_from_local_cache(cache_key)
               if cached_response:
                   using_cached = True
                   # Simulate streaming from cached content
                   full_text = cached_response['content'][0]['text']
                   chunk_size = 20
                   for i in range(0, len(full_text), chunk_size):
                       yield full_text[i:i+chunk_size]
                   return
           
           # Not in local cache, stream from API
           full_response = ""
           with self.client.messages.stream(
               model=self.model,
               max_tokens=8192,
               system=[
                   {
                       "type": "text", 
                       "text": system_prompt,
                       "cache_control": {"type": "ephemeral"}
                   }
               ],
               messages=[
                   {"role": "user", "content": user_message}
               ]
           ) as stream:
               for text in stream.text_stream:
                   full_response += text
                   yield text
           
           # Save to local cache if enabled
           if self.use_local_cache and not using_cached:
               response_data = {"content": [{"text": full_response}]}
               self._save_to_local_cache(cache_key, response_data)
   ```

### Phase 3: Advanced Prompt Restructuring

1. **Reorganize Prompts for Maximum Caching Efficiency**

   Restructure prompts to separate static and dynamic content:

   ```python
   # Static system prompt that rarely changes (highly cacheable)
   static_system_prompt = """You are an expert ATS optimization consultant...
   [lengthy instructions, examples, and guidance that's the same for all requests]
   """
   
   # Dynamic parts specific to this request
   dynamic_user_content = f"""
   Please analyze this resume against the following job description and create a detailed optimization plan.
   
   RESUME:
   ```
   {resume_content}
   ```
   
   JOB DESCRIPTION:
   ```
   {job_description}
   ```
   
   CURRENT ATS ANALYSIS:
   - Current ATS Score: {ats_analysis['score']}
   - Matching Keywords: {', '.join(ats_analysis['matching_keywords'][:10])}
   - Missing Keywords: {', '.join(ats_analysis['missing_keywords'][:10])}
   
   Return your analysis as a complete, valid JSON object.
   """
   
   # API call with cache_control on the static part
   response = self.client.messages.create(
       model=self.model,
       max_tokens=8192,
       system=[
           {
               "type": "text",
               "text": static_system_prompt,
               "cache_control": {"type": "ephemeral"}
           }
       ],
       messages=[
           {"role": "user", "content": dynamic_user_content}
       ]
   )
   ```

2. **Structure Multi-Turn Conversations for Caching**

   For multi-turn conversations like resume customization, structure conversations to maximize cache hits:

   ```python
   # First turn - analysis (cacheable system prompt + specific user input)
   system_prompt = """You are an expert resume analyzer..."""
   
   user_message_1 = f"""Analyze this resume against this job description...
   
   RESUME:
   {resume_content}
   
   JOB:
   {job_description}
   """
   
   # First API call with cache_control
   response_1 = self.client.messages.create(
       model=self.model,
       system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
       messages=[{"role": "user", "content": user_message_1}]
   )
   
   # Extract analysis from response_1
   analysis = response_1.content[0].text
   
   # Second turn - implementation (cacheable system prompt + analysis + customization options)
   system_prompt_2 = """You are an expert resume customizer..."""
   
   user_message_2 = f"""Based on this analysis, customize the resume:
   
   ANALYSIS:
   {analysis}
   
   RESUME:
   {resume_content}
   
   JOB:
   {job_description}
   
   CUSTOMIZATION LEVEL: {level.upper()}
   """
   
   # Second API call with cache_control
   response_2 = self.client.messages.create(
       model=self.model,
       system=[{"type": "text", "text": system_prompt_2, "cache_control": {"type": "ephemeral"}}],
       messages=[{"role": "user", "content": user_message_2}]
   )
   ```

### Phase 4: Monitoring and Optimization

1. **Implement Cache Performance Tracking**

   Add functions to track and log cache performance:

   ```python
   def track_cache_metrics(self, response):
       """Track cache usage metrics from Claude API response"""
       try:
           # Extract cache metrics from response
           cache_creation_tokens = response.usage.get("cache_creation_input_tokens", 0)
           cache_read_tokens = response.usage.get("cache_read_input_tokens", 0)
           input_tokens = response.usage.get("input_tokens", 0)
           output_tokens = response.usage.get("output_tokens", 0)
           
           # Calculate cost savings (approximate)
           base_input_rate = 0.003  # $3/MTok for Claude 3.7 Sonnet
           cache_write_rate = 0.00375  # $3.75/MTok for Claude 3.7 Sonnet
           cache_read_rate = 0.0003  # $0.30/MTok for Claude 3.7 Sonnet
           
           # Actual cost with caching
           actual_cost = (
               (input_tokens * base_input_rate / 1000000) +
               (cache_creation_tokens * cache_write_rate / 1000000) +
               (cache_read_tokens * cache_read_rate / 1000000) +
               (output_tokens * 0.015 / 1000000)  # $15/MTok for output
           )
           
           # Cost without caching
           no_cache_cost = (
               ((input_tokens + cache_read_tokens) * base_input_rate / 1000000) +
               (output_tokens * 0.015 / 1000000)
           )
           
           # Calculate savings
           savings = no_cache_cost - actual_cost
           
           # Log metrics
           logging.info(f"Claude API call: Input={input_tokens}, Output={output_tokens}, "
                     f"CacheWrite={cache_creation_tokens}, CacheRead={cache_read_tokens}, "
                     f"Cost=${actual_cost:.4f}, Savings=${savings:.4f} ({(savings/no_cache_cost*100):.1f}%)")
           
           # Store metrics for reporting
           self._update_cache_stats(
               input_tokens, 
               output_tokens,
               cache_creation_tokens, 
               cache_read_tokens,
               actual_cost,
               savings
           )
           
       except Exception as e:
           logging.error(f"Error tracking cache metrics: {str(e)}")
   ```

2. **Implement Admin Dashboard Metrics**

   Create an admin dashboard to visualize cache performance:
   - Cache hit rate
   - Cost savings
   - Average response time
   - Common cached prompts

3. **Cache Maintenance Utils**

   ```python
   def cleanup_local_cache(max_age_days=30, max_size_mb=500):
       """Clean up old cache entries to manage disk space"""
       cache_dir = os.environ.get('PROMPT_CACHE_DIR', 'cache/prompts')
       if not os.path.exists(cache_dir):
           return
       
       # Get current time
       now = time.time()
       max_age_seconds = max_age_days * 24 * 60 * 60
       
       # Track total size
       total_size = 0
       cache_files = []
       
       # Collect files with their age and size
       for filename in os.listdir(cache_dir):
           file_path = os.path.join(cache_dir, filename)
           if not os.path.isfile(file_path) or not filename.endswith('.json'):
               continue
               
           file_age = now - os.path.getmtime(file_path)
           file_size = os.path.getsize(file_path)
           total_size += file_size
           
           cache_files.append({
               'path': file_path,
               'age': file_age,
               'size': file_size
           })
       
       # Sort by age (oldest first)
       cache_files.sort(key=lambda x: x['age'], reverse=True)
       
       # Delete old files first
       files_deleted = 0
       bytes_freed = 0
       for file in cache_files:
           if file['age'] > max_age_seconds:
               os.remove(file['path'])
               bytes_freed += file['size']
               files_deleted += 1
               total_size -= file['size']
           # Stop if we're below the size threshold
           if total_size < (max_size_mb * 1024 * 1024):
               break
       
       logging.info(f"Cache cleanup: deleted {files_deleted} files, freed {bytes_freed/1024/1024:.2f}MB")
   ```

## Example Prompt Structures

### 1. Resume Analysis Prompt

```python
def analyze_resume(self, resume_text, job_description):
    """Analyze a resume against a job description using prompt caching"""
    
    # Static instructions - ideal for caching
    system_prompt = [
        {
            "type": "text",
            "text": """You are an expert ATS consultant who analyzes resumes against job descriptions.
            Your task is to provide a detailed analysis with an ATS score, matching keywords, and
            specific improvement suggestions.
            
            Follow these guidelines:
            1. Analyze keyword matching between resume and job description
            2. Evaluate section organization and formatting
            3. Identify strengths and weaknesses
            4. Provide specific, actionable suggestions
            5. Assign an overall ATS match score from 0-100
            
            [Additional detailed instructions that don't change between requests...]
            """,
            "cache_control": {"type": "ephemeral"}  # Enable caching for this static content
        }
    ]
    
    # Dynamic content - will not be cached
    user_message = [
        {
            "type": "text",
            "text": f"""Please analyze this resume against the job description and provide detailed feedback.
            
            RESUME:
            ```
            {resume_text}
            ```
            
            JOB DESCRIPTION:
            ```
            {job_description}
            ```
            
            Please provide:
            1. An overall ATS score (0-100)
            2. List of matching keywords found
            3. List of important missing keywords
            4. Section-by-section analysis
            5. Specific improvement suggestions
            """
        }
    ]
    
    # Make API call with cache_control
    response = self.client.messages.create(
        model=self.model,
        max_tokens=8192,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    # Track cache performance
    self.track_cache_metrics(response)
    
    # Process and return response
    return {
        "analysis": response.content[0].text,
        "cache_metrics": {
            "cached_tokens": response.usage.get("cache_read_input_tokens", 0),
            "new_tokens": response.usage.get("cache_creation_input_tokens", 0)
        }
    }
```

### 2. Resume Customization Prompt

```python
def customize_resume(self, resume_text, job_description, customization_level="balanced"):
    """Customize a resume for a job using prompt caching"""
    
    # Static customization instructions - ideal for caching
    system_prompt = [
        {
            "type": "text",
            "text": """You are an expert resume writer specialized in customizing resumes for specific job descriptions.
            Your task is to optimize a resume to better match a target job while maintaining authenticity.
            
            Follow these customization principles:
            1. NEVER invent qualifications or experience not present in the original resume
            2. Focus on terminology alignment, rephrasing existing content to match job keywords
            3. Reorganize content to emphasize most relevant experience and skills
            4. Improve clarity, specificity, and impact of achievements
            5. Return the complete customized resume in the same format as the original
            
            [Detailed customization instructions that remain constant...]
            """,
            "cache_control": {"type": "ephemeral"}  # Enable caching for this static content
        }
    ]
    
    # Dynamic content - unique to this request
    user_message = [
        {
            "type": "text",
            "text": f"""Please customize this resume for the provided job description.
            
            CUSTOMIZATION LEVEL: {customization_level.upper()}
            
            ORIGINAL RESUME:
            ```
            {resume_text}
            ```
            
            TARGET JOB DESCRIPTION:
            ```
            {job_description}
            ```
            
            Please provide the complete customized resume, maintaining the same format but optimizing
            content to better match the job requirements. Focus on terminology alignment, emphasizing
            relevant experience, and improving clarity.
            """
        }
    ]
    
    # Make API call with cache_control
    response = self.client.messages.create(
        model=self.model,
        max_tokens=8192,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    # Track cache metrics
    self.track_cache_metrics(response)
    
    # Return the customized resume
    return {
        "customized_resume": response.content[0].text,
        "cache_metrics": {
            "cached_tokens": response.usage.get("cache_read_input_tokens", 0),
            "new_tokens": response.usage.get("cache_creation_input_tokens", 0)
        }
    }
```

## Expected Outcomes

1. **Cost Reduction**
   - 90% cost savings on cached tokens (system instructions, formatting guidelines, etc.)
   - Estimated overall API cost reduction: 30-50% depending on usage patterns

2. **Performance Improvements**
   - Faster response times for cached requests
   - Reduced latency for complex operations with large system prompts

3. **Consistency Benefits**
   - More consistent responses for similar inputs
   - Better quality control through standardized prompt patterns

4. **Scaling Advantages**
   - Improved performance under load
   - Better handling of concurrent requests

## Deployment Strategy

1. **Development Phase**
   - Implement changes in a development branch
   - Add comprehensive logging for cache hits/misses
   - Test with a subset of production prompts

2. **Testing Phase**
   - Run A/B tests comparing cache performance
   - Benchmark response times and costs
   - Verify response consistency

3. **Gradual Rollout**
   - Deploy to production with limited traffic
   - Monitor performance and costs
   - Scale up gradually to all traffic

4. **Continuous Optimization**
   - Regular prompt analysis for cache efficiency
   - Optimize prompt structures based on cache hit rates
   - Fine-tune system vs. user content distribution

## Monitoring and Maintenance

1. **Regular Monitoring**
   - Track cache hit/miss rates
   - Monitor cost savings and performance improvements
   - Watch for any impacts on response quality

2. **Maintenance Tasks**
   - Clean up local cache periodically
   - Update prompt structures as Claude capabilities evolve
   - Refine caching strategy based on performance data

3. **Documentation**
   - Update developer documentation with caching best practices
   - Document prompt structures optimized for caching
   - Create troubleshooting guides for cache-related issues

This plan provides a comprehensive approach to implementing Anthropic's prompt caching in ResumeRocket, with specific code examples, implementation strategies, and expected outcomes.