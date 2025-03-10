#!/usr/bin/env python3
"""
Manual testing script for ATS enhancement features.
This script allows you to test the enhanced ATS analyzer and resume customizer with real data.

Usage:
    python test_ats_enhancement.py [--analyze-only] [--resume RESUME_PATH] [--job JOB_PATH]

Example:
    python test_ats_enhancement.py --analyze-only --resume ../test_data/sample_resume.pdf --job job_description.txt
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Add parent directory to path to import from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ats_analyzer import EnhancedATSAnalyzer
from services.resume_customizer import ResumeCustomizer
from services.file_parser import FileParser


def read_file_content(file_path):
    """Read content from a file, handling different file types."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    
    # Use FileParser if it's a PDF, DOCX, etc.
    if file_path.lower().endswith(('.pdf', '.docx')):
        try:
            parser = FileParser()
            content = parser.extract_text(file_path)
            return content
        except Exception as e:
            print(f"Error extracting content from {file_path}: {str(e)}")
            sys.exit(1)
    else:
        # Assume it's a text file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
            sys.exit(1)


def analyze_resume(resume_content, job_content):
    """Analyze resume against job description."""
    print("\n===== ANALYZING RESUME =====")
    analyzer = EnhancedATSAnalyzer()
    
    print("Running analysis...")
    start_time = datetime.now()
    result = analyzer.analyze(resume_content, job_content)
    end_time = datetime.now()
    print(f"Analysis completed in {(end_time - start_time).total_seconds():.2f} seconds")
    
    # Print key results
    print(f"\nOverall Score: {result.get('score', 0):.2f}/100")
    print(f"Confidence: {result.get('confidence', 'unknown')}")
    print(f"Job Type: {result.get('job_type', 'unknown')}")
    print(f"Keyword Density: {result.get('keyword_density', 0):.2f}%")
    
    print("\nMatching Keywords:")
    for kw in result.get('matching_keywords', [])[:10]:
        print(f"- {kw}")
    
    print("\nMissing Keywords:")
    for kw in result.get('missing_keywords', [])[:10]:
        print(f"- {kw}")
    
    print("\nSection Scores:")
    for section, score in result.get('section_scores', {}).items():
        print(f"- {section.title()}: {score:.2f}/100")
    
    print("\nSuggestions:")
    for suggestion in result.get('suggestions', []):
        print(f"- {suggestion.get('title')}: {suggestion.get('content')}")
    
    return result


def customize_resume(resume_content, job_content):
    """Customize resume for the job description."""
    print("\n===== CUSTOMIZING RESUME =====")
    customizer = ResumeCustomizer()
    
    # Check API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set this variable to run customization")
        return None
    
    print("Running initial analysis...")
    analysis = customizer.analyze_resume(resume_content, job_content)
    print(f"Initial score: {analysis.get('score', 0):.2f}/100")
    
    print("\nStarting two-stage customization process...")
    print("Stage 1: Analyzing and planning improvements...")
    start_time = datetime.now()
    result = customizer.customize_resume(resume_content, job_content)
    end_time = datetime.now()
    print(f"Customization completed in {(end_time - start_time).total_seconds():.2f} seconds")
    
    # Print key results
    print(f"\nOriginal Score: {result.get('original_score', 0):.2f}/100")
    print(f"New Score: {result.get('new_score', 0):.2f}/100")
    print(f"Improvement: {result.get('improvement', 0):.2f} points")
    print(f"Confidence: {result.get('confidence', 'unknown')}")
    
    # Save output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save customized resume
    customized_file = f"customized_resume_{timestamp}.md"
    with open(customized_file, 'w', encoding='utf-8') as f:
        f.write(result.get('customized_content', ''))
    print(f"\nCustomized resume saved to: {customized_file}")
    
    # Save optimization plan
    plan_file = f"optimization_plan_{timestamp}.json"
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(result.get('optimization_plan', {}), f, indent=2)
    print(f"Optimization plan saved to: {plan_file}")
    
    return result


def simulate_ats_systems(resume_content, job_content):
    """Simulate how different ATS systems would process the resume."""
    print("\n===== SIMULATING ATS SYSTEMS =====")
    customizer = ResumeCustomizer()
    
    # Check API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set this variable to run ATS simulation")
        return None
    
    print("Running ATS simulation...")
    start_time = datetime.now()
    result = customizer.simulate_ats_systems(resume_content, job_content)
    end_time = datetime.now()
    print(f"Simulation completed in {(end_time - start_time).total_seconds():.2f} seconds")
    
    # Print simulation results
    if 'error' in result:
        print(f"Error: {result.get('error')}")
        return None
    
    print("\nATS Simulation Results:")
    for ats_name, ats_data in result.get('simulations', {}).items():
        print(f"\n{ats_name}:")
        print(f"  Score: {ats_data.get('score', 0)}/100")
        
        print("  Strengths:")
        for strength in ats_data.get('strengths', []):
            print(f"    - {strength}")
        
        print("  Weaknesses:")
        for weakness in ats_data.get('weaknesses', []):
            print(f"    - {weakness}")
        
        print("  Recommendations:")
        for rec in ats_data.get('recommendations', []):
            print(f"    - {rec}")
    
    # Save simulation results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sim_file = f"ats_simulation_{timestamp}.json"
    with open(sim_file, 'w', encoding='utf-8') as f:
        json.dump(result.get('simulations', {}), f, indent=2)
    print(f"\nSimulation results saved to: {sim_file}")
    
    return result


def main():
    """Main function to run the test."""
    parser = argparse.ArgumentParser(description='Test ATS enhancement features')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze, don\'t customize')
    parser.add_argument('--resume', default='../test_data/sample_resume.pdf', help='Path to resume file')
    parser.add_argument('--job', default='../test_data/sample_job.txt', help='Path to job description file')
    
    args = parser.parse_args()
    
    print("=== ATS Enhancement Testing ===")
    print(f"Resume file: {args.resume}")
    print(f"Job description file: {args.job}")
    
    # Read content from files
    resume_content = read_file_content(args.resume)
    job_content = read_file_content(args.job)
    
    print(f"Resume length: {len(resume_content)} characters")
    print(f"Job description length: {len(job_content)} characters")
    
    # Always run analysis
    analysis_result = analyze_resume(resume_content, job_content)
    
    # Run customization if not analyze-only
    if not args.analyze_only:
        customization_result = customize_resume(resume_content, job_content)
        
        # Run ATS simulation
        print("\nDo you want to run ATS simulation? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            simulation_result = simulate_ats_systems(resume_content, job_content)
    
    print("\nTesting completed.")


if __name__ == "__main__":
    main()