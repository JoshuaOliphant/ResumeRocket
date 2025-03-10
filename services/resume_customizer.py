import os
import logging
import json
import re
from anthropic import Anthropic
from .ats_analyzer import EnhancedATSAnalyzer

logger = logging.getLogger(__name__)

class ResumeCustomizer:
    def __init__(self):
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            raise ValueError('ANTHROPIC_API_KEY environment variable must be set')
        
        self.client = Anthropic(api_key=self.anthropic_key)
        # the newest Anthropic model is "claude-3-7-sonnet-20250219" which was released February 19, 2025
        self.model = "claude-3-7-sonnet-20250219"
        self.ats_analyzer = EnhancedATSAnalyzer()
        
        # Customization parameters
        self.customization_levels = {
            "conservative": 0.7,  # Minimal changes, focus on essential alignment
            "balanced": 1.0,      # Default level - reasonable optimization
            "extensive": 1.3      # More aggressive optimization
        }
        self.default_level = "balanced"

    def customize_resume(self, resume_content, job_description, customization_level=None):
        """
        Two-stage resume customization process:
        1. Analysis stage: Analyze resume vs job description and plan improvements
        2. Optimization stage: Implement planned improvements
        """
        try:
            # Set customization level
            level = customization_level or self.default_level
            if level not in self.customization_levels:
                level = self.default_level
            
            # Create a separate ATS analyzer instance for the original resume to avoid shared state
            original_ats_analyzer = EnhancedATSAnalyzer()
            ats_analysis = original_ats_analyzer.analyze(resume_content, job_description)
            logger.info(f"Initial ATS score: {ats_analysis['score']}, confidence: {ats_analysis['confidence']}")
            
            # Stage 1: Analysis - Plan improvements
            optimization_plan = self._analyze_and_plan(resume_content, job_description, ats_analysis, level)
            logger.info(f"Generated optimization plan with {len(optimization_plan['recommendations'])} recommendations")
            
            # Stage 2: Implement improvements
            customized_content = self._implement_improvements(resume_content, job_description, optimization_plan, ats_analysis, level)
            
            # Create a separate ATS analyzer instance for the customized resume to avoid shared state
            new_ats_analyzer = EnhancedATSAnalyzer()
            new_ats_analysis = new_ats_analyzer.analyze(customized_content, job_description)
            logger.info(f"New ATS score: {new_ats_analysis['score']} (improved by {new_ats_analysis['score'] - ats_analysis['score']:.2f} points)")
            
            # Generate detailed comparison data
            comparison_data = self._generate_detailed_comparison(
                ats_analysis, 
                new_ats_analysis,
                optimization_plan
            )
            
            # Prepare comprehensive result
            return {
                'customized_content': customized_content,
                'original_score': ats_analysis['score'],
                'new_score': new_ats_analysis['score'],
                'improvement': new_ats_analysis['score'] - ats_analysis['score'],
                'confidence': new_ats_analysis['confidence'],
                'matching_keywords': new_ats_analysis['matching_keywords'],
                'missing_keywords': new_ats_analysis['missing_keywords'],
                'section_scores': new_ats_analysis['section_scores'],
                'job_type': new_ats_analysis['job_type'],
                'suggestions': new_ats_analysis['suggestions'],
                'optimization_plan': optimization_plan,
                'customization_level': level,
                'comparison_data': comparison_data
            }

        except Exception as e:
            logger.error(f"Error in resume customization: {str(e)}")
            raise Exception(f"Failed to customize resume: {str(e)}")
    
    def _analyze_and_plan(self, resume_content, job_description, ats_analysis, level):
        """
        Stage 1: Analyze resume against job description and create optimization plan
        """
        try:
            # Create system prompt for the analysis phase
            system_prompt = """You are an expert ATS optimization consultant specializing in resume customization. 
            Your task is to analyze a resume against a job description and create a detailed improvement plan that will 
            maximize the resume's success with Applicant Tracking Systems while maintaining authenticity.
            
            Create a specific, actionable plan identifying exactly what changes should be made and why. Focus on:
            1. Identify keywords and phrases in the job description that match ACTUAL experience in the resume but use different terminology
            2. Analyze existing content that should be repositioned or emphasized based on job priorities
            3. Look for synonyms or related terms where the candidate's experience matches the job requirements but uses different wording
            4. Identify sections that need improvement or rewriting to better highlight relevant experience
            5. Suggest phrase replacements that align with the job description while remaining truthful
            6. Find opportunities to reorganize content to prioritize most relevant experience
            
            CRITICAL AUTHENTICITY GUIDELINES:
            - Never suggest adding skills or experiences that aren't evidenced in the original resume
            - Only suggest changes that maintain the truthfulness of the candidate's experience
            - For each keyword in the job description, carefully examine if equivalent experience exists in the resume
            - If a key job requirement is missing from the resume, note it but do NOT suggest falsely adding it
            
            Do not implement the changes yet - create a clear, organized plan of what should be changed.
            Your output must be formatted as valid JSON with these sections:
            - summary: Brief overview of the resume-job match and key improvement areas
            - job_analysis: Key insights about the job requirements and priorities
            - recommendations: Array of specific changes to make (including the section to modify, what to change, and why)
            - keywords_to_add: List of missing keywords to incorporate ONLY IF they match existing experience
            - equivalent_terms: Map of job description terms to equivalent terms found in the resume
            - formatting_suggestions: Any structural improvements needed
            
            Be precise, practical, and focused on meaningful improvements that will genuinely improve the match while maintaining complete honesty.
            """
            
            # Extract section scores and prepare them for the prompt
            section_analysis = ""
            for section, score in ats_analysis.get('section_scores', {}).items():
                section_analysis += f"- {section.title()}: {score}/100\n"
            
            # Format suggestions
            suggestions_text = ""
            for suggestion in ats_analysis.get('suggestions', []):
                suggestions_text += f"- {suggestion.get('title')}: {suggestion.get('content')}\n"
            
            # Create user message with resume and job details
            user_message = f"""
            I need a plan to optimize this resume for the provided job description.
            
            Current ATS Analysis:
            - Overall Score: {ats_analysis.get('score')}/100
            - Confidence: {ats_analysis.get('confidence')}
            - Job Type: {ats_analysis.get('job_type', 'General')}
            - Keyword Density: {ats_analysis.get('keyword_density', 0):.2f}%
            
            Section Scores:
            {section_analysis}
            
            Matching Keywords: {', '.join(ats_analysis.get('matching_keywords', [])[:10])}
            
            Missing Keywords: {', '.join(ats_analysis.get('missing_keywords', [])[:10])}
            
            ATS Suggestions:
            {suggestions_text}
            
            Customization Level: {level.title()}
            
            Original Resume:
            {resume_content}
            
            Job Description:
            {job_description}
            
            Please provide a detailed optimization plan as structured JSON that I can use to implement the improvements.
            """
            
            # Call Claude for analysis
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2500,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_message
                }]
            )
            
            analysis_text = response.content[0].text
            
            # Extract JSON from response
            try:
                # Find JSON block in the response
                json_match = re.search(r'```json\s*(.*?)\s*```', analysis_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find anything that looks like JSON
                    json_str = analysis_text
                
                # Parse the JSON
                optimization_plan = json.loads(json_str)
                return optimization_plan
            except Exception as json_error:
                logger.error(f"Error parsing optimization plan JSON: {str(json_error)}")
                # Fallback to returning the raw text
                return {
                    "summary": "Error parsing optimization plan",
                    "raw_response": analysis_text,
                    "recommendations": [],
                    "keywords_to_add": ats_analysis.get('missing_keywords', [])[:10],
                    "equivalent_terms": {},
                    "formatting_suggestions": []
                }
                
        except Exception as e:
            logger.error(f"Error in resume analysis stage: {str(e)}")
            raise Exception(f"Failed to analyze resume: {str(e)}")
    
    def _implement_improvements(self, resume_content, job_description, optimization_plan, ats_analysis, level):
        """
        Stage 2: Implement the optimization plan to create an improved resume
        """
        try:
            # Create system prompt for implementation phase
            system_prompt = """You are an expert resume writer specializing in ATS optimization. 
            Your task is to implement the provided optimization plan to improve a resume for a specific job.
            
            Follow these strict guidelines:
            1. NEVER invent qualifications or experiences the candidate doesn't have - authenticity is critical
            2. ONLY use keywords that align with actual experience in the original resume
            3. Strategically reword existing skills and experiences to match the job description terminology
            4. Use exact phrasing from the job description when the resume contains equivalent concepts
            5. For each skill in the job description, look for related skills or synonyms in the resume that could be rephrased
            6. Pay special attention to high-impact sections (skills, experience, summary) - these affect the ATS score most
            7. Quantify achievements where possible (with numbers, percentages, etc.)
            8. Make SIGNIFICANT improvements to improve ATS score - be thorough but authentic
            9. Reorganize content to emphasize the most relevant experience for the job
            10. Use the exact terminology from the job description whenever the candidate has the equivalent experience
            11. Return ONLY the improved resume in Markdown format

            CRUCIAL: Maximize keyword matching while maintaining honesty. If the resume mentions "data analysis" and the job requires "data analytics," make that change. If the job requires "artificial intelligence" but the resume shows no related experience, do NOT add it.
            
            Your main goal is to significantly improve the resume's ATS score while maintaining complete authenticity.
            Focus on adding relevant keywords FROM THE JOB DESCRIPTION that match actual experience in the most natural and effective way.
            Your response should be the complete, ready-to-use optimized resume that implements all the 
            recommendations from the optimization plan but looks and reads like a professional document.
            """
            
            # Format the optimization plan for the prompt
            recommendations_text = ""
            for i, rec in enumerate(optimization_plan.get('recommendations', []), 1):
                section = rec.get('section', 'Unknown')
                change = rec.get('what', 'No specific change')
                reason = rec.get('why', 'No reason provided')
                recommendations_text += f"{i}. Section: {section}\n   Change: {change}\n   Reason: {reason}\n\n"
            
            # Process keywords to add - ensure everything is a string
            keywords_list = optimization_plan.get('keywords_to_add', [])
            keywords_strings = [str(kw) for kw in keywords_list]
            keywords_to_add = ", ".join(keywords_strings)
            
            # Process formatting suggestions - ensure everything is a string
            formatting_list = optimization_plan.get('formatting_suggestions', ['No formatting changes needed'])
            formatting_strings = [str(item) for item in formatting_list]
            formatting_suggestions = ", ".join(formatting_strings)
            
            # Create user message with implementation instructions
            user_message = f"""
            Please implement the following optimization plan to improve this resume for the target job description.
            
            OPTIMIZATION PLAN SUMMARY:
            {optimization_plan.get('summary', 'No summary provided')}
            
            JOB ANALYSIS:
            {optimization_plan.get('job_analysis', 'No job analysis provided')}
            
            SPECIFIC RECOMMENDATIONS:
            {recommendations_text}
            
            KEYWORDS TO ADD:
            {keywords_to_add}
            
            FORMATTING SUGGESTIONS:
            {formatting_suggestions}
            
            CUSTOMIZATION LEVEL: {level.title()}
            
            ORIGINAL RESUME:
            {resume_content}
            
            JOB DESCRIPTION:
            {job_description}
            
            Please implement all the recommended changes and return the complete, optimized resume in Markdown format.
            Focus on making these improvements while maintaining authenticity and professional standards.
            """
            
            # Call Claude for implementation
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_message
                }]
            )
            
            # Extract the customized resume
            customized_content = response.content[0].text
            
            # Clean up any markdown code block formatting
            customized_content = re.sub(r'```markdown\s*', '', customized_content)
            customized_content = re.sub(r'```\s*$', '', customized_content)
            
            return customized_content
                
        except Exception as e:
            logger.error(f"Error in resume implementation stage: {str(e)}")
            raise Exception(f"Failed to implement resume improvements: {str(e)}")

    def analyze_resume(self, resume_content, job_description):
        """
        Analyze resume without customization
        Returns detailed ATS analysis results
        """
        try:
            # Get enhanced ATS analysis
            ats_analysis = self.ats_analyzer.analyze(resume_content, job_description)
            return ats_analysis
        except Exception as e:
            logger.error(f"Error in resume analysis: {str(e)}")
            raise Exception(f"Failed to analyze resume: {str(e)}")

    def simulate_ats_systems(self, resume_content, job_description):
        """
        Simulate how different ATS systems would process the resume
        Returns analysis for multiple simulated systems
        """
        try:
            # Get base analysis
            base_analysis = self.ats_analyzer.analyze(resume_content, job_description)
            
            # Define system prompt for ATS simulation
            system_prompt = """You are an expert in Applicant Tracking Systems with deep knowledge of how different 
            ATS platforms process and score resumes. Simulate how these major ATS systems would evaluate the 
            provided resume for the given job description.
            
            For each ATS system, provide:
            1. Overall score (0-100)
            2. Key strengths detected
            3. Critical weaknesses or red flags
            4. Technical parsing issues that might occur
            5. System-specific recommendations
            
            Format your output as JSON with each ATS as a key and the results as structured data.
            Focus on these major systems:
            - Workday
            - Taleo
            - Greenhouse
            - Lever
            - ADP
            - iCIMS
            """
            
            # Create user message
            user_message = f"""
            Please simulate how different ATS systems would evaluate this resume for the provided job description.
            Base your simulation on the actual parsing and scoring behavior of each major ATS platform.
            
            Base ATS Analysis:
            - Overall Score: {base_analysis.get('score')}/100
            - Confidence: {base_analysis.get('confidence')}
            - Job Type: {base_analysis.get('job_type', 'General')}
            
            Resume:
            {resume_content}
            
            Job Description:
            {job_description}
            
            Please simulate each major ATS system's evaluation and return the results in JSON format.
            """
            
            # Call Claude for ATS simulation
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_message
                }]
            )
            
            simulation_text = response.content[0].text
            
            # Extract JSON from response
            try:
                # Find JSON block in the response
                json_match = re.search(r'```json\s*(.*?)\s*```', simulation_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find anything that looks like JSON
                    json_str = simulation_text
                
                # Parse the JSON
                ats_simulations = json.loads(json_str)
                return {
                    'simulations': ats_simulations,
                    'base_analysis': base_analysis
                }
            except Exception as json_error:
                logger.error(f"Error parsing ATS simulation JSON: {str(json_error)}")
                # Fallback to returning the raw text
                return {
                    'error': 'Failed to parse ATS simulation results',
                    'raw_response': simulation_text,
                    'base_analysis': base_analysis
                }
                
        except Exception as e:
            logger.error(f"Error in ATS simulation: {str(e)}")
            raise Exception(f"Failed to simulate ATS systems: {str(e)}")

    def _generate_detailed_comparison(self, original_analysis, new_analysis, optimization_plan):
        """
        Generate detailed comparison data between original and customized resume analyses
        """
        # Keywords comparison
        original_keywords = set(original_analysis.get('matching_keywords', []))
        new_keywords = set(new_analysis.get('matching_keywords', []))
        
        added_keywords = list(new_keywords - original_keywords)
        removed_keywords = list(original_keywords - new_keywords)
        
        # Section scores comparison
        section_improvements = {}
        for section, new_score in new_analysis.get('section_scores', {}).items():
            original_score = original_analysis.get('section_scores', {}).get(section, 0)
            improvement = new_score - original_score
            section_improvements[section] = {
                'original': original_score,
                'new': new_score,
                'improvement': improvement
            }
            
        # Count total changes
        total_changes = len(optimization_plan.get('recommendations', []))
        
        # Calculate keyword density change
        original_density = original_analysis.get('keyword_density', 0)
        new_density = new_analysis.get('keyword_density', 0)
        density_change = new_density - original_density
        
        return {
            'added_keywords': added_keywords,
            'removed_keywords': removed_keywords,
            'new_keywords_count': len(added_keywords),
            'section_improvements': section_improvements,
            'total_changes': total_changes,
            'keyword_density': {
                'original': original_density,
                'new': new_density,
                'change': density_change
            }
        }