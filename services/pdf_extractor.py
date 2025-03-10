import os
import io
import logging
import time
from typing import Optional, Tuple
import fitz  # PyMuPDF
from models import PDFCache

logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    Enhanced PDF extraction service using PyMuPDF (fitz) with caching support
    """
    
    def __init__(self, use_cache=True):
        """
        Initialize the PDF extractor
        
        Args:
            use_cache: Whether to use cache for PDF extraction (default: True)
        """
        self.use_cache = use_cache
        logger.info(f"Initialized enhanced PDF extractor with PyMuPDF (cache: {'enabled' if use_cache else 'disabled'})")
        
        # Periodically clean old cache entries (less than once per hour per instance)
        self._last_cache_cleanup = 0
    
    def extract_text(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF using PyMuPDF, with caching
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Extracted text as string
        """
        start_time = time.time()
        
        try:
            # Clean cache periodically (once per hour)
            self._maybe_clean_cache()
            
            # Try to get from cache first if caching is enabled
            if self.use_cache:
                cached_text = PDFCache.get_from_cache(pdf_bytes)
                if cached_text:
                    elapsed = time.time() - start_time
                    logger.info(f"Cache HIT! Retrieved PDF text from cache in {elapsed:.2f}s")
                    return cached_text
                    
                logger.debug("Cache MISS - Extracting PDF text using PyMuPDF")
            else:
                logger.debug("Cache disabled - Extracting PDF text using PyMuPDF")
            
            # Not in cache or cache disabled, extract text
            text, page_count = self._perform_extraction(pdf_bytes)
            
            # Store in cache if enabled
            if self.use_cache and text:
                PDFCache.add_to_cache(pdf_bytes, text, page_count)
                
            elapsed = time.time() - start_time
            logger.info(f"PDF text extraction completed in {elapsed:.2f}s")
            return text
                
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise Exception(f"Error extracting PDF text: {str(e)}")
    
    def _perform_extraction(self, pdf_bytes: bytes) -> Tuple[str, int]:
        """
        Perform the actual PDF text extraction using PyMuPDF
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Tuple of (extracted_text, page_count)
        """
        # Create a PyMuPDF document from the byte stream
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            page_count = len(doc)
            
            # Extract text from each page
            text_parts = []
            for i, page in enumerate(doc):
                # Get text with improved formatting preservation
                text = page.get_text("text")
                
                # Add additional formatting or structure if needed
                if text.strip():
                    # Just add the text without page markers that could confuse ATS systems
                    text_parts.append(text)
            
            # Join all text parts with double newlines
            content = "\n\n".join(text_parts)
            
            logger.info(f"Successfully extracted text from {page_count} PDF pages using PyMuPDF")
            return content, page_count
        
    def _maybe_clean_cache(self):
        """
        Periodically clean old cache entries (once per hour)
        """
        if not self.use_cache:
            return
            
        current_time = time.time()
        # Only clean up once per hour to avoid overhead
        if current_time - self._last_cache_cleanup > 3600:  # 3600 seconds = 1 hour
            try:
                deleted_count = PDFCache.clean_old_entries()
                if deleted_count > 0:
                    logger.info(f"Cache cleanup: removed {deleted_count} old cache entries")
                self._last_cache_cleanup = current_time
            except Exception as e:
                logger.warning(f"Cache cleanup failed: {str(e)}")
                # Don't retry too soon
                self._last_cache_cleanup = current_time - 3000 