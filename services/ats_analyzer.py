import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import logging

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

            # Tokenize and clean texts
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

            return {
                'score': round(score, 2),
                'matching_keywords': list(matching_keywords)[:10],  # Top 10 matching keywords
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
            # Manually split text into words to avoid NLTK tokenizer issues
            words = text.lower().split()
            # Keep only alphanumeric tokens and remove stop words
            tokens = [
                word for word in words 
                if any(c.isalnum() for c in word) and word not in self.stop_words
            ]
            return tokens
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return []