# Lightweight PDF Extraction

This document describes the PDF extraction feature implemented in ResumeRocket using PyPDF2.

## Overview

The PDF extraction feature allows users to upload PDF resumes, which are then parsed and converted to a structured format for analysis and customization. The implementation uses the `PyPDF2` library to extract text content from PDFs efficiently.

## Implementation Details

### Dependencies

The following dependencies are required for PDF extraction:

- `pypdf2`: Used for basic PDF text extraction

### PDFExtractor Class

The `PDFExtractor` class in `services/pdf_extractor.py` provides the main functionality for PDF extraction:

```python
class PDFExtractor:
    """
    Lightweight PDF extraction service using PyPDF2
    """
    
    def __init__(self):
        """Initialize the PDF extractor"""
        # ...
    
    def extract_text(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF using PyPDF2"""
        # ...
```

The `extract_text` method takes PDF content as bytes and returns the extracted text as a formatted string with page markers. It uses PyPDF2's `PdfReader` and `extract_text()` method to extract text from each page.

### Integration with FileParser

The `PDFExtractor` is integrated with the existing `FileParser` class in `services/file_parser.py`, which handles various file formats including PDF, DOCX, and Markdown. When a PDF file is uploaded, the `FileParser` uses the `PDFExtractor` to extract the text content.

## Usage

### Extracting Text from a PDF

```python
from services.pdf_extractor import PDFExtractor

# Initialize the PDF extractor
pdf_extractor = PDFExtractor()

# Read PDF file
with open('path/to/resume.pdf', 'rb') as f:
    pdf_bytes = f.read()

# Extract text
text = pdf_extractor.extract_text(pdf_bytes)
```

### Testing

A test script is provided in `scripts/test_pdf_extraction.py` to test the PDF extraction functionality:

```bash
python scripts/test_pdf_extraction.py path/to/sample.pdf
```

## Future Improvements

- Implement caching mechanism to improve performance for large PDFs
- Add basic table detection and formatting
- Consider using pdfplumber for more complex PDFs if needed

## References

- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/) 