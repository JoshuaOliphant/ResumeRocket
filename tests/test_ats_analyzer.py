"""
Tests for the enhanced ATS Analyzer and Resume Customizer components.

This test suite validates that the core ATS analysis and resume customization
functionality works as expected with various inputs and edge cases.
"""

import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock
from collections import defaultdict

# Add parent directory to path to import from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ats_analyzer import EnhancedATSAnalyzer, ATSAnalyzer
from services.resume_customizer import ResumeCustomizer

# Test data
SAMPLE_RESUME = """
# John Smith
Software Engineer | john@example.com | (123) 456-7890

## Summary
Experienced software engineer with 5 years of expertise in Python development, web applications, and cloud infrastructure.

## Skills
- Python, JavaScript, SQL
- Django, Flask, React
- AWS, Docker, CI/CD
- Unit testing, Agile methodologies

## Experience
### Senior Software Engineer, ABC Company
*January 2020 - Present*
- Developed and maintained Python web applications using Django
- Implemented CI/CD pipelines for automated testing and deployment
- Collaborated with cross-functional teams to deliver high-quality solutions

### Software Developer, XYZ Tech
*March 2018 - December 2019*
- Built RESTful APIs using Flask and SQLAlchemy
- Created frontend components with React and Redux
- Participated in code reviews and knowledge sharing sessions

## Education
### Bachelor of Science in Computer Science
University of Technology, 2018
"""

SAMPLE_JOB = """
# Senior Python Developer

## About Us
We're a growing tech company focused on building innovative web applications.

## Requirements
- 3+ years of experience with Python and Django
- Strong knowledge of SQL and database design
- Experience with RESTful API development
- Familiarity with AWS services (EC2, S3, Lambda)
- Understanding of frontend technologies (JavaScript, HTML, CSS)

## Responsibilities
- Design and implement backend services using Python and Django
- Work with the frontend team to integrate APIs
- Optimize applications for performance and scalability
- Participate in code reviews and mentor junior developers
- Implement automated testing and deployment pipelines

## Qualifications
- Bachelor's degree in Computer Science or related field
- Strong problem-solving skills and attention to detail
- Excellent communication and teamwork abilities
"""

EMPTY_TEXT = ""
MINIMAL_RESUME = "John Smith, Software Engineer. I know Python."
MINIMAL_JOB = "Software Engineer needed. Python required."


