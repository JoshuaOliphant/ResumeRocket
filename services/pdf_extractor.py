import os
import io
import logging
from typing import Optional, Tuple
import tempfile

# Import unstructured libraries
from unstructured.partition.pdf import partition_pdf

logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    PDF extraction service using unstructured.io
    Provides local extraction using the unstructured library
    """
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Initialize the PDF extractor
        
        Args:
            api_key: Optional API key for unstructured.io API (not used in local extraction)
            api_url: Optional API URL for unstructured.io API (not used in local extraction)
        """
        self.api_key = api_key or os.environ.get("UNSTRUCTURED_API_KEY")
        self.api_url = api_url or os.environ.get("UNSTRUCTURED_API_URL")
        
        # Log initialization
        logger.info("Initialized PDF extractor with local extraction capabilities")
    
    def extract_text(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF using local unstructured library
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Extracted text as markdown string
        """
        try:
            logger.info("Extracting PDF text using local unstructured library")
            
            # Create a temporary file to write the PDF content
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(pdf_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Use unstructured's partition_pdf to extract content
                elements = partition_pdf(
                    filename=temp_file_path,
                    strategy="hi_res",  # Use high-resolution strategy for better results
                    infer_table_structure=True,  # Extract tables with structure
                )
                
                # Convert elements to text (not all elements have to_markdown method)
                markdown_lines = []
                for element in elements:
                    # Check if the element has text attribute
                    if hasattr(element, 'text'):
                        # Try to use to_markdown if available, otherwise use text
                        if hasattr(element, 'to_markdown') and callable(getattr(element, 'to_markdown')):
                            try:
                                markdown_lines.append(element.to_markdown())
                            except Exception:
                                markdown_lines.append(element.text)
                        else:
                            markdown_lines.append(element.text)
                
                markdown_content = "\n\n".join(markdown_lines)
                
                logger.info(f"Successfully extracted {len(elements)} elements from PDF")
                return markdown_content
                
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise Exception(f"Error extracting PDF text: {str(e)}") 