import os
import logging
from anthropic import Anthropic
from services.ats_analyzer import ATSAnalyzer
from services.ai_suggestions import AISuggestions

logger = logging.getLogger(__name__)

class ResumeCustomizer:
    def __init__(self):
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            raise ValueError('ANTHROPIC_API_KEY environment variable must be set')

        self.client = Anthropic(api_key=self.anthropic_key)
        # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        self.model = "claude-3-5-sonnet-20241022"
        self.ats_analyzer = ATSAnalyzer()
        self.ai_suggestions = AISuggestions()

    def customize_resume(self, resume_content, job_description):
        """
        Customize a resume based on a job description using AI analysis
        """
        try:
            # Get ATS analysis and suggestions first
            ats_score = self.ats_analyzer.analyze(resume_content, job_description)
            suggestions = self.ai_suggestions.get_suggestions(resume_content, job_description)

            # Construct the prompt for resume customization
            prompt = f"""
            As an expert resume customization AI, optimize this resume for the provided job description.
            Use the ATS analysis and suggestions provided to make specific improvements.

            Current ATS Score: {ats_score['score']}%
            Matching Keywords: {', '.join(ats_score['matching_keywords'])}
            Missing Keywords: {', '.join(ats_score['missing_keywords'])}

            AI Suggestions:
            {chr(10).join(suggestions)}

            Guidelines for customization:
            1. Maintain the candidate's actual experience and qualifications
            2. Reorganize and rephrase content to better match job requirements
            3. Add relevant keywords naturally where appropriate
            4. Improve clarity and impact of achievements
            5. Keep the formatting in Markdown
            6. Ensure all modifications are truthful and ethical

            Original Resume:
            {resume_content}

            Job Description:
            {job_description}

            Please provide the customized resume in Markdown format, maintaining appropriate sections and structure.
            Focus on highlighting relevant experience and incorporating missing keywords naturally.
            """

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            customized_content = response.content[0].text.strip()
            
            # Get new ATS score for the customized version
            new_ats_score = self.ats_analyzer.analyze(customized_content, job_description)

            return {
                'customized_content': customized_content,
                'original_ats_score': ats_score['score'],
                'new_ats_score': new_ats_score['score'],
                'improvement': new_ats_score['score'] - ats_score['score']
            }

        except Exception as e:
            logger.error(f"Error customizing resume: {str(e)}")
            raise Exception(f"Failed to customize resume: {str(e)}")
