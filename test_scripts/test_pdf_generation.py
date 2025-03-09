#!/usr/bin/env python3
"""
Test script for PDF generation from markdown
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import from parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.file_parser import FileParser

def test_pdf_generation():
    """Test the markdown to PDF conversion"""
    # Sample markdown content
    markdown_content = """# Sample Resume

## John Doe
123 Main St, Anytown, USA
john.doe@email.com
555-123-4567

## Summary
Experienced software engineer with expertise in Python, JavaScript, and cloud technologies.
Passionate about building scalable web applications and using machine learning to solve real-world problems.

## Education
**Bachelor of Science in Computer Science**
University of Technology, 2015-2019

## Experience
**Senior Software Engineer**
Tech Company Inc., 2021-Present
- Developed and maintained RESTful APIs using Flask and Django
- Implemented CI/CD pipelines using GitHub Actions
- Optimized database queries resulting in 40% performance improvement

**Software Engineer**
Startup XYZ, 2019-2021
- Built responsive web applications using React and Redux
- Integrated third-party APIs for payment processing and social media
- Collaborated with cross-functional teams to deliver features on time

## Skills
1. Programming Languages: Python, JavaScript, TypeScript, SQL
2. Frameworks & Libraries: React, Django, Flask, Express.js
3. Tools & Technologies: Git, Docker, AWS, GCP
"""

    # Create the test_data directory if it doesn't exist
    os.makedirs("test_data", exist_ok=True)

    # Generate PDF
    try:
        print("Converting markdown to PDF...")
        pdf_bytes = FileParser.markdown_to_pdf(markdown_content)
        
        # Save the PDF to a file
        output_path = "test_data/test_resume.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
            
        print(f"PDF generated successfully at: {output_path}")
        print(f"PDF size: {len(pdf_bytes)} bytes")
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        
if __name__ == "__main__":
    test_pdf_generation() 