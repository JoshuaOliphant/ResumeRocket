import os
import hashlib
import json
import anthropic
from anthropic import Anthropic
from flask import current_app


class AISuggestions:

    def __init__(self):
        # Initialize Anthropic client
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            raise ValueError(
                'ANTHROPIC_API_KEY environment variable must be set')

        self.client = Anthropic(api_key=self.anthropic_key)
        # the newest Anthropic model is "claude-3-7-sonnet-20250219" which was released February 19, 2025
        self.model = "claude-3-7-sonnet-20250219"
        
        # Cache configuration
        self.use_cache = os.environ.get('USE_PROMPT_CACHE', 'true').lower() == 'true'
        self.cache_dir = os.environ.get('PROMPT_CACHE_DIR', 'cache/prompts')
        
        # Create cache directory if it doesn't exist
        if self.use_cache and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    def _generate_cache_key(self, model, messages, **kwargs):
        """Generate a deterministic cache key from request parameters"""
        # Create a dictionary with all relevant parameters
        cache_dict = {
            "model": model,
            "messages": messages
        }
        # Add any additional kwargs
        cache_dict.update(kwargs)
        
        # Convert to a stable JSON string
        cache_str = json.dumps(cache_dict, sort_keys=True)
        
        # Create hash
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key):
        """Attempt to retrieve a response from cache"""
        if not self.use_cache:
            return None
            
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    current_app.logger.info(f"Cache hit for {cache_key}")
                    return json.load(f)
            except Exception as e:
                current_app.logger.error(f"Error reading cache: {str(e)}")
                return None
        return None
        
    def _save_to_cache(self, cache_key, response_data):
        """Save a response to the cache"""
        if not self.use_cache:
            return
            
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(response_data, f)
                current_app.logger.info(f"Saved to cache: {cache_key}")
        except Exception as e:
            current_app.logger.error(f"Error writing to cache: {str(e)}")

    def get_suggestions(self, resume_text, job_description):
        """
        Get AI-powered suggestions for resume improvement (non-streaming)
        """
        try:
            prompt = self._create_suggestions_prompt(resume_text, job_description)
            messages = [{"role": "user", "content": prompt}]
            
            # Generate cache key
            cache_key = self._generate_cache_key(
                model=self.model,
                messages=messages,
                max_tokens=8192
            )
            
            # Try to get from cache
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                # Convert cached response to the expected format
                suggestions = cached_response['content'][0]['text'].split('\n')
                suggestions = [s.strip() for s in suggestions if s.strip()]
                return suggestions
            
            # Call API if not in cache
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8192,  # Maximum token limit for comprehensive responses
                messages=messages,
                cache_control=[{"type": "ephemeral"}]  # Proper cache_control parameter for Claude's caching
            )
            
            # Prepare response data for caching
            response_data = {
                "content": [{"text": response.content[0].text}]
            }
            
            # Save to cache
            self._save_to_cache(cache_key, response_data)
            
            suggestions = response.content[0].text.split('\n')
            # Clean up and format suggestions
            suggestions = [s.strip() for s in suggestions if s.strip()]
            return suggestions

        except Exception as e:
            current_app.logger.error(f"Error getting suggestions: {str(e)}")
            raise Exception(f"Failed to get AI suggestions: {str(e)}")
            
    def get_suggestions_stream(self, resume_text, job_description):
        """
        Get AI-powered suggestions with streaming response
        Yields chunks of text as they are received from the API
        """
        try:
            prompt = self._create_suggestions_prompt(resume_text, job_description)
            messages = [{"role": "user", "content": prompt}]
            
            # Generate cache key
            cache_key = self._generate_cache_key(
                model=self.model,
                messages=messages,
                max_tokens=8192,
                stream=True
            )
            
            # Try to get from cache
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                # For streaming, we'll yield the cached content in chunks to simulate streaming
                text = cached_response['content'][0]['text']
                # Yield text in reasonable chunks to simulate streaming
                chunk_size = 20  # characters per chunk
                for i in range(0, len(text), chunk_size):
                    yield text[i:i+chunk_size]
                return
            
            # Set up to collect the full response for caching
            full_response = ""
            
            # Create a streaming response
            with self.client.messages.stream(
                model=self.model,
                max_tokens=8192,  # Maximum token limit for comprehensive responses
                messages=messages,
                cache_control=[{"type": "ephemeral"}]  # Proper cache_control parameter for Claude's caching
            ) as stream:
                # Yield each text delta as it comes in
                for text in stream.text_stream:
                    full_response += text
                    yield text
            
            # Save the complete response to cache
            response_data = {
                "content": [{"text": full_response}]
            }
            self._save_to_cache(cache_key, response_data)
                    
        except Exception as e:
            current_app.logger.error(f"Streaming error: {str(e)}")
            yield f"\n\nError: Failed to stream suggestions: {str(e)}"
    
    def _create_suggestions_prompt(self, resume_text, job_description):
        """
        Create the prompt for suggestions
        """
        return f"""
        As an ATS expert, analyze this resume against the job description to provide detailed, actionable feedback.
        Format your response with the following structure using Markdown headings:

        # Resume Analysis for [Position]

        ## Overall Assessment
        Provide a clear overview (2-3 sentences) evaluating how well the resume matches the job requirements, highlighting strengths and areas needing improvement.

        ## Specific Improvement Suggestions

        ### 1. Content Relevance & Key Skills Alignment
        - List 3-4 specific skills/experiences from the resume that match the job requirements
        - Identify 3-4 key missing keywords or experiences from the job description
        - Provide 2-3 concrete suggestions for better aligning content with the role
        - Suggest modifications to highlight relevant achievements

        ### 2. Technical Skills Enhancement
        - Review technical skills mentioned in the resume vs. job requirements
        - Suggest specific technical areas to emphasize or add
        - Recommend ways to demonstrate technical proficiency

        ### 3. Format and Impact
        - Evaluate current resume structure and organization
        - Suggest improvements for better ATS optimization
        - Recommend ways to quantify achievements

        Resume:
        {resume_text}

        Job Description:
        {job_description}

        Provide detailed, actionable feedback for each section, maintaining the markdown heading hierarchy. 
        Ensure recommendations are specific and tailored to both the resume content and job requirements.
        """