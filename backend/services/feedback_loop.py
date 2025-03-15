import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from anthropic import Anthropic
from sqlalchemy import func
from models import CustomizedResume, CustomizationEvaluation, OptimizationSuggestion, ABTest
from services.ats_analyzer import EnhancedATSAnalyzer
from extensions import db

logger = logging.getLogger(__name__)

class FeedbackLoop:
    """
    Implements the continuous feedback loop for resume customization improvement
    following the Evaluator-Optimizer pattern from Anthropic's effective agents guide
    """
    
    def __init__(self):
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            raise ValueError('ANTHROPIC_API_KEY environment variable must be set')
        
        self.client = Anthropic(api_key=self.anthropic_key)
        self.model = "claude-3-7-sonnet-20250219"
        
        # Cache configuration
        self.use_cache = os.environ.get('USE_PROMPT_CACHE', 'true').lower() == 'true'
        self.cache_dir = os.environ.get('PROMPT_CACHE_DIR', 'cache/prompts')
        
        # Create cache directory if it doesn't exist
        if self.use_cache and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def _generate_cache_key(self, model, messages=None, system=None, **kwargs):
        """Generate a deterministic cache key from request parameters"""
        # Create a dictionary with all relevant parameters
        cache_dict = {
            "model": model
        }
        
        if messages:
            cache_dict["messages"] = messages
        
        if system:
            cache_dict["system"] = system
            
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
                    logger.info(f"Cache hit for {cache_key}")
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading cache: {str(e)}")
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
                logger.info(f"Saved to cache: {cache_key}")
        except Exception as e:
            logger.error(f"Error writing to cache: {str(e)}")
    
    def evaluate_customization(self, resume_id):
        """
        Evaluate a specific resume customization and generate insights
        """
        try:
            # Get the customized resume
            customized_resume = CustomizedResume.query.get(resume_id)
            if not customized_resume:
                return {"error": "Resume not found"}
            
            # Get the job description
            from models import JobDescription
            job_description = JobDescription.query.get(customized_resume.job_description_id)
            if not job_description:
                return {"error": "Job description not found"}
            
            # Gather metrics
            metrics = {
                "score_improvement": customized_resume.ats_score - customized_resume.original_ats_score,
                "added_keywords": customized_resume.added_keywords_count,
                "changes_count": customized_resume.changes_count,
                "section_improvements": customized_resume.comparison_data.get("section_improvements", {}) if customized_resume.comparison_data else {},
                "user_rating": customized_resume.user_rating,
                "user_feedback": customized_resume.user_feedback,
                "was_effective": customized_resume.was_effective,
                "interview_secured": customized_resume.interview_secured,
                "job_secured": customized_resume.job_secured
            }
            
            # Get keywords from job description
            ats_analyzer = EnhancedATSAnalyzer()
            job_elements = ats_analyzer._process_job_description(job_description.content)
            job_keywords = list(job_elements.get("keywords", {}).keys())
            
            # Generate evaluation using Claude
            system_prompt = """You are an expert ATS resume optimization evaluator. 
            Analyze the effectiveness of a resume customization based on the provided metrics.
            Provide specific insights on:
            1. What worked well in this customization
            2. What could be improved
            3. Specific recommendations for future customizations of similar resumes
            
            Be specific, detailed, and actionable in your evaluation.
            """
            
            user_message = f"""
            CUSTOMIZATION METRICS:
            - ATS score improvement: {metrics['score_improvement']:.2f} points
            - Keywords added: {metrics['added_keywords']}
            - Total changes made: {metrics['changes_count']}
            - Section improvements: {json.dumps(metrics['section_improvements'], indent=2)}
            
            USER FEEDBACK:
            - User rating: {metrics['user_rating'] if metrics['user_rating'] else 'Not provided'}
            - User feedback: {metrics['user_feedback'] if metrics['user_feedback'] else 'None'}
            - Led to interview: {metrics['interview_secured'] if metrics['interview_secured'] is not None else 'Unknown'}
            - Led to job offer: {metrics['job_secured'] if metrics['job_secured'] is not None else 'Unknown'}
            
            JOB DESCRIPTION KEYWORDS:
            {", ".join(job_keywords[:30])}
            
            Please evaluate this customization and provide actionable insights for future improvements.
            Focus on both what worked well and what could be improved.
            """
            
            # Generate cache key for this request
            messages = [{"role": "user", "content": user_message}]
            cache_key = self._generate_cache_key(
                model=self.model,
                messages=messages,
                system=system_prompt,
                max_tokens=8192
            )
            
            # Try to get from cache
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                response = type('obj', (object,), {
                    'content': cached_response['content']
                })
            else:
                # Call Claude
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8192,
                    system=system_prompt,
                    messages=messages,
                    cache_seed=cache_key  # Use cache_seed for Claude's server-side caching
                )
                
                # Save to cache
                response_data = {
                    "content": [{"text": response.content[0].text}]
                }
                self._save_to_cache(cache_key, response_data)
            
            evaluation_text = response.content[0].text
            
            # Store the evaluation
            evaluation = CustomizationEvaluation(
                customized_resume_id=resume_id,
                evaluation_text=evaluation_text,
                metrics=metrics,
                created_at=datetime.utcnow()
            )
            db.session.add(evaluation)
            db.session.commit()
            
            logger.info(f"Created evaluation for resume ID {resume_id}")
            
            return {
                "success": True,
                "evaluation": evaluation_text,
                "metrics": metrics,
                "evaluation_id": evaluation.id
            }
            
        except Exception as e:
            logger.error(f"Error evaluating customization: {str(e)}")
            return {"error": f"Failed to evaluate customization: {str(e)}"}
    
    def optimize_customization_strategy(self, min_evaluations=50):
        """
        Analyze patterns in customization evaluations to improve the model
        """
        try:
            # Count available evaluations
            evaluation_count = CustomizationEvaluation.query.count()
            if evaluation_count < min_evaluations:
                logger.info(f"Not enough evaluations for optimization yet: {evaluation_count}/{min_evaluations}")
                return {
                    "success": False,
                    "message": f"Not enough data for optimization yet ({evaluation_count}/{min_evaluations})"
                }
            
            # Get recent evaluations
            evaluations = CustomizationEvaluation.query.order_by(CustomizationEvaluation.created_at.desc()).limit(100).all()
            
            # Filter for successful customizations (good ratings or led to interviews)
            successful = [e for e in evaluations if 
                        (e.metrics.get('user_rating', 0) >= 4) or 
                        (e.metrics.get('interview_secured') == True)]
            
            # Filter for unsuccessful customizations
            unsuccessful = [e for e in evaluations if 
                        (e.metrics.get('user_rating', 0) <= 2) or 
                        (e.metrics.get('interview_secured') == False)]
            
            if len(successful) < 10 or len(unsuccessful) < 10:
                return {
                    "success": False,
                    "message": f"Insufficient contrast in outcomes for optimization. Need at least 10 successful and 10 unsuccessful examples. Currently have {len(successful)} successful and {len(unsuccessful)} unsuccessful."
                }
            
            system_prompt = """You are an expert AI system optimizer focused on resume customization.
            Based on patterns in successful and unsuccessful resume customizations, 
            recommend specific improvements to the resume customization system.
            
            Focus on:
            1. Key differences between successful and unsuccessful customizations
            2. Patterns in keyword selection and incorporation
            3. Section-specific optimization strategies
            4. Prompt engineering improvements for the LLM
            5. Areas where the system should be more or less aggressive
            
            Structure your response into:
            1. ANALYSIS: Summary of key patterns observed
            2. RECOMMENDATIONS: Specific changes to make to the system
            3. PROMPT ENGINEERING: Specific suggested changes to prompts
            """
            
            # Prepare examples in a structured format
            successful_examples = json.dumps([{
                "metrics": e.metrics,
                "evaluation": e.evaluation_text
            } for e in successful[:10]], indent=2)
            
            unsuccessful_examples = json.dumps([{
                "metrics": e.metrics,
                "evaluation": e.evaluation_text
            } for e in unsuccessful[:10]], indent=2)
            
            user_message = f"""
            Based on our analysis of resume customizations, please recommend improvements to our system.
            
            SUCCESSFUL CUSTOMIZATIONS (highest ratings or led to interviews):
            {successful_examples}
            
            UNSUCCESSFUL CUSTOMIZATIONS (low ratings or no interviews):
            {unsuccessful_examples}
            
            Please provide specific, actionable recommendations for:
            1. Prompt engineering improvements
            2. Keyword selection strategies
            3. Section-specific optimization approaches
            4. Balancing authenticity with keyword optimization
            """
            
            # Generate cache key for this request
            messages = [{"role": "user", "content": user_message}]
            cache_key = self._generate_cache_key(
                model=self.model,
                messages=messages,
                system=system_prompt,
                max_tokens=8192
            )
            
            # Try to get from cache
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                response = type('obj', (object,), {
                    'content': cached_response['content']
                })
            else:
                # Call Claude
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8192,
                    system=system_prompt,
                    messages=messages,
                    cache_seed=cache_key  # Use cache_seed for Claude's server-side caching
                )
                
                # Save to cache
                response_data = {
                    "content": [{"text": response.content[0].text}]
                }
                self._save_to_cache(cache_key, response_data)
            
            # Store the optimization suggestions
            optimization = OptimizationSuggestion(
                content=response.content[0].text,
                created_at=datetime.utcnow(),
                based_on_evaluations=evaluation_count,
                implemented=False
            )
            db.session.add(optimization)
            db.session.commit()
            
            logger.info(f"Created optimization suggestion based on {evaluation_count} evaluations")
            
            return {
                "success": True,
                "optimization_id": optimization.id,
                "content": response.content[0].text,
                "based_on_evaluations": evaluation_count
            }
            
        except Exception as e:
            logger.error(f"Error optimizing customization strategy: {str(e)}")
            return {"error": f"Failed to optimize strategy: {str(e)}"}
    
    def implement_ab_testing(self, optimization_id):
        """
        Create A/B test variants of prompts based on optimization suggestions
        """
        try:
            # Get the optimization suggestion
            optimization = OptimizationSuggestion.query.get(optimization_id)
            if not optimization:
                return {"error": "Optimization suggestion not found"}
            
            # Get current prompts (this would be stored in a config or DB in a real system)
            # Here we're simulating this with placeholder values
            current_prompts = {
                "analyze_prompt": "You are an expert ATS optimization consultant specializing in resume customization...",
                "customize_prompt": "You are an expert resume writer specializing in ATS optimization..."
            }
            
            # Create variants based on the optimization suggestion
            # In a real implementation, you would parse the suggestion and apply it to the prompts
            # Here we're simulating it
            prompt_variants = {
                "baseline": {
                    "analyze_prompt": current_prompts["analyze_prompt"],
                    "customize_prompt": current_prompts["customize_prompt"]
                },
                "variant_a": {
                    "analyze_prompt": current_prompts["analyze_prompt"] + "\n\nIMPORTANT: Focus more on keyword matching.",
                    "customize_prompt": current_prompts["customize_prompt"]
                },
                "variant_b": {
                    "analyze_prompt": current_prompts["analyze_prompt"],
                    "customize_prompt": current_prompts["customize_prompt"] + "\n\nIMPORTANT: Prioritize section-specific improvements."
                }
            }
            
            # Create A/B test configuration
            ab_test = ABTest(
                name=f"Optimization_{optimization.id}",
                description=f"Testing optimization suggestions from {optimization.created_at}",
                variants=prompt_variants,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=14),  # Run for two weeks
                is_active=True
            )
            
            db.session.add(ab_test)
            db.session.commit()
            
            logger.info(f"Created A/B test '{ab_test.name}' for optimization ID {optimization_id}")
            
            return {
                "success": True,
                "test_id": ab_test.id,
                "name": ab_test.name,
                "variants": list(prompt_variants.keys()),
                "end_date": ab_test.end_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error implementing A/B testing: {str(e)}")
            return {"error": f"Failed to implement A/B testing: {str(e)}"}
    
    def analyze_ab_test_results(self, test_id):
        """
        Analyze the results of an A/B test and determine the winner
        """
        try:
            # Get the A/B test
            ab_test = ABTest.query.get(test_id)
            if not ab_test:
                return {"error": "A/B test not found"}
            
            # In a real implementation, you would query metrics for each variant
            # Here we're simulating it with placeholder values
            results = {
                "baseline": {
                    "count": 50,
                    "avg_improvement": 2.5,
                    "avg_rating": 3.8,
                    "interview_rate": 0.22
                },
                "variant_a": {
                    "count": 48,
                    "avg_improvement": 3.1,
                    "avg_rating": 4.1,
                    "interview_rate": 0.29
                },
                "variant_b": {
                    "count": 52,
                    "avg_improvement": 2.8,
                    "avg_rating": 3.9,
                    "interview_rate": 0.25
                }
            }
            
            # Determine the winner based on a weighted score
            # This could be more sophisticated in a real implementation
            scores = {}
            for variant, metrics in results.items():
                # Weight factors (these could be configurable)
                score = (
                    metrics["avg_improvement"] * 5 +
                    metrics["avg_rating"] * 10 +
                    metrics["interview_rate"] * 50
                )
                scores[variant] = score
            
            winner = max(scores, key=scores.get)
            
            # Update the A/B test with results and winner
            ab_test.results = results
            ab_test.winner = winner
            ab_test.is_active = False
            ab_test.end_date = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"A/B test '{ab_test.name}' completed with winner: {winner}")
            
            return {
                "success": True,
                "winner": winner,
                "results": results,
                "scores": scores
            }
            
        except Exception as e:
            logger.error(f"Error analyzing A/B test results: {str(e)}")
            return {"error": f"Failed to analyze A/B test results: {str(e)}"}
            
    def apply_winning_variant(self, test_id, optimization_id):
        """
        Apply the winning variant from an A/B test
        """
        try:
            # Get the A/B test
            ab_test = ABTest.query.get(test_id)
            if not ab_test:
                return {"error": "A/B test not found"}
                
            # Get the optimization suggestion
            optimization = OptimizationSuggestion.query.get(optimization_id)
            if not optimization:
                return {"error": "Optimization suggestion not found"}
            
            if not ab_test.winner:
                return {"error": "A/B test does not have a winner yet"}
            
            # In a real implementation, you would update the production prompts
            # Here we're just simulating it
            
            # Mark the optimization as implemented
            optimization.implemented = True
            optimization.implementation_date = datetime.utcnow()
            optimization.implementation_notes = f"Implemented variant '{ab_test.winner}' from A/B test '{ab_test.name}'"
            db.session.commit()
            
            logger.info(f"Applied winning variant '{ab_test.winner}' from A/B test '{ab_test.name}'")
            
            return {
                "success": True,
                "winner": ab_test.winner,
                "implementation_date": optimization.implementation_date.isoformat(),
                "implementation_notes": optimization.implementation_notes
            }
            
        except Exception as e:
            logger.error(f"Error applying winning variant: {str(e)}")
            return {"error": f"Failed to apply winning variant: {str(e)}"}
    
    def list_evaluations(self):
        """
        List all customization evaluations
        """
        try:
            evaluations = CustomizationEvaluation.query.order_by(CustomizationEvaluation.created_at.desc()).all()
            return evaluations
        except Exception as e:
            logger.error(f"Error listing evaluations: {str(e)}")
            return []
    
    def list_optimizations(self):
        """
        List all optimization suggestions
        """
        try:
            optimizations = OptimizationSuggestion.query.order_by(OptimizationSuggestion.created_at.desc()).all()
            return optimizations
        except Exception as e:
            logger.error(f"Error listing optimizations: {str(e)}")
            return []
    
    def list_ab_tests(self):
        """
        List all A/B tests
        """
        try:
            tests = ABTest.query.order_by(ABTest.start_date.desc()).all()
            return tests
        except Exception as e:
            logger.error(f"Error listing A/B tests: {str(e)}")
            return [] 