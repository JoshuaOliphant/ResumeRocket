import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

class ATSAnalyzer:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
    
    def analyze(self, resume_text, job_description):
        """
        Analyze resume against job description using keyword matching
        Returns a score from 0-100 and relevant keywords
        """
        # Tokenize and clean texts
        resume_tokens = self._process_text(resume_text)
        job_tokens = self._process_text(job_description)
        
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
            'matching_keywords': list(matching_keywords),
            'missing_keywords': missing_keywords[:10]  # Top 10 missing keywords
        }
    
    def _process_text(self, text):
        """Process text by tokenizing and removing stop words"""
        tokens = word_tokenize(text.lower())
        tokens = [token for token in tokens if token.isalnum()]  # Keep only alphanumeric
        tokens = [token for token in tokens if token not in self.stop_words]
        return tokens
