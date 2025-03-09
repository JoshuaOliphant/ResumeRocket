import os
import io
import logging
from typing import Optional
import PyPDF2

logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    Lightweight PDF extraction service using PyPDF2
    """
    
    def __init__(self):
        """
        Initialize the PDF extractor
        """
        logger.info("Initialized lightweight PDF extractor with PyPDF2")
    
    def extract_text(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF using PyPDF2
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Extracted text as string
        """
        try:
            logger.info("Extracting PDF text using PyPDF2")
            
            # Create a PyPDF2 reader from the byte stream
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            
            # Extract text from each page
            text_parts = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    # Add a page header and the extracted text
                    text_parts.append(f"## Page {i+1}\n\n{text}")
            
            # Join all text parts with double newlines
            content = "\n\n".join(text_parts)
            
            logger.info(f"Successfully extracted text from {len(reader.pages)} PDF pages")
            return content
                
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise Exception(f"Error extracting PDF text: {str(e)}") 