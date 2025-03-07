import requests
from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)

class JobDescriptionProcessor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def extract_from_url(self, url):
        """
        Extract job description from a given URL
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()

            # Try to find the job title
            title = None
            title_candidates = [
                soup.find('h1'),  # Most common location for job titles
                soup.find('title'),
                soup.find(class_=re.compile(r'job.*title', re.I)),
                soup.find(id=re.compile(r'job.*title', re.I))
            ]
            
            for candidate in title_candidates:
                if candidate and candidate.text.strip():
                    title = candidate.text.strip()
                    break

            # Try to find the main job description content
            content = None
            content_candidates = [
                soup.find(class_=re.compile(r'job.*description', re.I)),
                soup.find(id=re.compile(r'job.*description', re.I)),
                soup.find(class_=re.compile(r'description', re.I)),
                soup.find('article'),
                soup.find('main')
            ]

            for candidate in content_candidates:
                if candidate and candidate.text.strip():
                    content = candidate.text.strip()
                    break

            if not content:
                # Fallback to body content if no specific job description found
                content = soup.body.text.strip()

            # Clean up the content
            content = re.sub(r'\s+', ' ', content)  # Replace multiple spaces with single space
            content = re.sub(r'\n\s*\n', '\n\n', content)  # Remove multiple empty lines

            if not title:
                title = "Job Posting"  # Default title if none found

            return {
                'title': title,
                'content': content,
                'url': url
            }

        except Exception as e:
            logger.error(f"Error extracting job description from URL {url}: {str(e)}")
            raise Exception(f"Failed to extract job description: {str(e)}")

    def process_text(self, text, title=None):
        """
        Process raw text job description
        """
        try:
            # Clean up the text
            cleaned_text = re.sub(r'\s+', ' ', text).strip()
            
            # If no title provided, try to extract from first line
            if not title:
                lines = cleaned_text.split('\n')
                if lines:
                    title = lines[0].strip()
                    # If first line is short enough, use it as title
                    if len(title) <= 200:
                        cleaned_text = '\n'.join(lines[1:]).strip()
                    else:
                        title = "Job Posting"

            return {
                'title': title,
                'content': cleaned_text
            }

        except Exception as e:
            logger.error(f"Error processing job description text: {str(e)}")
            raise Exception(f"Failed to process job description: {str(e)}")
