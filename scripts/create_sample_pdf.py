"""
Script to create a sample PDF file for testing
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_sample_pdf(input_text_path, output_pdf_path):
    """Create a PDF file from a text file"""
    # Read the text file
    with open(input_text_path, "r") as f:
        content = f.read()
    
    # Create a PDF document
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get default styles
    styles = getSampleStyleSheet()
    
    # Process text and build flowables
    flowables = []
    lines = content.split('\n')
    
    for line in lines:
        if not line.strip():
            # Add space for empty lines
            flowables.append(Spacer(1, 12))
        elif line.strip().upper() == line.strip() and len(line.strip()) > 3:
            # Assume section headings are uppercase
            flowables.append(Paragraph(f"<b>{line}</b>", styles['Heading2']))
        else:
            # Regular text
            flowables.append(Paragraph(line, styles['Normal']))
    
    # Build the PDF
    doc.build(flowables)
    print(f"Created PDF file: {output_pdf_path}")

if __name__ == "__main__":
    # Create the test_data directory if it doesn't exist
    os.makedirs("test_data", exist_ok=True)
    
    # Create a sample text file if it doesn't exist
    sample_text_path = "test_data/sample.txt"
    if not os.path.exists(sample_text_path):
        with open(sample_text_path, "w") as f:
            f.write("""Sample Resume

John Doe
123 Main St, Anytown, USA
john.doe@email.com
555-123-4567

SUMMARY
Experienced software engineer with expertise in Python, JavaScript, and cloud technologies.
Passionate about building scalable web applications and using machine learning to solve real-world problems.

EDUCATION
Bachelor of Science in Computer Science
University of Technology, 2015-2019

EXPERIENCE
Senior Software Engineer
Tech Company Inc., 2021-Present
- Developed and maintained RESTful APIs using Flask and Django
- Implemented CI/CD pipelines using GitHub Actions
- Optimized database queries resulting in 40% performance improvement

Software Engineer
Startup XYZ, 2019-2021
- Built responsive web applications using React and Redux
- Integrated third-party APIs for payment processing and social media
- Collaborated with cross-functional teams to deliver features on time

SKILLS
Programming Languages: Python, JavaScript, TypeScript, SQL
Frameworks & Libraries: React, Django, Flask, Express.js
Tools & Technologies: Git, Docker, AWS, GCP
""")
    
    # Create the PDF
    create_sample_pdf(sample_text_path, "test_data/sample_resume.pdf") 