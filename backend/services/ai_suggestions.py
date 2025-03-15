import os
from flask import current_app
from .claude_client import ClaudeClient


class AISuggestions:

    def __init__(self):
        # Initialize the centralized Claude client
        self.claude = ClaudeClient()
        self.model = self.claude.model

    def get_suggestions(self, resume_text, job_description):
        """
        Get AI-powered suggestions for resume improvement (non-streaming)
        """
        try:
            # Create the system prompt with detailed instructions
            system_prompt = """You are an expert ATS consultant specializing in resume optimization. 
            Your task is to analyze the provided resume against a job description and provide detailed, 
            actionable feedback for improving the resume's effectiveness with ATS systems and human reviewers."""
            
            # Create the content prompt
            user_message = self._create_suggestions_prompt(resume_text, job_description)
            
            # Call Claude API with prompt caching via the centralized client
            response = self.claude.create_message(
                system=system_prompt,  # Client will automatically add cache_control
                messages=[{"role": "user", "content": user_message}],
                max_tokens=8192
            )
            
            # Process response into suggestions list
            suggestions = response.content[0].text.split('\n')
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
            # Create the system prompt with detailed instructions
            system_prompt = """You are an expert ATS consultant specializing in resume optimization. 
            Your task is to analyze the provided resume against a job description and provide detailed, 
            actionable feedback for improving the resume's effectiveness with ATS systems and human reviewers."""
            
            # Create the content prompt
            user_message = self._create_suggestions_prompt(resume_text, job_description)
            
            # Create a streaming response via the centralized client
            with self.claude.client.messages.stream(
                model=self.model,
                max_tokens=8192,
                system=[
                    {
                        "type": "text", 
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"}  # Enable caching for static system prompt
                    }
                ],
                messages=[{"role": "user", "content": user_message}]
            ) as stream:
                # Yield each text delta as it comes in
                for text in stream.text_stream:
                    yield text
                    
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