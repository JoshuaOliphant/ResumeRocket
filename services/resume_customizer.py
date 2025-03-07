import os
import logging
from anthropic import Anthropic
from .ats_analyzer import ATSAnalyzer

logger = logging.getLogger(__name__)

class ResumeCustomizer:
    def __init__(self):
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            raise ValueError('ANTHROPIC_API_KEY environment variable must be set')
        
        self.client = Anthropic(api_key=self.anthropic_key)
        # the newest Anthropic model is "claude-3-7-sonnet-20250219" which was released February 19, 2025
        self.model = "claude-3-7-sonnet-20250219"
        self.ats_analyzer = ATSAnalyzer()

    def customize_resume(self, resume_content, job_description):
        """
        Customize a resume based on a job description using AI
        """
        try:
            # Get initial ATS analysis
            ats_analysis = self.ats_analyzer.analyze(resume_content, job_description)
            
            prompt = f"""
            As an expert resume customization AI, your task is to optimize the provided resume for the specific job description.
            Follow these guidelines:

            1. Maintain the resume's professional tone and factual accuracy
            2. Align skills and experiences with job requirements
            3. Incorporate relevant keywords naturally
            4. Quantify achievements where possible
            5. Maintain the original resume's structure and sections
            6. Keep the content truthful and authentic

            Current ATS Score: {ats_analysis['score']}
            Matching Keywords: {', '.join(ats_analysis['matching_keywords'])}
            Missing Keywords: {', '.join(ats_analysis['missing_keywords'])}

            Original Resume:
            {resume_content}

            Job Description:
            {job_description}

            Please provide the optimized resume in Markdown format, maintaining professional formatting while enhancing content relevance.
            Focus on incorporating missing keywords naturally and emphasizing relevant experiences.
            Do not invent new experiences or qualifications.
            """

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            customized_content = response.content[0].text

            # Get new ATS score for the customized version
            new_ats_analysis = self.ats_analyzer.analyze(customized_content, job_description)

            return {
                'customized_content': customized_content,
                'ats_score': new_ats_analysis['score'],
                'matching_keywords': new_ats_analysis['matching_keywords'],
                'missing_keywords': new_ats_analysis['missing_keywords']
            }

        except Exception as e:
            logger.error(f"Error in resume customization: {str(e)}")
            raise Exception(f"Failed to customize resume: {str(e)}")
