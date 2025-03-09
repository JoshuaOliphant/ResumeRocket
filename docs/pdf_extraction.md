# PDF Extraction with unstructured.io

This document describes the PDF extraction feature implemented in ResumeRocket using the unstructured.io library.

## Overview

The PDF extraction feature allows users to upload PDF resumes, which are then parsed and converted to a structured format for analysis and customization. The implementation uses the `unstructured` library to extract text content from PDFs while preserving the document structure.

## Implementation Details

### Dependencies

The following dependencies are required for PDF extraction:

- `unstructured[pdf]`: The core library for PDF extraction
- `pypdf2`: Used as a fallback for basic PDF text extraction
- System dependencies:
  - `tesseract`: For OCR (Optical Character Recognition)
  - `poppler`: For PDF rendering

### PDFExtractor Class

The `PDFExtractor` class in `services/pdf_extractor.py` provides the main functionality for PDF extraction:

```python
class PDFExtractor:
    """
    PDF extraction service using unstructured.io
    Provides local extraction using the unstructured library
    """
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """Initialize the PDF extractor"""
        # ...
    
    def extract_text(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF using local unstructured library"""
        # ...
```

The `extract_text` method takes PDF content as bytes and returns the extracted text as a markdown string. It uses the `partition_pdf` function from the `unstructured` library with the following parameters:

- `strategy="hi_res"`: Uses high-resolution strategy for better results
- `infer_table_structure=True`: Extracts tables with structure preserved

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

- Add support for unstructured.io API for enhanced extraction capabilities
- Implement caching mechanism to improve performance for large PDFs
- Add more advanced table extraction and formatting
- Improve handling of complex layouts and formatting

## References

- [unstructured.io Documentation](https://unstructured.io/docs)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/) 