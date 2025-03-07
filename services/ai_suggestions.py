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

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,  # Increased token limit for more detailed responses
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