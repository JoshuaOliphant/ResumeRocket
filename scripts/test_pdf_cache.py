#!/usr/bin/env python3
"""
Test script for PDF caching functionality

This script specifically tests the PDF caching mechanism by:
1. Testing extraction with caching enabled vs disabled
2. Measuring performance difference between cached and uncached extractions
3. Verifying cache entries are correctly created and updated
4. Testing cache cleanup functionality

Usage:
    python scripts/test_pdf_cache.py [--cleanup] [--verbose]
    
Options:
    --cleanup: Force cache cleanup after tests
    --verbose: Show detailed information including extracted text samples
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path
from flask import Flask
from datetime import datetime, timedelta

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
print(f"Using database: {db_uri}")

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

def separator(title=""):
    """Print a separator line with optional title"""
    width = 80
    if title:
        padding = (width - len(title) - 4) // 2
        print("\n" + "=" * padding + f" {title} " + "=" * padding + "\n")
    else:
        print("\n" + "=" * width + "\n")

def test_extraction_performance(pdf_path, iterations=3):
    """Test performance difference between cached and uncached extractions"""
    separator("PERFORMANCE TEST")
    
    with app.app_context():
        # Read PDF file once
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        file_size = len(pdf_bytes) / 1024  # Size in KB
        logger.info(f"Testing with {pdf_path} ({file_size:.2f} KB)")
        
        # First, test without cache
        extractor_no_cache = PDFExtractor(use_cache=False)
        total_time_no_cache = 0
        
        logger.info("Testing extraction WITHOUT cache...")
        for i in range(iterations):
            start_time = time.time()
            result_no_cache = extractor_no_cache.extract_text(pdf_bytes)
            elapsed = time.time() - start_time
            logger.info(f"  Iteration {i+1}: {elapsed:.4f} seconds")
            total_time_no_cache += elapsed
        
        avg_time_no_cache = total_time_no_cache / iterations
        logger.info(f"Average extraction time WITHOUT cache: {avg_time_no_cache:.4f} seconds")
        
        # Now test with cache
        extractor_with_cache = PDFExtractor(use_cache=True)
        times_with_cache = []
        
        logger.info("Testing extraction WITH cache...")
        for i in range(iterations):
            start_time = time.time()
            result_with_cache = extractor_with_cache.extract_text(pdf_bytes)
            elapsed = time.time() - start_time
            logger.info(f"  Iteration {i+1}: {elapsed:.4f} seconds")
            times_with_cache.append(elapsed)
        
        # First iteration should be cache miss, subsequent should be hits
        first_time = times_with_cache[0]
        avg_cached_time = sum(times_with_cache[1:]) / (iterations - 1) if iterations > 1 else 0
        
        logger.info(f"First extraction (cache creation): {first_time:.4f} seconds")
        if iterations > 1:
            logger.info(f"Average extraction time WITH cache: {avg_cached_time:.4f} seconds")
            speedup = avg_time_no_cache / avg_cached_time if avg_cached_time > 0 else float('inf')
            logger.info(f"Cache speedup factor: {speedup:.2f}x faster")
        
        # Verify results match
        if result_no_cache == result_with_cache:
            logger.info("✅ Results match between cached and non-cached extraction")
        else:
            logger.error("❌ Results DO NOT match between cached and non-cached extraction")
        
        return result_with_cache

def test_cache_operations(pdf_path, verbose=False):
    """Test cache operations including creation, retrieval, and updates"""
    separator("CACHE OPERATIONS TEST")
    
    with app.app_context():
        # Clear any existing cache entries for this test
        content_hash = None
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            content_hash = PDFCache.generate_hash(pdf_bytes)
        
        existing = PDFCache.query.filter_by(content_hash=content_hash).first()
        if existing:
            logger.info(f"Clearing existing cache entry for {pdf_path}")
            db.session.delete(existing)
            db.session.commit()
        
        # Check initial cache state
        cache_count = PDFCache.query.count()
        logger.info(f"Current cache entries: {cache_count}")
        
        # Setup extractor with cache
        extractor = PDFExtractor(use_cache=True)
        
        # First extraction - should create cache entry
        logger.info("First extraction (should create new cache entry)...")
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            
            start_time = time.time()
            result1 = extractor.extract_text(pdf_bytes)
            elapsed1 = time.time() - start_time
            
            if verbose:
                logger.info(f"Extracted text sample: {result1[:200]}...")
        
        # Verify cache entry was created
        cache_entry = PDFCache.query.filter_by(content_hash=content_hash).first()
        if cache_entry:
            logger.info("✅ Cache entry created successfully")
            logger.info(f"  Creation time: {cache_entry.created_at}")
            logger.info(f"  Hit count: {cache_entry.hit_count}")
            logger.info(f"  File size: {cache_entry.file_size / 1024:.2f} KB")
            logger.info(f"  Page count: {cache_entry.page_count}")
        else:
            logger.error("❌ Failed to create cache entry")
            return
        
        # Second extraction - should hit cache
        logger.info("\nSecond extraction (should hit cache)...")
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            
            start_time = time.time()
            result2 = extractor.extract_text(pdf_bytes)
            elapsed2 = time.time() - start_time
        
        # Verify cache entry was updated
        cache_entry = PDFCache.query.filter_by(content_hash=content_hash).first()
        if cache_entry and cache_entry.hit_count > 1:
            logger.info("✅ Cache hit count updated successfully")
            logger.info(f"  Current hit count: {cache_entry.hit_count}")
            logger.info(f"  Last accessed: {cache_entry.last_accessed}")
        else:
            logger.error("❌ Cache hit count not updated properly")
        
        # Compare performance
        speedup = elapsed1 / elapsed2 if elapsed2 > 0 else float('inf')
        logger.info(f"\nFirst extraction time: {elapsed1:.4f} seconds")
        logger.info(f"Second extraction time: {elapsed2:.4f} seconds")
        logger.info(f"Speedup factor: {speedup:.2f}x faster with cache")

def test_cache_cleanup():
    """Test cache cleanup functionality"""
    separator("CACHE CLEANUP TEST")
    
    with app.app_context():
        # Get initial count
        initial_count = PDFCache.query.count()
        logger.info(f"Initial cache entries: {initial_count}")
        
        # First clean up any existing test entries
        PDFCache.query.filter(
            PDFCache.content_hash.like("test_%")
        ).delete()
        db.session.commit()
        
        # Create some old entries for testing cleanup
        logger.info("Creating test entries with old timestamps...")
        content = b"Test PDF content"
        
        # Create entries with old timestamps
        old_date = datetime.utcnow() - timedelta(days=40)
        for i in range(5):
            test_hash = f"test_old_{i}"
            cache_entry = PDFCache(
                content_hash=test_hash,
                extracted_text=f"Test content {i}",
                file_size=len(content),
                page_count=1,
                created_at=old_date,
                last_accessed=old_date,
                hit_count=1
            )
            db.session.add(cache_entry)
        
        # Create recent entries with higher hit counts
        for i in range(5):
            test_hash = f"test_recent_{i}"
            cache_entry = PDFCache(
                content_hash=test_hash,
                extracted_text=f"Test content {i}",
                file_size=len(content),
                page_count=1,
                hit_count=10
            )
            db.session.add(cache_entry)
        
        db.session.commit()
        
        # Verify test entries were created
        after_creation = PDFCache.query.count()
        logger.info(f"Cache entries after creating test data: {after_creation}")
        
        # Run cleanup
        logger.info("Running cache cleanup...")
        deleted_count = PDFCache.clean_old_entries(max_age_days=30, keep_min=5)
        logger.info(f"Deleted {deleted_count} old cache entries")
        
        # Verify old entries were removed
        remaining_old = PDFCache.query.filter(
            PDFCache.content_hash.like("test_old_%")
        ).count()
        
        remaining_recent = PDFCache.query.filter(
            PDFCache.content_hash.like("test_recent_%")
        ).count()
        
        logger.info(f"Remaining old test entries: {remaining_old}")
        logger.info(f"Remaining recent test entries: {remaining_recent}")
        
        if remaining_old == 0:
            logger.info("✅ Successfully removed old entries")
        else:
            logger.error("❌ Failed to remove all old entries")
            
        if remaining_recent == 5:
            logger.info("✅ Successfully kept recent entries")
        else:
            logger.error(f"❌ Unexpectedly removed recent entries")
        
        # Clean up test entries
        PDFCache.query.filter(
            PDFCache.content_hash.like("test_%")
        ).delete()
        db.session.commit()
        
        final_count = PDFCache.query.count()
        logger.info(f"Final cache entries: {final_count}")

def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description='Test PDF caching functionality')
    parser.add_argument('--cleanup', action='store_true', help='Force cache cleanup after tests')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    
    # Find test PDF files
    test_dir = Path(__file__).parent.parent / "test_data"
    test_pdfs = list(test_dir.glob("*.pdf"))
    
    if not test_pdfs:
        logger.error("No test PDF files found in test_data directory")
        return
    
    # Use the first PDF for testing
    test_pdf = str(test_pdfs[0])
    logger.info(f"Using test PDF: {test_pdf}")
    
    # Run tests
    test_cache_operations(test_pdf, verbose=args.verbose)
    separator()
    
    extracted_text = test_extraction_performance(test_pdf)
    separator()
    
    # Test cache cleanup
    test_cache_cleanup()
    
    # Force additional cleanup if requested
    if args.cleanup:
        separator("FORCED CLEANUP")
        with app.app_context():
            deleted = PDFCache.clean_old_entries(max_age_days=0, keep_min=0)
            logger.info(f"Forced cleanup: deleted {deleted} cache entries")

if __name__ == "__main__":
    main()