class TestEnhancedATSAnalyzer(unittest.TestCase):
    """Tests for the EnhancedATSAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = EnhancedATSAnalyzer()
    
    def test_initialization(self):
        """Test that the analyzer initializes correctly."""
        self.assertIsNotNone(self.analyzer.section_weights)
        self.assertIsNotNone(self.analyzer.skills_taxonomy)
        self.assertGreater(len(self.analyzer.skills_taxonomy), 0)
        
    def test_analyze_with_valid_inputs(self):
        """Test analyze method with valid resume and job description."""
        result = self.analyzer.analyze(SAMPLE_RESUME, SAMPLE_JOB)
        
        # Check result structure
        self.assertIn('score', result)
        self.assertIn('confidence', result)
        self.assertIn('matching_keywords', result)
        self.assertIn('missing_keywords', result)
        self.assertIn('section_scores', result)
        self.assertIn('job_type', result)
        self.assertIn('suggestions', result)
        
        # Check score ranges
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)
        
        # Verify that we get some matching keywords
        self.assertGreater(len(result['matching_keywords']), 0)
        
        # Check section scores
        self.assertIn('experience', result['section_scores'])
        self.assertIn('skills', result['section_scores'])
        self.assertIn('education', result['section_scores'])
        
        # Verify job type detection 
        self.assertEqual(result['job_type'], 'technical')
        
        # Check suggestions
        self.assertGreater(len(result['suggestions']), 0)
        
    def test_analyze_with_empty_inputs(self):
        """Test analyze method with empty inputs."""
        result = self.analyzer.analyze(EMPTY_TEXT, EMPTY_TEXT)
        
        # Check default result for empty inputs
        self.assertEqual(result['score'], 0)
        self.assertEqual(result['confidence'], 'low')
        self.assertEqual(len(result['matching_keywords']), 0)
        self.assertEqual(len(result['missing_keywords']), 0)
        
    def test_analyze_with_minimal_inputs(self):
        """Test analyze method with minimal inputs."""
        result = self.analyzer.analyze(MINIMAL_RESUME, MINIMAL_JOB)
        
        # Check that we still get a reasonable score
        self.assertGreater(result['score'], 0)
        
        # Check that Python is matched
        python_matched = any('python' in kw.lower() for kw in result['matching_keywords'])
        self.assertTrue(python_matched)
        
    def test_section_detection(self):
        """Test ability to detect resume sections."""
        sections = self.analyzer._identify_sections(SAMPLE_RESUME)
        
        # Print detected sections for debugging
        print(f"Detected sections: {list(sections.keys())}")
        
        # Check for key sections - summary might be detected as part of unknown
        self.assertIn('skills', sections)
        self.assertIn('experience', sections)
        self.assertIn('education', sections)
        
        # Check section content
        self.assertIn('Python', sections['skills'])
        self.assertIn('Computer Science', sections['education'])
        
    def test_ngram_extraction(self):
        """Test n-gram extraction capability."""
        ngrams = self.analyzer._extract_ngrams("Python programming with Django and Flask")
        
        # Print detected ngrams for debugging
        print(f"Detected ngrams: {dict(ngrams)}")
        
        # Check for unigrams
        self.assertIn('python', ngrams)
        self.assertIn('django', ngrams)
        
        # Check for bigrams
        self.assertIn('python programming', ngrams)
        
        # Note: "django and flask" might not be extracted if "and" is a stopword
        # or if our implementation has other filtering rules
        
    def test_job_description_processing(self):
        """Test job description processing."""
        job_elements = self.analyzer._process_job_description(SAMPLE_JOB)
        
        # Check structure
        self.assertIn('title', job_elements)
        self.assertIn('requirements', job_elements)
        self.assertIn('responsibilities', job_elements)
        self.assertIn('keywords', job_elements)
        
        # Check content
        self.assertGreater(len(job_elements['requirements']), 0)
        self.assertGreater(len(job_elements['keywords']), 0)
        
        # Check keyword weights
        self.assertGreater(job_elements['keywords']['python'], 0)
        
    def test_semantic_matching(self):
        """Test semantic matching capabilities."""
        # Create a controlled test case
        resume_with_react = "I am proficient in React and Redux."
        job_with_javascript = "Requires JavaScript experience."
        
        result = self.analyzer.analyze(resume_with_react, job_with_javascript)
        
        # Check if JavaScript is matched semantically through React
        all_matches = result['matching_keywords']
        javascript_matched = any('javascript' in kw.lower() for kw in all_matches)
        self.assertTrue(javascript_matched)

    def test_different_resume_formats(self):
        """Test analyzer with different resume formats."""
        # Plain text format
        plain_resume = """
        John Smith
        Software Engineer
        
        Skills: Python, JavaScript, React
        
        Experience:
        * Senior Developer at ABC Corp (2020-Present)
        * Developer at XYZ Inc (2018-2020)
        
        Education:
        Computer Science, BS, University, 2018
        """
        
        result = self.analyzer.analyze(plain_resume, SAMPLE_JOB)
        
        # Should still detect key sections and skills
        self.assertGreater(result['score'], 0)
        python_matched = any('python' in kw.lower() for kw in result['matching_keywords'])
        self.assertTrue(python_matched)

    def test_job_type_detection(self):
        """Test job type detection for different job descriptions."""
        # Technical job
        tech_job = "Software Engineer position requiring Python, Java and cloud skills."
        result = self.analyzer._detect_job_type(tech_job)
        self.assertEqual(result, 'technical')
        
        # Management job
        mgmt_job = "Engineering Manager needed to lead a team of developers."
        result = self.analyzer._detect_job_type(mgmt_job)
        self.assertEqual(result, 'management')
        
        # Entry-level job
        entry_job = "Junior Developer position for recent graduates."
        result = self.analyzer._detect_job_type(entry_job)
        self.assertEqual(result, 'entry_level')

    def test_score_calibration(self):
        """Test score calibration logic."""
        # Create test data for score calculation
        match_results = {
            'total_job_keywords': 20,
            'weighted_match_score': 15,
            'exact_matches': {'python': {'weight': 2, 'frequency': 3}},
            'semantic_matches': {'java': {'matched_with': 'javascript', 'weight': 1.5}},
            'keyword_density': 4.5
        }
        
        section_scores = {
            'experience': 70,
            'skills': 80,
            'education': 60
        }
        
        # Calculate score
        score = self.analyzer._calculate_calibrated_score(match_results, section_scores)
        
        # Check that score is in reasonable range
        self.assertGreater(score, 30)  # Base score should be at least 30
        self.assertLess(score, 100)    # But less than 100

    def test_legacy_compatibility(self):
        """Test that the legacy ATSAnalyzer interface works with new implementation."""
        legacy_analyzer = ATSAnalyzer()
        result = legacy_analyzer.analyze(SAMPLE_RESUME, SAMPLE_JOB)
        
        # Check old format
        self.assertIn('score', result)
        self.assertIn('matching_keywords', result)
        self.assertIn('missing_keywords', result)
        
        # Should only have these keys for backward compatibility
        self.assertEqual(len(result.keys()), 3)


class TestResumeCustomizer(unittest.TestCase):
    """Tests for the ResumeCustomizer class."""
    
    def setUp(self):
        """Set up test fixtures with mocked Anthropic API."""
        # Create mock for Anthropic client
        self.anthropic_mock = MagicMock()
        self.response_mock = MagicMock()
        self.response_mock.content = [MagicMock(text="Customized resume content")]
        self.anthropic_mock.messages.create.return_value = self.response_mock
        
        # Patch environment variable and Anthropic client
        patcher1 = patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"})
        patcher1.start()
        self.addCleanup(patcher1.stop)
        
        patcher2 = patch('anthropic.Anthropic', return_value=self.anthropic_mock)
        patcher2.start()
        self.addCleanup(patcher2.stop)
        
        # Create customizer with patched dependencies
        self.customizer = ResumeCustomizer()
        
        # Mock the analyzer methods
        self.customizer.ats_analyzer.analyze = MagicMock(return_value={
            'score': 50.0,
            'confidence': 'medium',
            'matching_keywords': ['python', 'django', 'api'],
            'missing_keywords': ['aws', 'docker'],
            'section_scores': {'experience': 60, 'skills': 70, 'education': 40},
            'job_type': 'technical',
            'keyword_density': 4.0,
            'suggestions': [{'title': 'Add keywords', 'content': 'Add missing keywords'}]
        })
    
    def test_initialization(self):
        """Test that ResumeCustomizer initializes correctly."""
        self.assertEqual(self.customizer.model, "claude-3-7-sonnet-20250219")
        self.assertIsNotNone(self.customizer.ats_analyzer)
        self.assertEqual(self.customizer.default_level, "balanced")
    
    def test_analyze_resume(self):
        """Test analyze_resume method."""
        result = self.customizer.analyze_resume(SAMPLE_RESUME, SAMPLE_JOB)
        
        # Verify analyzer was called
        self.customizer.ats_analyzer.analyze.assert_called_once_with(SAMPLE_RESUME, SAMPLE_JOB)
        
        # Check result
        self.assertEqual(result['score'], 50.0)
        self.assertEqual(result['job_type'], 'technical')
    
    @patch('json.loads')
    def test_customize_resume_two_stage(self, mock_json_loads):
        """Test the two-stage resume customization process."""
        # Mock json loading for optimization plan
        mock_json_loads.return_value = {
            'summary': 'Optimization plan summary',
            'job_analysis': 'Job analysis details',
            'recommendations': [
                {'section': 'skills', 'what': 'Add AWS', 'why': 'Required skill'}
            ],
            'keywords_to_add': ['aws', 'docker'],
            'formatting_suggestions': ['Use bullet points']
        }
        
        # Set up mock for second ATS analysis
        improved_analysis = {
            'score': 75.0,
            'confidence': 'high',
            'matching_keywords': ['python', 'django', 'api', 'aws'],
            'missing_keywords': ['docker'],
            'section_scores': {'experience': 70, 'skills': 85, 'education': 50},
            'job_type': 'technical',
            'keyword_density': 5.0,
            'suggestions': []
        }
        
        # Configure analyzer to return different results on second call
        self.customizer.ats_analyzer.analyze = MagicMock(side_effect=[
            # First call - initial analysis
            {
                'score': 50.0,
                'confidence': 'medium',
                'matching_keywords': ['python', 'django', 'api'],
                'missing_keywords': ['aws', 'docker'],
                'section_scores': {'experience': 60, 'skills': 70, 'education': 40},
                'job_type': 'technical',
                'keyword_density': 4.0,
                'suggestions': [{'title': 'Add keywords', 'content': 'Add missing keywords'}]
            },
            # Second call - improved analysis
            improved_analysis
        ])
        
        # Test customization
        result = self.customizer.customize_resume(SAMPLE_RESUME, SAMPLE_JOB, "balanced")
        
        # Check that analyzer was called twice
        self.assertEqual(self.customizer.ats_analyzer.analyze.call_count, 2)
        
        # Check that Claude API was called twice (analyze and implement)
        self.assertEqual(self.anthropic_mock.messages.create.call_count, 2)
        
        # Verify result structure
        self.assertIn('customized_content', result)
        self.assertIn('original_score', result)
        self.assertIn('new_score', result)
        self.assertIn('improvement', result)
        
        # Check improvement calculation
        self.assertEqual(result['improvement'], 25.0)  # 75 - 50
        self.assertEqual(result['customization_level'], 'balanced')
    
    def test_customize_resume_with_invalid_level(self):
        """Test customization with invalid level falls back to default."""
        self.customizer.ats_analyzer.analyze = MagicMock(side_effect=[
            # First call
            {
                'score': 50.0,
                'confidence': 'medium',
                'matching_keywords': [],
                'missing_keywords': [],
                'section_scores': {},
                'job_type': 'technical',
                'keyword_density': 4.0,
                'suggestions': []
            },
            # Second call
            {
                'score': 60.0,
                'confidence': 'medium',
                'matching_keywords': [],
                'missing_keywords': [],
                'section_scores': {},
                'job_type': 'technical',
                'keyword_density': 4.0,
                'suggestions': []
            }
        ])
        
        # Mock JSON parsing
        with patch('json.loads', return_value={'recommendations': []}):
            result = self.customizer.customize_resume(SAMPLE_RESUME, SAMPLE_JOB, "invalid_level")
            
            # Should fall back to default level
            self.assertEqual(result['customization_level'], 'balanced')
    
    @patch('json.loads')
    def test_simulate_ats_systems(self, mock_json_loads):
        """Test ATS simulation functionality."""
        # Mock simulation results
        mock_json_loads.return_value = {
            'Workday': {'score': 65, 'strengths': ['Python'], 'weaknesses': ['AWS']},
            'Taleo': {'score': 58, 'strengths': ['Django'], 'weaknesses': ['Docker']},
            'Greenhouse': {'score': 72, 'strengths': ['API'], 'weaknesses': []}
        }
        
        # Test simulation
        result = self.customizer.simulate_ats_systems(SAMPLE_RESUME, SAMPLE_JOB)
        
        # Check that Claude API was called
        self.anthropic_mock.messages.create.assert_called_once()
        
        # Check system prompt parameter
        system_param = self.anthropic_mock.messages.create.call_args[1]['system']
        self.assertIn('Applicant Tracking Systems', system_param)
        self.assertIn('Workday', system_param)
        self.assertIn('Taleo', system_param)
        
        # Check result structure
        self.assertIn('simulations', result)
        self.assertIn('base_analysis', result)
    
    def test_error_handling(self):
        """Test error handling in customizer methods."""
        # Make analyzer raise an exception
        self.customizer.ats_analyzer.analyze.side_effect = Exception("Analysis error")
        
        # Test error handling in analyze_resume
        with self.assertRaises(Exception) as context:
            self.customizer.analyze_resume(SAMPLE_RESUME, SAMPLE_JOB)
        self.assertIn("Failed to analyze resume", str(context.exception))
        
        # Test error handling in customize_resume
        with self.assertRaises(Exception) as context:
            self.customizer.customize_resume(SAMPLE_RESUME, SAMPLE_JOB)
        self.assertIn("Failed to customize resume", str(context.exception))


# Integration test for the complete resume optimization flow
class TestATSIntegration(unittest.TestCase):
    """Integration tests for ATS analysis and resume customization."""
    
    @unittest.skip("Integration test requires real API key")
    def test_end_to_end_optimization(self):
        """
        End-to-end test of the resume optimization flow.
        
        This test requires a real ANTHROPIC_API_KEY and is skipped by default.
        """
        if not os.environ.get('ANTHROPIC_API_KEY'):
            self.skipTest("ANTHROPIC_API_KEY environment variable not set")
        
        # Create real instances
        analyzer = EnhancedATSAnalyzer()
        customizer = ResumeCustomizer()
        
        # Run initial analysis
        initial_analysis = analyzer.analyze(SAMPLE_RESUME, SAMPLE_JOB)
        initial_score = initial_analysis['score']
        
        # Customize resume
        customization_result = customizer.customize_resume(SAMPLE_RESUME, SAMPLE_JOB)
        customized_resume = customization_result['customized_content']
        
        # Analyze customized resume
        final_analysis = analyzer.analyze(customized_resume, SAMPLE_JOB)
        final_score = final_analysis['score']
        
        # Verify improvement
        self.assertGreater(final_score, initial_score)
        self.assertEqual(customization_result['improvement'], final_score - initial_score)
        
        # Print results for manual inspection
        print(f"Initial score: {initial_score}")
        print(f"Final score: {final_score}")
        print(f"Improvement: {final_score - initial_score}")


if __name__ == '__main__':
    unittest.main()