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
            As an ATS expert, analyze this resume and job description to provide detailed feedback.
            Format your response with the following structure using Markdown headings:

            # Resume Analysis for [Position]

            ## Overall Assessment
            Provide a concise overview of how well the resume matches the job requirements.

            ## Specific Improvement Suggestions
            Break down key areas for improvement.

            ### 1. Content Relevance & Key Skills Alignment
            - Detail specific skills that match or need emphasis
            - Identify missing keywords and experiences
            - Suggest modifications to better align with job requirements

            ### 2. Format and Organization
            - Evaluate resume structure and readability
            - Suggest improvements to layout and organization
            - Identify any formatting issues

            ### 3. Technical Focus Areas
            - Highlight relevant technical skills and experiences
            - Suggest ways to better showcase technical capabilities
            - Identify missing technical competencies

            Resume:
            {resume_text}

            Job Description:
            {job_description}

            Provide your analysis in the exact format specified above, maintaining markdown heading hierarchy.
            """

            response = self.client.messages.create(model=self.model,
                                                   max_tokens=1000,
                                                   messages=[{
                                                       "role": "user",
                                                       "content": prompt
                                                   }])

            suggestions = response.content[0].text.split('\n')
            # Clean up and format suggestions
            suggestions = [s.strip() for s in suggestions if s.strip()]
            return suggestions

        except Exception as e:
            raise Exception(f"Failed to get AI suggestions: {str(e)}")