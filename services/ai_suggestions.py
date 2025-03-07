import os
import anthropic
from anthropic import Anthropic


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

    def get_suggestions(self, resume_text, job_description):
        """
        Get AI-powered suggestions for resume improvement
        """
        try:
            prompt = f"""
            As an ATS expert, analyze this resume and job description and provide specific suggestions for improvement.
            Focus on:
            1. Content relevance
            2. Key skills alignment
            3. Specific improvements
            4. Format optimization

            Resume:
            {resume_text}

            Job Description:
            {job_description}

            Provide 3-5 specific, actionable suggestions.
            """

            response = self.client.messages.create(model=self.model,
                                                   max_tokens=500,
                                                   messages=[{
                                                       "role": "user",
                                                       "content": prompt
                                                   }])

            suggestions = response.content[0].text.split('\n')
            # Clean up and format suggestions
            suggestions = [s.strip() for s in suggestions if s.strip()]
            return suggestions[:5]  # Return top 5 suggestions

        except Exception as e:
            raise Exception(f"Failed to get AI suggestions: {str(e)}")
