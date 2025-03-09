#!/usr/bin/env python3
"""
Benchmark for PDF caching performance with real-world PDFs

Usage:
    python scripts/bench_pdf_cache.py [pdf_path]
    
If no pdf_path is provided, the script will use a sample PDF from the test_data directory.
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path
from flask import Flask
from datetime import datetime

# Add parent directory to path to import from parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set up Flask app context for database operations
instance_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance')
os.makedirs(instance_path, exist_ok=True)

app = Flask(__name__)
db_name = 'resumerocket.db'
db_path = os.path.join(instance_path, db_name)
db_uri = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import after app is created
from extensions import db
from services.pdf_extractor import PDFExtractor
from models import PDFCache

# Initialize the database
db.init_app(app)

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def separator(title=None):
    """Print a separator line with optional title"""
    width = 70
    if title:
        print(f"\n{'=' * 5} {title} {'=' * (width - len(title) - 7)}\n")
    else:
        print("\n" + "=" * width + "\n")

def benchmark_pdf_extraction(pdf_path, iterations=5):
    """Benchmark PDF extraction with and without cache"""
    separator(f"BENCHMARKING {os.path.basename(pdf_path)}")
    
    # Calculate file size
    file_size_bytes = os.path.getsize(pdf_path)
    file_size_kb = file_size_bytes / 1024
    
    print(f"PDF Size: {file_size_kb:.2f} KB")
    
    with app.app_context():
        # Read PDF file
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            
        # Clear any existing cache for this PDF
        content_hash = PDFCache.generate_hash(pdf_bytes)
        existing = PDFCache.query.filter_by(content_hash=content_hash).first()
        if existing:
            print(f"Clearing existing cache entry")
            db.session.delete(existing)
            db.session.commit()
            
        # Benchmark without cache
        print("\nExtraction WITHOUT cache:")
        extractor_no_cache = PDFExtractor(use_cache=False)
        
        uncached_times = []
        for i in range(iterations):
            start_time = time.time()
            result = extractor_no_cache.extract_text(pdf_bytes)
            elapsed = time.time() - start_time
            uncached_times.append(elapsed)
            print(f"  Iteration {i+1}: {elapsed:.4f} seconds")
            
        avg_time_no_cache = sum(uncached_times) / len(uncached_times)
        print(f"\nAverage time WITHOUT cache: {avg_time_no_cache:.4f} seconds")
        
        # Benchmark with cache
        print("\nExtraction WITH cache:")
        extractor_with_cache = PDFExtractor(use_cache=True)
        
        # First run (cache miss)
        start_time = time.time()
        result = extractor_with_cache.extract_text(pdf_bytes)
        first_run_time = time.time() - start_time
        print(f"  First run (cache miss): {first_run_time:.4f} seconds")
        
        # Subsequent runs (cache hits)
        cached_times = []
        for i in range(iterations - 1):
            start_time = time.time()
            result = extractor_with_cache.extract_text(pdf_bytes)
            elapsed = time.time() - start_time
            cached_times.append(elapsed)
            print(f"  Run {i+2} (cache hit): {elapsed:.4f} seconds")
            
        if cached_times:
            avg_time_with_cache = sum(cached_times) / len(cached_times)
            print(f"\nAverage time WITH cache: {avg_time_with_cache:.4f} seconds")
            
            # Calculate speedup
            speedup = avg_time_no_cache / avg_time_with_cache
            print(f"Cache speedup: {speedup:.2f}x faster")
            
            # Verify cache entry
            cache_entry = PDFCache.query.filter_by(content_hash=content_hash).first()
            if cache_entry:
                print(f"\nCache entry details:")
                print(f"  Content hash: {cache_entry.content_hash[:10]}...")
                print(f"  File size: {cache_entry.file_size / 1024:.2f} KB")
                print(f"  Page count: {cache_entry.page_count}")
                print(f"  Hit count: {cache_entry.hit_count}")
                print(f"  Created: {cache_entry.created_at}")
                print(f"  Last accessed: {cache_entry.last_accessed}")

def find_sample_pdf():
    """Find a sample PDF in the test_data directory"""
    test_dir = Path(__file__).parent.parent / "test_data"
    test_pdfs = list(test_dir.glob("*.pdf"))
    
    if not test_pdfs:
        logger.error("No test PDF files found in test_data directory")
        return None
        
    return str(test_pdfs[0])

def main():
    """Main benchmark function"""
    parser = argparse.ArgumentParser(description='Benchmark PDF caching performance')
    parser.add_argument('pdf_path', nargs='?', help='Path to PDF file to benchmark')
    
    args = parser.parse_args()
    
    # Use provided PDF path or find a sample
    pdf_path = args.pdf_path or find_sample_pdf()
    
    if not pdf_path:
        print("Please provide a valid PDF file path")
        return
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return
        
    benchmark_pdf_extraction(pdf_path)

if __name__ == "__main__":
    main()