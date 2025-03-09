"""
Test script for enhanced PDF extraction using PyMuPDF (fitz) with caching

This script allows you to test PDF extraction and the caching mechanism.

Usage:
    python scripts/test_pdf_extraction.py path/to/sample.pdf [--no-cache] [--test-cache]
    
Options:
    --no-cache: Disable caching for the test
    --test-cache: Test cache performance by running extraction twice
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path
from flask import Flask

# Add parent directory to path to import from parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set up Flask app context for database operations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import after app is created
from extensions import db
from services.pdf_extractor import PDFExtractor
from models import PDFCache

# Initialize the database
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_extraction(pdf_path, use_cache=True, test_cache=False):
    """Test enhanced PDF extraction with PyMuPDF on a sample PDF file with optional caching"""
    logger.info(f"Testing PDF extraction on: {pdf_path}")
    logger.info(f"Cache enabled: {use_cache}")
    
    with app.app_context():
        # Initialize PDF extractor with specified cache setting
        pdf_extractor = PDFExtractor(use_cache=use_cache)
        
        # Read PDF file
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        # First extraction
        logger.info("Running first extraction...")
        start_time = time.time()
        try:
            result = pdf_extractor.extract_text(pdf_bytes)
            elapsed = time.time() - start_time
            logger.info(f"First extraction completed in {elapsed:.2f} seconds")
            logger.info(f"Result length: {len(result)}")
            logger.info(f"Extraction sample: {result[:500]}...")
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            return
        
        # Test cache if requested
        if test_cache and use_cache:
            logger.info("Testing cache with second extraction...")
            # Check current cache entries
            cache_count = PDFCache.query.count()
            logger.info(f"Current cache entries: {cache_count}")
            
            # Run second extraction which should hit the cache
            start_time = time.time()
            result2 = pdf_extractor.extract_text(pdf_bytes)
            elapsed = time.time() - start_time
            logger.info(f"Second extraction completed in {elapsed:.2f} seconds")
            
            # Verify results match
            if result == result2:
                logger.info("Cache verification: Results match ✓")
            else:
                logger.error("Cache verification: Results do not match ✗")
            
            # Show cache metrics
            content_hash = PDFCache.generate_hash(pdf_bytes)
            cache_entry = PDFCache.query.filter_by(content_hash=content_hash).first()
            if cache_entry:
                logger.info(f"Cache hit count: {cache_entry.hit_count}")
                logger.info(f"Cache entry created: {cache_entry.created_at}")
                logger.info(f"Cache entry last accessed: {cache_entry.last_accessed}")
        
        logger.info("PDF extraction test completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test PDF extraction with caching')
    parser.add_argument('pdf_path', help='Path to the PDF file to test')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching for the test')
    parser.add_argument('--test-cache', action='store_true', help='Test cache performance by running extraction twice')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found: {args.pdf_path}")
        sys.exit(1)
    
    test_extraction(args.pdf_path, use_cache=not args.no_cache, test_cache=args.test_cache) 