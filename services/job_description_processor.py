import requests
import logging
import re
import os
from urllib.parse import quote

logger = logging.getLogger(__name__)

class JobDescriptionProcessor:
    def __init__(self):
        self.jina_api_key = os.environ.get('JINA_API_KEY')
        if not self.jina_api_key:
            raise ValueError('JINA_API_KEY environment variable must be set')

        self.headers = {
            'Authorization': f'Bearer {self.jina_api_key}'
        }

    def extract_from_url(self, url):
        """
        Extract job description from a given URL using Jina Reader API
        """
        try:
            # Properly encode the target URL and append it to Jina's base URL
            encoded_url = quote(url, safe='')
            jina_url = f"https://r.jina.ai/{encoded_url}"

            logger.debug(f"Sending request to Jina API for URL: {url}")
            response = requests.get(jina_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            content = response.text
            logger.debug(f"Received response from Jina API: {content[:200]}...")  # Log first 200 chars

            # Extract title and content from Jina's markdown response
            title_match = re.search(r'Title:\s*(.+?)(?:\n|$)', content)
            title = title_match.group(1) if title_match else "Job Posting"

            # Remove the Title and URL Source lines from content
            content_lines = content.split('\n')
            content_lines = [line for line in content_lines 
                           if not line.startswith('Title:') and 
                           not line.startswith('URL Source:')]
            cleaned_content = '\n'.join(content_lines).strip()

            return {
                'title': title,
                'content': cleaned_content,
                'url': url
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error extracting job description from URL {url}: {str(e)}")
            raise Exception(f"Failed to extract job description due to request error: {str(e)}")
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