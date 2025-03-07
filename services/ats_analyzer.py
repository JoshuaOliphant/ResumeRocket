import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import logging
import re

logger = logging.getLogger(__name__)

class ATSAnalyzer:
    def __init__(self):
        # Download required NLTK data
        try:
            # Download only if not already present
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))
        except Exception as e:
            logger.error(f"Error initializing NLTK: {str(e)}")
            self.stop_words = set()

    def analyze(self, resume_text, job_description):
        """
        Analyze resume against job description using keyword matching
        Returns a score from 0-100 and relevant keywords
        """
        try:
            if not resume_text or not job_description:
                return {
                    'score': 0,
                    'matching_keywords': [],
                    'missing_keywords': []
                }

            # Clean and tokenize texts
            resume_tokens = self._process_text(resume_text)
            job_tokens = self._process_text(job_description)

            if not resume_tokens or not job_tokens:
                logger.error("Failed to process text tokens")
                return {
                    'score': 0,
                    'matching_keywords': [],
                    'missing_keywords': []
                }

            # Get keyword frequencies
            job_keywords = Counter(job_tokens)
            resume_keywords = Counter(resume_tokens)

            # Filter out common words and URLs/HTML content
            job_keywords = self._filter_keywords(job_keywords)
            resume_keywords = self._filter_keywords(resume_keywords)

            # Calculate matching score
            matching_keywords = set(resume_keywords.keys()) & set(job_keywords.keys())
            total_job_keywords = len(set(job_keywords.keys()))

            if total_job_keywords == 0:
                return {
                    'score': 0,
                    'matching_keywords': list(matching_keywords),
                    'missing_keywords': []
                }

            score = (len(matching_keywords) / total_job_keywords) * 100
            missing_keywords = list(set(job_keywords.keys()) - set(resume_keywords.keys()))

            # Sort keywords by frequency
            matching_keywords = sorted(matching_keywords, key=lambda k: job_keywords[k], reverse=True)
            missing_keywords = sorted(missing_keywords, key=lambda k: job_keywords[k], reverse=True)

            return {
                'score': round(score, 2),
                'matching_keywords': matching_keywords[:10],  # Top 10 matching keywords
                'missing_keywords': missing_keywords[:10]  # Top 10 missing keywords
            }
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            return {
                'score': 0,
                'matching_keywords': [],
                'missing_keywords': []
            }

    def _process_text(self, text):
        """Process text by tokenizing and removing stop words"""
        try:
            # Remove URLs and HTML-like content
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            text = re.sub(r'\[.*?\]', '', text)
            text = re.sub(r'\(.*?\)', '', text)

            # Split into words and clean
            words = text.lower().split()
            # Keep only meaningful words
            tokens = [
                word for word in words 
                if any(c.isalnum() for c in word) 
                and word not in self.stop_words
                and len(word) > 2  # Filter out very short words
            ]
            return tokens
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return []

    def _filter_keywords(self, keywords):
        """Filter out common words and non-relevant content"""
        # Remove very common words and non-meaningful terms
        filtered = {k: v for k, v in keywords.items() 
                   if not any(char in k for char in ',.:;=()[]{}<>') 
                   and not k.startswith(('http', 'www', 'com'))
                   and len(k) > 2}
        return filtered