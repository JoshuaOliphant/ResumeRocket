"""
Test script for PDF extraction using unstructured.io

This script allows you to test local extraction using the unstructured library.

Usage:
    python scripts/test_pdf_extraction.py path/to/sample.pdf
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import from parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.pdf_extractor import PDFExtractor

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_extraction(pdf_path):
    """Test PDF extraction on a sample PDF file"""
    logger.info(f"Testing PDF extraction on: {pdf_path}")
    
    # Initialize PDF extractor
    pdf_extractor = PDFExtractor()
    
    # Read PDF file
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # Test extraction
    logger.info("Testing PDF extraction...")
    try:
        result = pdf_extractor.extract_text(pdf_bytes)
        logger.info(f"Extraction successful. Result length: {len(result)}")
        logger.info(f"Extraction sample: {result[:500]}...")
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
    
    logger.info("PDF extraction test completed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_pdf_extraction.py path/to/sample.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    test_extraction(pdf_path) 