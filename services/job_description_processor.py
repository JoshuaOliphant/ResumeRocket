import requests
import logging
import re
import os

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
            logger.debug(f"Attempting to extract content from URL: {url}")

            # Use Jina API to extract content
            logger.debug(f"Using Jina API to extract content from: {url}")
            jina_url = f"https://r.jina.ai/{url}"
            logger.debug(f"Sending request to Jina API with URL: {jina_url}")

            response = requests.get(jina_url, headers=self.headers, timeout=30)
            response.raise_for_status()

            content = response.text
            logger.debug(f"Received response from Jina API: {content[:200]}...")

            # Extract title and content
            title_match = re.search(r'Title:\s*(.+?)(?:\n|$)', content)
            title = title_match.group(1) if title_match else "Job Posting"

            # Split content into lines
            content_lines = content.split('\n')

            # Get content after "Markdown Content:" marker
            try:
                markdown_start = content_lines.index('Markdown Content:')
                content_lines = content_lines[markdown_start + 1:]
                logger.debug("Found Markdown Content marker in Jina response")
            except ValueError:
                logger.warning("Markdown Content marker not found in Jina response")
                # Remove header lines
                content_lines = [line for line in content_lines 
                               if not line.startswith('Title:') and 
                               not line.startswith('URL Source:')]

            # Clean up the content
            cleaned_content = []
            for line in content_lines:
                # Skip image lines
                if line.startswith('![') or line.startswith('[!['):
                    continue
                # Remove markdown links but keep the text
                line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line)
                # Remove multiple spaces and newlines
                line = re.sub(r'\s+', ' ', line).strip()
                if line:
                    cleaned_content.append(line)

            cleaned_content = '\n'.join(cleaned_content).strip()

            if not cleaned_content:
                raise Exception("No content was extracted from the job posting URL")

            logger.debug(f"Extracted title from Jina: {title}")
            logger.debug(f"Extracted content length from Jina: {len(cleaned_content)}")

            return {
                'title': title,
                'content': cleaned_content,
                'url': url
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error extracting job description from URL {url}: {str(e)}")
            raise Exception(f"Failed to extract job description: {str(e)}")
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