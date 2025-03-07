import os
import io
import magic
import docx
import PyPDF2
from werkzeug.utils import secure_filename

class FileParser:
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
    ALLOWED_EXTENSIONS = {'md', 'docx', 'pdf'}
    ALLOWED_MIMETYPES = {
        'text/plain': 'md',             # For Markdown files
        'text/markdown': 'md',          # Alternative MIME type for Markdown
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/pdf': 'pdf'
    }

    @staticmethod
    def allowed_file(file):
        """Check if file type is allowed and size is within limit"""
        if not file:
            return False, "No file provided"

        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > FileParser.MAX_FILE_SIZE:
            return False, "File size exceeds 5MB limit"

        # Get filename and extension
        filename = secure_filename(file.filename)
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else None

        if extension not in FileParser.ALLOWED_EXTENSIONS:
            return False, f"File extension .{extension} not allowed"

        # Check file type using python-magic
        file_content = file.read()
        file.seek(0)
        mime_type = magic.from_buffer(file_content, mime=True)

        # Special handling for Markdown files
        if extension == 'md' and mime_type == 'text/plain':
            return True, None

        if mime_type not in FileParser.ALLOWED_MIMETYPES:
            return False, f"File type {mime_type} not allowed"

        # Verify extension matches MIME type
        if FileParser.ALLOWED_MIMETYPES[mime_type] != extension:
            return False, "File extension doesn't match its content type"

        return True, None

    @staticmethod
    def parse_to_markdown(file):
        """Parse different file types to markdown format"""
        try:
            # Get MIME type
            file_content = file.read()
            file.seek(0)
            mime_type = magic.from_buffer(file_content, mime=True)
            filename = secure_filename(file.filename)
            extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else None

            # Handle Markdown files (both text/plain and text/markdown)
            if extension == 'md' and mime_type == 'text/plain':
                return file.read().decode('utf-8')

            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                doc = docx.Document(io.BytesIO(file_content))
                markdown = []
                for para in doc.paragraphs:
                    if para.style.name.startswith('Heading'):
                        level = int(para.style.name[-1])
                        markdown.append(f"{'#' * level} {para.text}\n")
                    else:
                        markdown.append(f"{para.text}\n")
                return '\n'.join(markdown)

            elif mime_type == 'application/pdf':
                reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                markdown = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        markdown.append(text)
                return '\n\n'.join(markdown)

            else:
                raise ValueError(f"Unsupported file type: {mime_type}")

        except Exception as e:
            raise Exception(f"Error parsing file: {str(e)}")