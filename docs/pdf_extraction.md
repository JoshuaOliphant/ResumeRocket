# Enhanced PDF Extraction with PyMuPDF and Caching

This document describes the PDF extraction feature implemented in ResumeRocket using PyMuPDF (fitz), including the caching mechanism for improved performance.

## Overview

The PDF extraction feature allows users to upload PDF resumes, which are then parsed and converted to a structured format for analysis and customization. The implementation uses the `PyMuPDF` library to extract text content from PDFs with superior formatting retention, with a database-backed caching system to improve performance for large files and repeated processing.

## Implementation Details

### Dependencies

The following dependencies are required for PDF extraction:

- `pymupdf`: A high-performance PDF processing library for superior text extraction
- SQLAlchemy: For database caching

### PDFExtractor Class

The `PDFExtractor` class in `services/pdf_extractor.py` provides the main functionality for PDF extraction:

```python
class PDFExtractor:
    """
    Enhanced PDF extraction service using PyMuPDF (fitz) with caching support
    """
    
    def __init__(self, use_cache=True):
        """Initialize the PDF extractor with optional caching"""
        # ...
    
    def extract_text(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF using PyMuPDF, with caching"""
        # ...
```

The `extract_text` method takes PDF content as bytes and returns the extracted text as a formatted string with page markers. It first checks the cache for previously processed identical PDF files, and only performs extraction if needed.

### PDF Caching Mechanism

The caching system uses a database table to store extracted PDF content based on a hash of the PDF file contents:

1. **Caching Strategy**: PDF content is hashed using SHA-256 to create a unique identifier
2. **Cache Lookup**: Before processing, the system checks if the content hash exists in the cache
3. **Cache Storage**: After extraction, results are stored in the cache along with metadata (file size, page count, etc.)
4. **Cache Invalidation**: A periodic cleanup removes old and least-used entries to prevent unlimited growth
5. **Cache Statistics**: The system tracks usage metrics (hit count, last access time) for smart cleanup

### Integration with FileParser

The `PDFExtractor` is integrated with the existing `FileParser` class in `services/file_parser.py`, which handles various file formats including PDF, DOCX, and Markdown. When a PDF file is uploaded, the `FileParser` uses the `PDFExtractor` to extract the text content.

## Usage

### Extracting Text from a PDF with Caching

```python
from services.pdf_extractor import PDFExtractor

# Initialize the PDF extractor with caching enabled (default)
pdf_extractor = PDFExtractor(use_cache=True)

# Read PDF file
with open('path/to/resume.pdf', 'rb') as f:
    pdf_bytes = f.read()

# Extract text (uses cache if available)
text = pdf_extractor.extract_text(pdf_bytes)
```

### Disabling Cache for Specific Cases

```python
# Initialize without caching
pdf_extractor = PDFExtractor(use_cache=False)

# Extract text (always processes the PDF)
text = pdf_extractor.extract_text(pdf_bytes)
```

### Cache Maintenance

The PDFCache model includes a utility method to clean up old entries:

```python
from models import PDFCache

# Clean cache (keep recent/frequently used entries)
deleted_count = PDFCache.clean_old_entries(max_age_days=30, keep_min=100)
```

This is automatically called periodically by the PDFExtractor.

### Testing

A test script is provided in `scripts/test_pdf_extraction.py` to test the PDF extraction functionality:

```bash
python scripts/test_pdf_extraction.py path/to/sample.pdf
```

## Performance Benefits

The caching mechanism provides several benefits:

- **Reduced Processing Time**: Repeated processing of the same PDF file is eliminated
- **Lower CPU Usage**: Processing large PDFs is computationally expensive
- **Improved User Experience**: Faster response times for previously processed files
- **Reduced Memory Usage**: Avoids loading large PDFs into memory repeatedly

## Future Improvements

- Enhance table structure detection and formatting
- Add deeper document structure recognition (headings, sections, lists)
- Implement advanced layout analysis for multi-column resumes
- Consider structure detection with AI for complex formatting

## Advantages of PyMuPDF

PyMuPDF offers several advantages over the previously used PyPDF2:

1. **Superior Text Extraction**: Better preservation of text flow and formatting
2. **Performance**: 3-5x faster extraction speed for most documents
3. **Layout Analysis**: Better handling of columns, tables, and complex layouts
4. **Accuracy**: More reliable extraction, especially with complex PDFs
5. **Active Development**: Regular updates and bug fixes

## References

- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [MuPDF Project](https://mupdf.com/) 