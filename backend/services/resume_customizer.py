import os
import logging
import json
import re
import uuid
from .ats_analyzer import EnhancedATSAnalyzer
from .claude_client import ClaudeClient

logger = logging.getLogger(__name__)

class ResumeCustomizer:
    def __init__(self):
        # Initialize the Claude client
        self.claude = ClaudeClient()
        self.model = self.claude.model
        self.ats_analyzer = EnhancedATSAnalyzer()
        
        # Customization parameters
        self.customization_levels = {
            "conservative": 0.7,  # Minimal changes, focus on essential alignment
            "balanced": 1.0,      # Default level - reasonable optimization
            "extensive": 1.3      # More aggressive optimization
        }
        self.default_level = "balanced"
        
        # Industry-specific guidance for different sectors
        self.industry_guidance = {}
        
    def _generate_customization_notes(self, optimization_plan, comparison_data, level, industry=None):
        """
        Generate human-readable notes explaining the customization changes
        based on the optimization plan and comparison data.
        """
        try:
            notes = []
            
            # Overall summary
            notes.append(f"<h5 class='text-lg font-semibold mt-2 mb-1'>Summary</h5>")
            notes.append(f"<p class='mb-2'>{optimization_plan.get('summary', 'Resume customized to better match the job requirements.')}</p>")
            
            # Add job analysis
            notes.append(f"<h5 class='text-lg font-semibold mt-4 mb-1'>Job Analysis</h5>")
            notes.append(f"<p class='mb-2'>{optimization_plan.get('job_analysis', 'Analysis of key job requirements and their alignment with your resume.')}</p>")
            
            # Customization approach
            notes.append(f"<h5 class='text-lg font-semibold mt-4 mb-1'>Customization Approach</h5>")
            notes.append(f"<p class='mb-2'>Level: <span class='font-medium'>{level.capitalize()}</span>")
            if industry:
                notes.append(f" | Industry: <span class='font-medium'>{industry}</span>")
            notes.append("</p>")
            
            # Add keyword information
            if comparison_data and 'added_keywords' in comparison_data:
                added_keywords = comparison_data.get('added_keywords', [])
                if added_keywords:
                    notes.append(f"<h5 class='text-lg font-semibold mt-4 mb-1'>Added Keywords</h5>")
                    notes.append("<div class='flex flex-wrap gap-1 mb-3'>")
                    for keyword in added_keywords:
                        notes.append(f"<span class='px-2 py-0.5 text-xs font-medium rounded-full bg-accent-light/80 text-white'>{keyword}</span>")
                    notes.append("</div>")
            
            # Add section improvements
            if comparison_data and 'section_improvements' in comparison_data:
                section_improvements = comparison_data.get('section_improvements', {})
                if section_improvements:
                    notes.append(f"<h5 class='text-lg font-semibold mt-4 mb-1'>Section Improvements</h5>")
                    notes.append("<div class='grid grid-cols-1 gap-2 mb-3'>")
                    for section, data in section_improvements.items():
                        if data.get('improvement', 0) > 0:
                            notes.append(f"<div class='text-sm mb-1'>{section.title()}: " + 
                                        f"<span class='text-gray-600 dark:text-gray-400'>{data.get('original', 0):.1f}</span> → " +
                                        f"<span class='text-accent-dark dark:text-accent-light'>{data.get('new', 0):.1f}</span> " +
                                        f"<span class='text-accent-light/90'>(+{data.get('improvement', 0):.1f})</span></div>")
                    notes.append("</div>")
            
            # Add implemented recommendations summary
            if 'recommendations' in optimization_plan:
                recommendations = optimization_plan.get('recommendations', [])
                if recommendations:
                    notes.append(f"<h5 class='text-lg font-semibold mt-4 mb-1'>Implemented Changes</h5>")
                    notes.append("<div class='space-y-3 mb-3'>")
                    for i, rec in enumerate(recommendations):
                        section = rec.get('section', 'General')
                        reason = rec.get('reason', 'Improved alignment with job requirements')
                        notes.append(f"<div class='p-3 bg-gray-50 dark:bg-gray-700 rounded-md border border-gray-200 dark:border-gray-600'>")
                        notes.append(f"<div class='font-medium mb-1'>{i+1}. {section}</div>")
                        notes.append(f"<div class='text-sm text-gray-600 dark:text-gray-400 mb-2'>{reason}</div>")
                        
                        # Only show brief descriptions rather than the full before/after text
                        change_description = rec.get('description', 'Optimized content for better keyword matching')
                        notes.append(f"<div class='text-sm'>{change_description}</div>")
                        notes.append("</div>")
                    notes.append("</div>")
            
            return "\n".join(notes)
        except Exception as e:
            logger.error(f"Error generating customization notes: {str(e)}")
            return "<p>Detailed customization notes could not be generated. The resume was customized to better match the job requirements.</p>"
            
    def customize_resume(self, resume_content, job_description, customization_level=None, industry=None, selected_recommendations=None):
        """
        Two-stage resume customization process:
        1. Analysis stage: Analyze resume vs job description and plan improvements
        2. Optimization stage: Implement planned improvements
        
        Parameters:
        - resume_content: The original resume content
        - job_description: The job description to customize for
        - customization_level: Level of customization (conservative, balanced, extensive)
        - industry: Target industry for more tailored optimization
        - selected_recommendations: List of recommendation IDs to implement (if None, implement all)
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
            optimization_plan = self._analyze_and_plan(resume_content, job_description, ats_analysis, level, industry)
            logger.info(f"Generated optimization plan with {len(optimization_plan['recommendations'])} recommendations")
            
            # Filter recommendations if specific ones were selected
            if selected_recommendations:
                filtered_recommendations = []
                for idx, rec in enumerate(optimization_plan['recommendations']):
                    if str(idx) in selected_recommendations:
                        filtered_recommendations.append(rec)
                
                # Update the plan with only selected recommendations
                optimization_plan['recommendations'] = filtered_recommendations
                optimization_plan['summary'] = f"Implementing {len(filtered_recommendations)} of {len(optimization_plan['recommendations'])} recommendations"
                logger.info(f"Filtered to {len(filtered_recommendations)} selected recommendations")
            
            # Stage 2: Implement improvements
            customized_content = self._implement_improvements(resume_content, job_description, optimization_plan, ats_analysis, level, industry)
            
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
            
            # Generate human-readable customization notes
            customization_notes = self._generate_customization_notes(
                optimization_plan,
                comparison_data,
                level,
                industry
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
                'industry': industry,
                'comparison_data': comparison_data,
                'customization_notes': customization_notes
            }

        except Exception as e:
            logger.error(f"Error in resume customization: {str(e)}")
            raise Exception(f"Failed to customize resume: {str(e)}")
    
    def _analyze_and_plan(self, resume_content, job_description, ats_analysis, level, industry=None):
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
            5. For each recommendation, provide the specific text to change and how it should be changed
            6. Include both the 'before' and 'after' text in each recommendation
            
            CRUCIAL: Maintain complete authenticity - never invent qualifications or experience that isn't shown in the original resume.
            Focus on optimizing terminology, structure, emphasis, and keyword alignment while preserving the candidate's actual background.
            
            For each recommendation, include:
            1. The section it applies to (like "Summary", "Experience", "Skills", etc.)
            2. What specific change should be made (using the exact words from the job description where applicable)
            3. Why this change will improve ATS performance
            4. The original text that should be modified (before_text)
            5. The suggested revised text (after_text)
            
            Your response must be in JSON format with these fields:
            {
                "summary": "Brief overall assessment of the resume's current alignment with the job",
                "job_analysis": "Brief analysis of the job description's key requirements and priorities",
                "keywords_to_add": ["list", "of", "important", "keywords", "to", "incorporate"],
                "formatting_suggestions": ["suggestions", "for", "better", "ATS", "friendly", "formatting"],
                "recommendations": [
                    {
                        "section": "Section name",
                        "what": "Specific change to make",
                        "why": "Why this change improves ATS performance",
                        "before_text": "Original text to be replaced",
                        "after_text": "Suggested new text"
                    }
                ]
            }
            """
            
            # Add industry-specific guidance if provided
            if industry and industry.lower() in self.industry_guidance:
                system_prompt += f"\n\nINDUSTRY-SPECIFIC GUIDANCE ({industry.upper()}):\n"
                system_prompt += self.industry_guidance[industry.lower()]
            
            # Set intensity factor based on customization level
            intensity_factor = 0.5  # default/balanced
            if level.lower() == "conservative":
                intensity_factor = 0.3
            elif level.lower() == "extensive":
                intensity_factor = 0.8
            
            user_message = f"""
            Please analyze this resume against the job description and create a detailed optimization plan.
            
            CUSTOMIZATION LEVEL: {level.title()} (intensity factor: {intensity_factor})
            
            ORIGINAL RESUME:
            {resume_content}
            
            JOB DESCRIPTION:
            {job_description}
            
            CURRENT ATS ANALYSIS:
            - Current ATS score: {ats_analysis['score']}
            - Matching keywords: {', '.join(ats_analysis.get('matching_keywords', []))}
            - Missing keywords: {', '.join(ats_analysis.get('missing_keywords', []))}
            - Job type: {ats_analysis.get('job_type', 'Unknown')}
            
            Adjustments for customization level:
            - Conservative: Focus only on the most essential improvements with minimal changes
            - Balanced: Make all reasonable improvements for good ATS optimization
            - Extensive: More aggressive optimization maximizing keyword incorporation
            
            Based on the {level} level selected, calibrate your recommendations accordingly.
            
            IMPORTANT: For EACH recommendation, you MUST include:
            - before_text: The EXACT text from the resume that needs modification
            - after_text: The EXACT text after your suggested changes
            
            Please provide your analysis and plan in the JSON format specified.
            """
            
            # Call Claude with prompt caching through our client
            response = self.claude.create_message(
                system=system_prompt,  # The client will automatically add cache_control
                messages=[{"role": "user", "content": user_message}],
                max_tokens=8192
            )
            
            # Extract and parse the optimization plan from Claude's response
            response_text = response.content[0].text
            
            # Try to extract JSON from the response using regex
            plan_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if plan_match:
                plan_json = plan_match.group(1)
            else:
                # If no code block, treat the entire response as JSON
                plan_json = response_text
                
            try:
                # Clean up the JSON string and parse it
                plan_json = re.sub(r'```\s*$', '', plan_json)  # Remove trailing backticks if present
                optimization_plan = json.loads(plan_json)
                
                # Validate and fix recommendations if needed
                recommendations = optimization_plan.get('recommendations', [])
                for rec in recommendations:
                    # Ensure key fields exist
                    if 'before_text' not in rec:
                        rec['before_text'] = "No original text provided"
                    if 'after_text' not in rec:
                        rec['after_text'] = "No suggested text provided"
                
                # Log some information about the plan
                recommendation_count = len(optimization_plan.get('recommendations', []))
                logger.info(f"Generated optimization plan with {recommendation_count} recommendations")
                
                return optimization_plan
                
            except json.JSONDecodeError as json_error:
                logger.error(f"Error parsing optimization plan JSON: {str(json_error)}")
                # Attempt to extract JSON with a more lenient regex if the first attempt failed
                json_pattern = r'{.*}'
                json_match = re.search(json_pattern, response_text, re.DOTALL)
                if json_match:
                    try:
                        plan_json = json_match.group(0)
                        optimization_plan = json.loads(plan_json)
                        return optimization_plan
                    except:
                        logger.error("Second JSON extraction attempt failed")
                
                # If all attempts fail, return a basic structure
                return {
                    "summary": "Error parsing optimization plan",
                    "recommendations": [],
                    "keywords_to_add": [],
                    "formatting_suggestions": [],
                    "raw_response": response_text
                }
                
        except Exception as e:
            logger.error(f"Error in resume analysis stage: {str(e)}")
            raise Exception(f"Failed to analyze resume: {str(e)}")
            
    def _get_industry_guidance(self, industry):
        """
        Provide industry-specific guidance for resume optimization
        """
        industry_guidance = {
            "technology": """
            - Emphasize technical skills using exact terms from job description
            - Include specific technologies, programming languages, frameworks, and methodologies
            - Highlight certifications and technical achievements
            - Use industry-standard abbreviations (API, UI/UX, CI/CD, etc.)
            - Focus on quantifiable technical achievements and project outcomes
            """,
            
            "healthcare": """
            - Include relevant medical terminology and specializations
            - Emphasize patient care metrics and outcomes
            - Include specific healthcare systems, technologies, and compliance frameworks
            - Highlight certifications, licenses, and continuing education
            - Use proper medical abbreviations and terminology (EHR, HIPAA, etc.)
            """,
            
            "finance": """
            - Emphasize quantifiable financial achievements and metrics
            - Include specific financial systems, regulations, and compliance frameworks
            - Use precise financial terminology relevant to the specific role
            - Highlight certifications (CFA, CPA, etc.) and regulatory knowledge
            - Focus on risk management, analytical skills, and reporting capabilities
            """,
            
            "marketing": """
            - Include specific marketing platforms, tools, and methodologies
            - Emphasize measurable campaign results and ROI figures
            - Highlight experience with specific channels (social media, email, content)
            - Use current marketing terminology (SEO, SEM, conversion optimization)
            - Focus on audience targeting, growth metrics, and brand development
            """,
            
            "education": """
            - Include specific teaching methodologies and curriculum development
            - Emphasize measurable student outcomes and achievement metrics
            - Highlight classroom management and institutional collaboration
            - Use appropriate educational terminology and frameworks
            - Focus on assessment methods and educational technology experience
            """,
            
            "manufacturing": """
            - Emphasize experience with specific manufacturing processes and systems
            - Include knowledge of quality standards, safety protocols, and compliance
            - Highlight efficiency improvements and cost reductions
            - Use industry-specific terminology (Six Sigma, Lean, JIT, etc.)
            - Focus on production metrics, team management, and problem-solving
            """,
            
            "retail": """
            - Emphasize customer experience, sales metrics, and inventory management
            - Include specific POS systems, CRM tools, and retail technologies
            - Highlight merchandising, promotion, and upselling experience
            - Use retail-specific terminology and metrics (conversion rate, shrinkage)
            - Focus on team leadership, operations, and customer service achievements
            """
        }
        
        # Return guidance for the specified industry or a generic message
        return industry_guidance.get(industry.lower(), 
            "Focus on terminology specific to this industry, including standard abbreviations, " 
            "systems, methodologies, and metrics that demonstrate domain expertise.")
    
    def _implement_improvements(self, resume_content, job_description, optimization_plan, ats_analysis, level, industry=None):
        """
        Implement the recommended improvements based on the optimization plan
        Returns the customized resume content
        """
        try:
            # Create system prompt for the implementation phase
            system_prompt = """You are an expert resume writer and ATS optimization specialist.
            Your task is to implement all the suggested improvements from the optimization plan to create a 
            highly effective, ATS-optimized version of this resume for the target job.
            
            This is the IMPLEMENTATION phase. The analysis has already been completed, and your job is to create
            a final, ready-to-use resume that incorporates all the suggested changes.
            
            When implementing the improvements:
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
            
            # Add industry-specific guidance if industry is provided
            if industry:
                industry_guidance = self._get_industry_guidance(industry)
                system_prompt += f"""
                
                INDUSTRY-SPECIFIC GUIDANCE:
                The target industry is {industry}. When implementing the improvements, consider:
                {industry_guidance}
                
                Ensure the final resume uses terminology that positions the candidate effectively for the {industry} industry.
                """
            
            # Format the optimization plan for the prompt
            recommendations_text = ""
            for i, rec in enumerate(optimization_plan.get('recommendations', []), 1):
                section = rec.get('section', 'Unknown')
                change = rec.get('what', 'No specific change')
                reason = rec.get('why', 'No reason provided')
                
                # Include both the before and after text in the recommendation if available
                recommendations_text += f"{i}. Section: {section}\n   Change: {change}\n   Reason: {reason}\n"
                if rec.get('before_text', '') != "No original text provided":
                    recommendations_text += f"   Before: {rec.get('before_text', '')}\n"
                if rec.get('after_text', '') != "No suggested text provided":
                    recommendations_text += f"   After: {rec.get('after_text', '')}\n"
                recommendations_text += "\n"
            
            # Process keywords to add - ensure everything is a string
            keywords_list = optimization_plan.get('keywords_to_add', [])
            keywords_strings = [str(kw) for kw in keywords_list]
            keywords_to_add = ", ".join(keywords_strings)
            
            # Process formatting suggestions - ensure everything is a string
            formatting_list = optimization_plan.get('formatting_suggestions', [])
            formatting_strings = [str(item) for item in formatting_list if item]
            if not formatting_strings:
                formatting_strings = ["No specific formatting changes needed"]
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
            
            # Call Claude with prompt caching through our client
            response = self.claude.create_message(
                system=system_prompt,  # The client will automatically add cache_control
                messages=[{"role": "user", "content": user_message}],
                max_tokens=8192
            )
            
            # Extract the customized resume
            customized_content = response.content[0].text
            
            # Clean up any markdown code block formatting
            customized_content = re.sub(r'```markdown\s*', '', customized_content)
            customized_content = re.sub(r'```\s*$', '', customized_content)
            
            return customized_content
                
        except Exception as e:
            logger.error(f"Error in resume improvement implementation: {str(e)}")
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

    def customize_resume_streaming(self, resume_content, job_description, customization_level=None, industry=None, selected_recommendations=None):
        """Streaming version of the resume customization process that uses Anthropic's streaming API format directly"""
        
        # Yield initial status update with Anthropic-compatible format
        yield json.dumps({
            'type': 'message_start',
            'message': {
                'id': f"msg_{str(uuid.uuid4()).replace('-', '')}",
                'role': 'assistant',
                'content': [],
                'model': self.model,
                'stop_reason': None
            }
        }) + "\n"
        
        # Yield content block start
        yield json.dumps({
            'type': 'content_block_start',
            'index': 0,
            'content_block': {
                'type': 'text',
                'text': ''
            }
        }) + "\n"
        
        try:
            # Set customization level
            level = customization_level or self.default_level
            if level not in self.customization_levels:
                level = self.default_level
            
            # Custom status update in Anthropic format
            yield json.dumps({
                'type': 'content_block_delta',
                'index': 0,
                'delta': {
                    'type': 'text_delta',
                    'text': 'Starting analysis of your resume against job requirements...'
                }
            }) + "\n"
            
            # Create ATS analyzer and run initial analysis
            original_ats_analyzer = EnhancedATSAnalyzer()
            ats_analysis = original_ats_analyzer.analyze(resume_content, job_description)
            
            # Send initial analysis results - convert to streaming format
            yield json.dumps({
                'type': 'content_block_delta',
                'index': 0,
                'delta': {
                    'type': 'text_delta',
                    'text': f"\nInitial analysis complete. Current ATS match score: {ats_analysis['score']:.2f}%\n"
                }
            }) + "\n"
            
            # Send planning status update
            yield json.dumps({
                'type': 'content_block_delta',
                'index': 0,
                'delta': {
                    'type': 'text_delta',
                    'text': '\nGenerating optimization plan...\n'
                }
            }) + "\n"
            
            # Generate optimization plan - this now returns Anthropic streaming events directly
            optimization_plan = None
            last_plan_result = None
            
            # Stream the planning process chunks
            for chunk in self._analyze_and_plan_streaming(resume_content, job_description, ats_analysis, level, industry):
                if isinstance(chunk, dict) and 'type' not in chunk:
                    # This is the final result with the structured plan
                    last_plan_result = chunk
                    optimization_plan = chunk
                    
                    # Send a summary of the plan in streaming format
                    recommendation_count = len(chunk.get('recommendations', []))
                    yield json.dumps({
                        'type': 'content_block_delta',
                        'index': 0,
                        'delta': {
                            'type': 'text_delta',
                            'text': f"\nOptimization plan generated with {recommendation_count} recommendations.\n"
                        }
                    }) + "\n"
                else:
                    # This is a streaming event from Anthropic - pass it through
                    yield chunk
            
            # Filter recommendations if needed
            if selected_recommendations and last_plan_result:
                filtered_recommendations = []
                for idx, rec in enumerate(last_plan_result['recommendations']):
                    if str(idx) in selected_recommendations:
                        filtered_recommendations.append(rec)
                
                # Update the plan with only selected recommendations
                last_plan_result['recommendations'] = filtered_recommendations
                
                # Send update in streaming format
                yield json.dumps({
                    'type': 'content_block_delta',
                    'index': 0,
                    'delta': {
                        'type': 'text_delta',
                        'text': f"\nApplying {len(filtered_recommendations)} selected recommendations.\n"
                    }
                }) + "\n"
            
            # Implementation status update
            yield json.dumps({
                'type': 'content_block_delta',
                'index': 0,
                'delta': {
                    'type': 'text_delta',
                    'text': '\nImplementing optimizations...\n'
                }
            }) + "\n"
            
            # Apply the improvements - this also returns Anthropic streaming events directly
            customized_content = None
            
            # Stream the implementation process
            for chunk in self._implement_improvements_streaming(resume_content, job_description, 
                                                           last_plan_result, ats_analysis, level, industry):
                if isinstance(chunk, dict) and 'type' not in chunk and 'final_content' in chunk:
                    # This is the final result with the full customized content
                    customized_content = chunk['final_content']
                    modified_sections = chunk.get('sections_modified', [])
                    
                    # Send completion message in streaming format
                    sections_text = ", ".join(modified_sections) if modified_sections else "None"
                    yield json.dumps({
                        'type': 'content_block_delta',
                        'index': 0,
                        'delta': {
                            'type': 'text_delta',
                            'text': f"\nCustomization complete. Modified sections: {sections_text}\n"
                        }
                    }) + "\n"
                else:
                    # This is a streaming event from Anthropic - pass it through
                    yield chunk
            
            # Final analysis status
            yield json.dumps({
                'type': 'content_block_delta',
                'index': 0,
                'delta': {
                    'type': 'text_delta',
                    'text': '\nPerforming final ATS analysis...\n'
                }
            }) + "\n"
            
            # Perform final ATS analysis on the customized resume
            new_ats_analyzer = EnhancedATSAnalyzer()
            new_ats_analysis = new_ats_analyzer.analyze(customized_content, job_description)
            
            improvement = new_ats_analysis['score'] - ats_analysis['score']
            
            # Send final analysis results in streaming format
            yield json.dumps({
                'type': 'content_block_delta',
                'index': 0,
                'delta': {
                    'type': 'text_delta',
                    'text': f"\nFinal analysis complete:\n- Original score: {ats_analysis['score']:.2f}%\n- New score: {new_ats_analysis['score']:.2f}%\n- Improvement: {improvement:.2f}%\n"
                }
            }) + "\n"
            
            # Generate and send comparison data in a format compatible with client-side display
            comparison_data = self._generate_detailed_comparison(
                ats_analysis, 
                new_ats_analysis,
                last_plan_result
            )
            
            # Close the content block
            yield json.dumps({
                'type': 'content_block_stop',
                'index': 0
            }) + "\n"
            
            # Send the customization_complete event as a message_delta
            yield json.dumps({
                'type': 'message_delta',
                'delta': {
                    'stop_reason': 'end_turn'
                },
                'usage': {
                    'output_tokens': 1000  # Estimated usage
                }
            }) + "\n"
            
            # Append the final customization data as a structured message for client to save
            yield json.dumps({
                'type': 'message_stop',
                'customization_data': {
                    'original_content': resume_content,
                    'customized_content': customized_content,
                    'original_score': ats_analysis['score'],
                    'new_score': new_ats_analysis['score'],
                    'improvement': improvement,
                    'optimization_plan': last_plan_result,
                    'comparison_data': comparison_data
                }
            }) + "\n"
            
        except Exception as e:
            logger.error(f"Error in streaming resume customization: {str(e)}")
            
            # Send error in Anthropic streaming format
            yield json.dumps({
                'type': 'error',
                'error': {
                    'type': 'streaming_error',
                    'message': str(e)
                }
            }) + "\n"
    
    def _analyze_and_plan_streaming(self, resume_content, job_description, ats_analysis, level, industry=None):
        """Streaming version of the resume analysis and planning stage"""
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
            5. For each recommendation, provide the specific text to change and how it should be changed
            6. Include both the 'before' and 'after' text in each recommendation
            
            CRUCIAL: Maintain complete authenticity - never invent qualifications or experience that isn't shown in the original resume.
            Focus on optimizing terminology, structure, emphasis, and keyword alignment while preserving the candidate's actual background.
            
            For each recommendation, include:
            1. The section it applies to (like "Summary", "Experience", "Skills", etc.)
            2. What specific change should be made (using the exact words from the job description where applicable)
            3. Why this change will improve ATS performance
            4. The original text that should be modified (before_text)
            5. The suggested revised text (after_text)
            
            Your response must be in JSON format with these fields:
            {
                "summary": "Brief overall assessment of the resume's current alignment with the job",
                "job_analysis": "Brief analysis of the job description's key requirements and priorities",
                "keywords_to_add": ["list", "of", "important", "keywords", "to", "incorporate"],
                "formatting_suggestions": ["suggestions", "for", "better", "ATS", "friendly", "formatting"],
                "recommendations": [
                    {
                        "section": "Section name",
                        "what": "Specific change to make",
                        "why": "Why this change improves ATS performance",
                        "before_text": "Original text to be replaced",
                        "after_text": "Suggested new text"
                    }
                ]
            }
            """
            
            # Add industry-specific guidance if provided
            if industry and industry.lower() in self.industry_guidance:
                system_prompt += f"\n\nINDUSTRY-SPECIFIC GUIDANCE ({industry.upper()}):\n"
                system_prompt += self.industry_guidance[industry.lower()]
            
            # Set intensity factor based on customization level
            intensity_factor = 0.5  # default/balanced
            if level.lower() == "conservative":
                intensity_factor = 0.3
            elif level.lower() == "extensive":
                intensity_factor = 0.8
            
            user_message = f"""
            Please analyze this resume against the job description and create a detailed optimization plan.
            
            CUSTOMIZATION LEVEL: {level.title()} (intensity factor: {intensity_factor})
            
            ORIGINAL RESUME:
            {resume_content}
            
            JOB DESCRIPTION:
            {job_description}
            
            CURRENT ATS ANALYSIS:
            - Current ATS score: {ats_analysis['score']}
            - Matching keywords: {', '.join(ats_analysis.get('matching_keywords', []))}
            - Missing keywords: {', '.join(ats_analysis.get('missing_keywords', []))}
            - Job type: {ats_analysis.get('job_type', 'Unknown')}
            
            Adjustments for customization level:
            - Conservative: Focus only on the most essential improvements with minimal changes
            - Balanced: Make all reasonable improvements for good ATS optimization
            - Extensive: More aggressive optimization maximizing keyword incorporation
            
            Based on the {level} level selected, calibrate your recommendations accordingly.
            
            IMPORTANT: For EACH recommendation, you MUST include:
            - before_text: The EXACT text from the resume that needs modification
            - after_text: The EXACT text after your suggested changes
            
            Please provide your analysis and plan in the JSON format specified.
            """
            
            # Use centralized Claude client with streaming
            accumulated_text = ""
            
            # Stream the response using our Claude client
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
                # Forward all the stream events directly, capturing the content for processing
                for event in stream:
                    event_dict = event.model_dump()
                    
                    # Special handling for content_block_delta events to extract text
                    if event_dict.get('type') == 'content_block_delta' and event_dict.get('delta', {}).get('type') == 'text_delta':
                        text_chunk = event_dict['delta']['text']
                        accumulated_text += text_chunk
                    
                    # Forward the event as a properly formatted JSON string
                    yield json.dumps(event_dict) + "\n"
            
            # After streaming is complete, try to parse the accumulated text as JSON
            try:
                # Clean up the text to extract just the JSON portion
                json_text = accumulated_text.strip()
                if json_text.startswith('```json'):
                    json_text = json_text[7:]
                if json_text.endswith('```'):
                    json_text = json_text[:-3]
                
                # Parse the JSON
                plan_result = json.loads(json_text.strip())
                
                # Yield the final structured plan result
                yield plan_result
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON from analysis response: {str(e)}")
                logger.debug(f"Raw response text: {accumulated_text[:500]}...")
                
                # Still return something useful even if JSON parsing fails
                yield {
                    "summary": "Error creating structured plan. Please check the raw output.",
                    "recommendations": [],
                    "raw_output": accumulated_text
                }
            
        except Exception as e:
            logger.error(f"Error in streaming analysis and planning: {str(e)}")
            yield f"Error in analysis: {str(e)}"
            yield {"error": str(e)}
    
    def _implement_improvements_streaming(self, resume_content, job_description, optimization_plan, ats_analysis, level, industry=None):
        """Streaming version of the resume implementation stage"""
        try:
            # Create system prompt for the implementation phase
            system_prompt = """You are an expert ATS optimization consultant specializing in resume customization.
            
            Your task is to implement the optimization plan to improve the resume's ATS score while maintaining authenticity.
            
            Follow these guidelines:
            1. Implement ALL the specific recommendations in the optimization plan
            2. Maintain the overall structure and formatting of the original resume
            3. Ensure all formatting is consistent (bullet points, headings, etc.)
            4. Use Markdown formatting for the optimized resume
            5. Include the ENTIRE resume content in your response, not just the changed parts
            6. NEVER fabricate experience, qualifications, or dates that weren't in the original
            
            IMPORTANT: Your output should be the complete resume in markdown format, ready to be used directly.
            Markdown headers (#, ##, ###) are encouraged for section titles.
            """
            
            # Add industry-specific guidance if provided
            if industry and industry.lower() in self.industry_guidance:
                system_prompt += f"\n\nINDUSTRY-SPECIFIC GUIDANCE ({industry.upper()}):\n"
                system_prompt += self.industry_guidance[industry.lower()]
            
            # Extract recommendations text
            recommendations = optimization_plan.get('recommendations', [])
            recommendations_text = ""
            
            for idx, rec in enumerate(recommendations):
                recommendations_text += f"\n{idx+1}. {rec.get('section', 'General')} Section:\n"
                recommendations_text += f"   - What: {rec.get('what', 'No change specified')}\n"
                recommendations_text += f"   - Why: {rec.get('why', 'No reason provided')}\n"
                recommendations_text += f"   - Original Text: {rec.get('before_text', 'No original text provided')}\n"
                recommendations_text += f"   - Suggested Text: {rec.get('after_text', 'No suggested text provided')}\n"
            
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
            {', '.join(str(kw) for kw in optimization_plan.get('keywords_to_add', []))}
            
            FORMATTING SUGGESTIONS:
            {', '.join(str(item) for item in optimization_plan.get('formatting_suggestions', ['No formatting changes needed']))}
            
            CUSTOMIZATION LEVEL: {level.title()}
            
            ORIGINAL RESUME:
            {resume_content}
            
            JOB DESCRIPTION:
            {job_description}
            
            Please implement all the recommended changes and return the complete, optimized resume in Markdown format.
            Focus on making these improvements while maintaining authenticity and professional standards.
            """
            
            # Track the accumulated text for parsing later
            accumulated_text = ""
            
            # Stream the response directly from Anthropic API with prompt caching
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
                # Forward all the stream events directly, capturing the content for processing
                for event in stream:
                    event_dict = event.model_dump()
                    
                    # Special handling for content_block_delta events to extract text
                    if event_dict.get('type') == 'content_block_delta' and event_dict.get('delta', {}).get('type') == 'text_delta':
                        text_chunk = event_dict['delta']['text']
                        accumulated_text += text_chunk
                    
                    # Forward the event as a properly formatted JSON string
                    yield json.dumps(event_dict) + "\n"
            
            # Clean up any markdown code block formatting
            customized_content = re.sub(r'```markdown\s*', '', accumulated_text)
            customized_content = re.sub(r'```\s*$', '', customized_content)
            
            # Identify modified sections (basic implementation)
            modified_sections = []
            for rec in optimization_plan.get('recommendations', []):
                section = rec.get('section')
                if section and section not in modified_sections:
                    modified_sections.append(section)
            
            # Return the final result
            yield {
                'final_content': customized_content,
                'sections_modified': modified_sections
            }
                
        except Exception as e:
            logger.error(f"Error in streaming resume implementation: {str(e)}")
            yield {"error": str(e)}
    
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
            
            # Call Claude with prompt caching through our client
            response = self.claude.create_message(
                system=system_prompt,  # The client will automatically add cache_control
                messages=[{"role": "user", "content": user_message}],
                max_tokens=8192
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
        
        # Extract rationale for each recommendation
        recommendations_with_rationale = []
        for rec in optimization_plan.get('recommendations', []):
            section = rec.get('section', 'Unknown')
            change = rec.get('what', 'No specific change')
            reason = rec.get('why', 'No reason provided')
            
            # Extract the specific change details
            change_details = {
                'section': section,
                'change': change,
                'reason': reason,
                'impact_rating': self._calculate_impact_rating(section, change, reason),
                'ats_relevance': self._assess_ats_relevance(change, reason),
                'before_text': rec.get('before_text', ''),
                'after_text': rec.get('after_text', ''),
                'keywords_affected': self._extract_affected_keywords(change, added_keywords)
            }
            recommendations_with_rationale.append(change_details)
            
        # Section-by-section improvement explanations
        section_explanations = {}
        for section, scores in section_improvements.items():
            if scores['improvement'] > 0:
                section_explanations[section] = self._generate_section_explanation(
                    section, 
                    scores['improvement'],
                    recommendations_with_rationale
                )
        
        return {
            'added_keywords': added_keywords,
            'removed_keywords': removed_keywords,
            'new_keywords_count': len(added_keywords),
            'section_improvements': section_improvements,
            'section_explanations': section_explanations,
            'total_changes': total_changes,
            'recommendations_with_rationale': recommendations_with_rationale,
            'keyword_density': {
                'original': original_density,
                'new': new_density,
                'change': density_change
            }
        }
        
    def _calculate_impact_rating(self, section, change, reason):
        """
        Calculate an impact rating (1-10) for a specific change based on section importance
        and the nature of the change
        """
        # Base impact scores by section (reflecting ATS importance)
        section_base_scores = {
            'summary': 9,
            'skills': 10,
            'experience': 8,
            'education': 6,
            'projects': 7,
            'certifications': 7,
            'achievements': 8,
            'header': 5
        }
        
        # Default score for unknown sections
        base_score = section_base_scores.get(section.lower(), 5)
        
        # Keyword indicators that suggest higher impact
        high_impact_indicators = [
            'keyword', 'match', 'critical', 'essential', 'required', 
            'important', 'significant', 'key', 'ats score', 'visibility'
        ]
        
        # Check if reason or change contain high impact indicators
        impact_modifiers = sum(1 for term in high_impact_indicators if term in reason.lower() or term in change.lower())
        
        # Calculate final score (capped at 10)
        impact_score = min(base_score + impact_modifiers, 10)
        
        return impact_score
        
    def _assess_ats_relevance(self, change, reason):
        """
        Assess how relevant a change is specifically for ATS optimization
        Returns a description of the ATS relevance
        """
        ats_keywords = [
            'keyword', 'match', 'scan', 'parse', 'algorithm', 'ats', 'applicant tracking',
            'filter', 'rank', 'score', 'visibility', 'searchable'
        ]
        
        reason_lower = reason.lower()
        change_lower = change.lower()
        
        # Count how many ATS-related terms appear in the reason
        relevance_count = sum(1 for term in ats_keywords if term in reason_lower or term in change_lower)
        
        # Determine relevance category
        if relevance_count >= 3:
            return "Critical for ATS scoring"
        elif relevance_count >= 1:
            return "Improves ATS visibility"
        else:
            return "General improvement"
            
    def _extract_affected_keywords(self, change, added_keywords):
        """
        Extract which keywords from the added_keywords list are affected by this specific change
        """
        change_lower = change.lower()
        return [keyword for keyword in added_keywords if keyword.lower() in change_lower]
        
    def _generate_section_explanation(self, section, improvement, recommendations):
        """
        Generate a detailed explanation of why a specific section improved
        """
        # Filter recommendations affecting this section
        section_recommendations = [r for r in recommendations if r['section'].lower() == section.lower()]
        
        # Count how many changes were made to this section
        change_count = len(section_recommendations)
        
        # If no specific changes were found, provide a generic explanation
        if change_count == 0:
            return f"This section improved by {improvement:.1f} points. The changes in other sections may have indirectly improved this section's score."
        
        # Get the highest impact changes
        section_recommendations.sort(key=lambda x: x['impact_rating'], reverse=True)
        top_recommendations = section_recommendations[:3]  # Get top 3 or less
        
        # Generate explanation
        explanation = f"This section improved by {improvement:.1f} points with {change_count} changes. "
        explanation += "Key improvements include: "
        
        # Add explanation for each top recommendation
        for i, rec in enumerate(top_recommendations):
            if i > 0:
                explanation += "; "
            explanation += rec['reason']
            
        return explanation