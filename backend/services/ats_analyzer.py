import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.util import ngrams
from collections import Counter, defaultdict
import logging
import re
import math
import json
import os
from typing import Dict, List, Tuple, Set, Any, Optional

logger = logging.getLogger(__name__)

# Resume section patterns for detection
RESUME_SECTIONS = {
    "contact_info": [
        "contact information", "personal information", "contact details", "contact", 
        "personal details", "profile", "personal profile", "bio", "about me"
    ],
    "summary": [
        "professional summary", "summary", "executive summary", "career summary", 
        "profile summary", "professional profile", "career objective", "objective",
        "about me", "career profile", "summary of qualifications", "professional overview"
    ],
    "experience": [
        "experience", "work experience", "professional experience", "employment",
        "employment history", "work history", "career history", "job history",
        "professional background", "career accomplishments", "professional activities"
    ],
    "education": [
        "education", "educational background", "academic background", "academic history",
        "qualifications", "academic qualifications", "educational qualifications",
        "training", "academic training", "certifications & education", "degrees"
    ],
    "skills": [
        "skills", "technical skills", "core skills", "key skills", "professional skills",
        "competencies", "core competencies", "skill set", "expertise", "areas of expertise",
        "core capabilities", "professional skills", "strengths", "key strengths",
        "qualifications", "professional competencies", "technical competencies"
    ],
    "projects": [
        "projects", "project experience", "key projects", "professional projects",
        "research projects", "major projects", "notable projects", "project portfolio",
        "case studies", "portfolio", "project highlights", "selected projects"
    ],
    "certifications": [
        "certifications", "professional certifications", "licenses", "licensure",
        "credentials", "accreditations", "professional licenses", "qualifications",
        "certificates", "professional development", "training & certifications"
    ],
    "achievements": [
        "awards", "honors", "achievements", "accomplishments", "recognition",
        "awards & recognition", "honors & awards", "accolades", "distinctions",
        "notable achievements", "professional achievements", "key accomplishments"
    ],
    "languages": [
        "languages", "language skills", "language proficiencies", "foreign languages",
        "linguistic proficiency", "language competencies"
    ],
    "interests": [
        "interests", "personal interests", "hobbies", "activities", "extracurricular activities",
        "volunteer work", "community involvement", "volunteer experience", "volunteering"
    ],
    "references": [
        "references", "professional references", "character references", "referees",
        "recommendations", "testimonials", "endorsements", "reference list"
    ],
    "publications": [
        "publications", "research publications", "published works", "published research",
        "papers", "articles", "research papers", "academic publications", 
        "books", "journals", "conference papers", "presentations"
    ],
    "additional": [
        "additional information", "miscellaneous", "other information", "other",
        "additional details", "supplementary information", "additional skills"
    ]
}

# Section importance weights for different job types
SECTION_WEIGHTS = {
    "default": {
        "summary": 0.7,
        "experience": 1.5,
        "skills": 1.8,
        "education": 0.8,
        "projects": 1.0,
        "certifications": 0.9,
        "achievements": 0.7,
        "languages": 0.5,
        "publications": 0.6,
        "interests": 0.2,
        "additional": 0.4,
        "references": 0.1,
        "contact_info": 0.3
    },
    "technical": {
        "skills": 2.0,
        "experience": 1.6,
        "projects": 1.5,
        "education": 0.9,
        "certifications": 1.0
    },
    "management": {
        "experience": 2.0,
        "achievements": 1.5,
        "summary": 1.3,
        "skills": 1.2
    },
    "entry_level": {
        "education": 1.8,
        "skills": 1.5,
        "projects": 1.5,
        "experience": 1.0,
    },
    "academic": {
        "education": 1.8,
        "publications": 1.8,
        "research projects": 1.5,
        "experience": 1.0
    }
}

# Skills taxonomy and hierarchy
SKILLS_TAXONOMY = {
    # Programming Languages family relationships
    "programming": ["python", "java", "javascript", "c++", "c#", "ruby", "php", "typescript", "go", "swift"],
    "python": ["django", "flask", "fastapi", "pyramid", "numpy", "pandas", "scikit-learn", "tensorflow", "pytorch"],
    "java": ["spring", "hibernate", "maven", "junit", "struts", "jsf", "jpa", "jdbc"],
    "javascript": ["node.js", "react", "angular", "vue", "express", "jquery", "typescript", "nextjs", "nuxt"],
    "web_development": ["html", "css", "javascript", "react", "angular", "vue", "django", "flask", "node", "express"],
    
    # Data Science and Analytics
    "data_science": ["machine learning", "deep learning", "statistics", "data mining", "nlp", "computer vision", 
                     "predictive modeling", "python", "r", "tensorflow", "pytorch", "sklearn"],
    "data_analysis": ["sql", "data visualization", "etl", "data cleaning", "excel", "tableau", "power bi", 
                      "python", "r", "pandas", "numpy", "statistical analysis"],
    
    # DevOps and Cloud
    "devops": ["ci/cd", "jenkins", "docker", "kubernetes", "terraform", "ansible", "aws", "azure", "gcp", 
               "monitoring", "git", "github actions", "gitlab ci", "circleci"],
    "cloud": ["aws", "azure", "gcp", "cloud architecture", "serverless", "lambda", "ec2", "s3", "dynamodb", 
              "cloud security", "cloud migration", "docker", "kubernetes"],
    
    # Management and Leadership
    "leadership": ["team management", "strategy", "project management", "people management", "mentoring", 
                   "team building", "cross-functional", "stakeholder management"],
    "project_management": ["agile", "scrum", "kanban", "waterfall", "jira", "project planning", "risk management", 
                           "budgeting", "stakeholder communication"],
    
    # General Business Skills
    "business_analysis": ["requirements gathering", "process modeling", "data analysis", "stakeholder management", 
                          "use cases", "user stories", "bpmn", "uml"],
    "marketing": ["digital marketing", "seo", "sem", "content marketing", "social media", "email marketing", 
                  "marketing strategy", "analytics", "customer acquisition"]
}

class EnhancedATSAnalyzer:
    def __init__(self):
        # Download required NLTK data
        try:
            # Download only if not already present
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))
            
            # Add additional downloads for enhanced analysis
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('maxent_ne_chunker', quiet=True)
            nltk.download('words', quiet=True)
        except Exception as e:
            logger.error(f"Error initializing NLTK: {str(e)}")
            self.stop_words = set()
        
        # Default section weights
        self.section_weights = SECTION_WEIGHTS["default"]
        
        # Load skill relationships
        self.skills_taxonomy = SKILLS_TAXONOMY
        
        # Calibration constants
        self.BASE_SCORE_ADJUSTMENT = 30  # Lowered to make keyword matches more impactful
        self.SCALING_FACTOR = 0.8  # Increased to make improvements more significant
        
        # Position weights
        self.TITLE_WEIGHT = 2.5
        self.HEADER_WEIGHT = 2.0
        self.FIRST_PARAGRAPH_WEIGHT = 1.5
        self.BULLET_WEIGHT = 1.2
        
        # N-gram settings
        self.max_ngram_size = 3
    
    def analyze(self, resume_text, job_description):
        """
        Enhanced analysis of resume against job description using weighted keyword matching
        Returns a detailed score from 0-100, matching and missing keywords, section scores, and more
        """
        try:
            if not resume_text or not job_description:
                return self._empty_result()
            
            # Detect job type and adjust section weights
            job_type = self._detect_job_type(job_description)
            self._adjust_section_weights(job_type)
            
            # Identify sections in resume
            resume_sections = self._identify_sections(resume_text)
            
            # Process job description to extract key elements
            jd_elements = self._process_job_description(job_description)
            
            # Extract ngrams from both texts
            resume_ngrams = self._extract_ngrams(resume_text)
            job_ngrams = self._extract_ngrams(job_description)
            
            # Perform matching and scoring
            match_results = self._perform_matching(resume_text, resume_sections, resume_ngrams, 
                                                  job_description, jd_elements, job_ngrams)
            
            # Calculate section-based scores
            section_scores = self._calculate_section_scores(resume_sections, jd_elements)
            
            # Calculate overall score with calibration
            overall_score = self._calculate_calibrated_score(match_results, section_scores)
            
            # Prepare result with comprehensive details
            return {
                'score': round(overall_score, 2),
                'confidence': self._calculate_confidence(match_results),
                'matching_keywords': match_results['top_matching_keywords'],
                'missing_keywords': match_results['top_missing_keywords'],
                'section_scores': section_scores,
                'job_type': job_type,
                'keyword_density': match_results['keyword_density'],
                'suggestions': self._generate_suggestions(match_results, section_scores, jd_elements)
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced analysis: {str(e)}")
            return self._empty_result()
    
    def _empty_result(self):
        """Return empty result structure"""
        return {
            'score': 0,
            'confidence': 'low',
            'matching_keywords': [],
            'missing_keywords': [],
            'section_scores': {},
            'job_type': 'unknown',
            'keyword_density': 0,
            'suggestions': []
        }
    
    def _detect_job_type(self, job_description):
        """Detect job type based on job description content"""
        job_lower = job_description.lower()
        
        # Technical role indicators
        tech_keywords = ['developer', 'engineer', 'programmer', 'software', 'data scientist', 
                        'technical', 'architect', 'devops', 'administrator', 'analyst']
        
        # Management role indicators
        mgmt_keywords = ['manager', 'director', 'head of', 'lead', 'chief', 'senior', 
                         'executive', 'leadership', 'supervisor', 'principal']
        
        # Academic/research role indicators
        academic_keywords = ['research', 'phd', 'scientist', 'postdoc', 'professor', 
                            'lecturer', 'academic', 'teaching', 'fellow']
        
        # Entry-level indicators
        entry_keywords = ['entry', 'junior', 'internship', 'intern', 'trainee', 
                         'associate', 'assistant', 'graduate']
        
        # Count occurrences
        tech_count = sum(job_lower.count(kw) for kw in tech_keywords)
        mgmt_count = sum(job_lower.count(kw) for kw in mgmt_keywords)
        academic_count = sum(job_lower.count(kw) for kw in academic_keywords)
        entry_count = sum(job_lower.count(kw) for kw in entry_keywords)
        
        # Determine job type based on highest count
        counts = {
            'technical': tech_count,
            'management': mgmt_count,
            'academic': academic_count,
            'entry_level': entry_count
        }
        
        job_type = max(counts, key=counts.get) if max(counts.values()) > 0 else 'default'
        logger.debug(f"Detected job type: {job_type}")
        
        return job_type
    
    def _adjust_section_weights(self, job_type):
        """Adjust section weights based on job type"""
        # Start with default weights
        self.section_weights = SECTION_WEIGHTS["default"].copy()
        
        # Update with job-type specific weights if available
        if job_type in SECTION_WEIGHTS:
            for section, weight in SECTION_WEIGHTS[job_type].items():
                self.section_weights[section] = weight
    
    def _identify_sections(self, text):
        """Identify resume sections and their content"""
        sections = {}
        lines = text.split('\n')
        current_section = "unknown"
        section_content = []
        
        # Check for sections based on common headers and patterns
        for line in lines:
            line_lower = line.strip().lower()
            
            # Check if line is a section header
            found_section = False
            for section_name, section_patterns in RESUME_SECTIONS.items():
                # Check exact matches first
                if line_lower in section_patterns:
                    # Save previous section
                    if section_content:
                        sections[current_section] = '\n'.join(section_content)
                    
                    # Start new section
                    current_section = section_name
                    section_content = []
                    found_section = True
                    break
                
                # Check for header patterns (all caps, followed by colon, etc)
                elif any(pattern in line_lower for pattern in section_patterns):
                    # Save previous section
                    if section_content:
                        sections[current_section] = '\n'.join(section_content)
                    
                    # Start new section
                    current_section = section_name
                    section_content = []
                    found_section = True
                    break
                
                # Check for markdown-style headers
                elif line_lower.startswith(('#')):
                    header_text = re.sub(r'^#+\s*', '', line_lower)
                    for section_name, section_patterns in RESUME_SECTIONS.items():
                        if any(pattern in header_text for pattern in section_patterns):
                            # Save previous section
                            if section_content:
                                sections[current_section] = '\n'.join(section_content)
                            
                            # Start new section
                            current_section = section_name
                            section_content = []
                            found_section = True
                            break
            
            # If not a section header, add to current section content
            if not found_section:
                section_content.append(line)
        
        # Add the last section
        if section_content:
            sections[current_section] = '\n'.join(section_content)
        
        return sections
    
    def _process_job_description(self, text):
        """
        Process job description to extract key elements like requirements, responsibilities,
        qualifications, title, etc. with their relative importance
        """
        elements = {
            'title': '',
            'requirements': [],
            'responsibilities': [],
            'qualifications': [],
            'keywords': defaultdict(float),  # keyword -> weight mapping
            'sections': {}
        }
        
        # Extract title (usually first line or "Job Title:" or similar)
        lines = text.split('\n')
        for i, line in enumerate(lines[:5]):  # Check first 5 lines
            if re.search(r'job\s+title|position|role', line.lower()):
                title_match = re.search(r'(?:job\s+title|position|role)\s*[:-]\s*(.+)', line, re.IGNORECASE)
                if title_match:
                    elements['title'] = title_match.group(1).strip()
                    break
            elif i == 0 and len(line.strip()) < 80 and not line.strip().lower().startswith(('job ', 'about ', 'company')):
                # First line, relatively short, not a header
                elements['title'] = line.strip()
        
        # Process sections
        current_section = "general"
        section_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if line is a section header
            if re.match(r'^#+\s+', line) or re.match(r'^\*{2}[^*]+\*{2}$', line):  # Markdown headers or **bold**
                # Save previous section
                if section_content:
                    elements['sections'][current_section] = '\n'.join(section_content)
                
                # Determine new section
                clean_header = re.sub(r'^#+\s+|\*+', '', line_lower).strip()
                if any(kw in clean_header for kw in ['requirement', 'qualification', 'what you need']):
                    current_section = "requirements"
                elif any(kw in clean_header for kw in ['responsibilit', 'what you will do', 'duties']):
                    current_section = "responsibilities"
                elif any(kw in clean_header for kw in ['benefit', 'offer', 'what we offer']):
                    current_section = "benefits"
                elif any(kw in clean_header for kw in ['about us', 'company', 'who we are']):
                    current_section = "company"
                else:
                    current_section = clean_header
                
                section_content = []
            else:
                section_content.append(line)
            
            # Extract requirements & responsibilities from bullets/numbered lists
            if line_lower.strip().startswith(('- ', '* ', '• ')):
                item = re.sub(r'^[-*•]\s+', '', line).strip()
                
                if current_section == "requirements":
                    elements['requirements'].append(item)
                elif current_section == "responsibilities":
                    elements['responsibilities'].append(item)
            
            # Process each line for weighted keywords
            self._extract_weighted_keywords(line, elements['keywords'], current_section)
        
        # Save the last section
        if section_content:
            elements['sections'][current_section] = '\n'.join(section_content)
        
        return elements
    
    def _extract_weighted_keywords(self, line, keywords_dict, section_name):
        """Extract keywords from a line and assign weights based on position and context"""
        line_lower = line.lower()
        weight = 1.0
        
        # Adjust weight based on line formatting and position
        if re.match(r'^#+\s+', line):  # Markdown header
            weight = self.HEADER_WEIGHT
        elif line.isupper():  # ALL CAPS
            weight = 1.8
        elif re.match(r'^\*{2}[^*]+\*{2}$', line):  # **bold**
            weight = 1.5
        elif line_lower.strip().startswith(('- ', '* ', '• ')):  # Bullet points
            weight = self.BULLET_WEIGHT
        
        # Boost weight for requirements and qualifications sections
        if section_name in ["requirements", "qualifications"]:
            weight *= 1.5
        
        # Further boost for explicit required skills
        required_match = re.search(r'required|must have|necessary', line_lower)
        if required_match:
            weight *= 1.3
        
        # Process the text with n-grams
        tokens = self._process_text(line_lower)
        
        # Add single tokens with their weights
        for token in tokens:
            if token not in self.stop_words and len(token) > 2:
                keywords_dict[token] += weight
        
        # Process n-grams
        for n in range(2, self.max_ngram_size + 1):
            n_grams = list(ngrams(tokens, n))
            for gram in n_grams:
                if all(token not in self.stop_words for token in gram):
                    gram_text = ' '.join(gram)
                    if len(gram_text) > 3:  # Avoid very short n-grams
                        # Assign higher weight to multi-word technical terms
                        if gram_text in self._get_flattened_skills():
                            keywords_dict[gram_text] += weight * 1.5
                        else:
                            keywords_dict[gram_text] += weight * 1.2
    
    def _get_flattened_skills(self):
        """Flatten the skills taxonomy into a single set"""
        all_skills = set()
        for category, skills in self.skills_taxonomy.items():
            all_skills.add(category)
            all_skills.update(skills)
        return all_skills
    
    def _extract_ngrams(self, text):
        """Extract n-grams from text with their frequencies"""
        result = defaultdict(int)
        
        # Convert to lowercase and tokenize
        tokens = self._process_text(text.lower())
        
        # Extract n-grams of different sizes
        for n in range(1, self.max_ngram_size + 1):
            n_grams = list(ngrams(tokens, n))
            for gram in n_grams:
                # Filter out n-grams with stop words
                if n > 1 and any(token in self.stop_words for token in gram):
                    continue
                
                gram_text = ' '.join(gram)
                if len(gram_text) > 3:  # Avoid very short n-grams
                    result[gram_text] += 1
        
        return result
    
    def _process_text(self, text):
        """Process text by tokenizing and removing stop words"""
        try:
            # Remove URLs and HTML-like content
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            text = re.sub(r'\[.*?\]', '', text)
            text = re.sub(r'\(.*?\)', '', text)
            
            # Replace non-alphanumeric with space
            text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
            
            # Tokenize
            tokens = word_tokenize(text.lower())
            
            # Keep only meaningful words
            tokens = [
                word for word in tokens 
                if any(c.isalnum() for c in word) 
                and len(word) > 2  # Filter out very short words
            ]
            return tokens
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return []
    
    def _perform_matching(self, resume_text, resume_sections, resume_ngrams, 
                         job_description, jd_elements, job_ngrams):
        """Perform weighted matching between resume and job description"""
        result = {
            'exact_matches': {},
            'semantic_matches': {},
            'total_job_keywords': 0,
            'matched_job_keywords': 0,
            'weighted_match_score': 0,
            'top_matching_keywords': [],
            'top_missing_keywords': [],
            'keyword_density': 0
        }
        
        # Get weighted job keywords
        weighted_job_keywords = jd_elements['keywords']
        result['total_job_keywords'] = len(weighted_job_keywords)
        
        # 1. Exact matching with n-grams
        for job_keyword, job_weight in weighted_job_keywords.items():
            if job_keyword in resume_ngrams:
                match_weight = job_weight
                result['exact_matches'][job_keyword] = {
                    'weight': match_weight,
                    'frequency': resume_ngrams[job_keyword]
                }
                result['matched_job_keywords'] += 1
                result['weighted_match_score'] += match_weight
        
        # 2. Semantic matching with skill taxonomy
        for job_keyword, job_weight in weighted_job_keywords.items():
            # Skip already exactly matched
            if job_keyword in result['exact_matches']:
                continue
            
            # Check if this is a skill with related skills
            for category, skills in self.skills_taxonomy.items():
                # If job keyword is in a category's skills
                if job_keyword in skills:
                    # Check if resume has the category or any of its skills
                    if category in resume_ngrams:
                        result['semantic_matches'][job_keyword] = {
                            'matched_with': category,
                            'weight': job_weight * 0.8,  # Reduce weight for category match
                            'confidence': 'medium'
                        }
                        result['weighted_match_score'] += job_weight * 0.8
                        result['matched_job_keywords'] += 0.8  # Partial match
                        break
                    
                    # Check for sibling skills
                    for skill in skills:
                        if skill != job_keyword and skill in resume_ngrams:
                            result['semantic_matches'][job_keyword] = {
                                'matched_with': skill,
                                'weight': job_weight * 0.7,  # Reduce weight for sibling match
                                'confidence': 'medium'
                            }
                            result['weighted_match_score'] += job_weight * 0.7
                            result['matched_job_keywords'] += 0.7  # Partial match
                            break
                            
                # If job keyword is a category
                elif job_keyword == category:
                    # Check if resume has any of its skills
                    for skill in skills:
                        if skill in resume_ngrams:
                            result['semantic_matches'][job_keyword] = {
                                'matched_with': skill,
                                'weight': job_weight * 0.85,  # Higher match for skill under category
                                'confidence': 'high'
                            }
                            result['weighted_match_score'] += job_weight * 0.85
                            result['matched_job_keywords'] += 0.85  # Strong partial match
                            break
        
        # Calculate keyword density
        total_resume_words = len(self._process_text(resume_text))
        if total_resume_words > 0:
            matched_keywords_count = sum(data['frequency'] for data in result['exact_matches'].values())
            result['keyword_density'] = (matched_keywords_count / total_resume_words) * 100
        
        # Sort and get top matching and missing keywords
        all_matches = {**result['exact_matches'], **result['semantic_matches']}
        
        # Sort matches by weight and frequency
        sorted_matches = sorted(
            all_matches.items(), 
            key=lambda x: x[1].get('weight', 0) * (x[1].get('frequency', 1) if 'frequency' in x[1] else 1),
            reverse=True
        )
        result['top_matching_keywords'] = [keyword for keyword, _ in sorted_matches[:15]]
        
        # Get missing keywords (those not in exact or semantic matches)
        missing_keywords = {
            kw: weight for kw, weight in weighted_job_keywords.items() 
            if kw not in result['exact_matches'] and kw not in result['semantic_matches']
        }
        sorted_missing = sorted(missing_keywords.items(), key=lambda x: x[1], reverse=True)
        result['top_missing_keywords'] = [keyword for keyword, _ in sorted_missing[:15]]
        
        return result
    
    def _calculate_section_scores(self, resume_sections, jd_elements):
        """Calculate scores for each resume section based on job requirements"""
        section_scores = {}
        
        # Process each resume section
        for section_name, section_content in resume_sections.items():
            if section_name == "unknown":
                continue
                
            # Get the appropriate weight for this section
            section_weight = self.section_weights.get(section_name, 1.0)
            
            # Skip empty sections
            if not section_content.strip():
                section_scores[section_name] = 0
                continue
            
            # Calculate match score for this section
            section_tokens = self._process_text(section_content.lower())
            section_text = ' '.join(section_tokens)
            
            matches = 0
            total_keywords = 0
            
            # Check matches against job keywords
            for keyword, weight in jd_elements['keywords'].items():
                total_keywords += 1
                if ' ' in keyword:  # Multi-word keyword
                    if keyword in section_text:
                        matches += weight
                else:  # Single word
                    if keyword in section_tokens:
                        matches += weight
            
            # Calculate section score
            if total_keywords > 0:
                raw_score = (matches / total_keywords) * 100
                # Apply section weight
                weighted_score = raw_score * section_weight
                section_scores[section_name] = min(round(weighted_score, 2), 100)
            else:
                section_scores[section_name] = 0
        
        return section_scores
    
    def _calculate_calibrated_score(self, match_results, section_scores):
        """Calculate overall ATS score with calibration to match industry benchmarks"""
        # Base factors
        exact_match_score = 0
        semantic_match_score = 0
        section_coverage_score = 0
        density_score = 0
        
        # Calculate exact match component - MORE RESPONSIVE SIGMOID CURVE
        if match_results['total_job_keywords'] > 0:
            raw_match_ratio = match_results['weighted_match_score'] / (match_results['total_job_keywords'] * 2)
            # Modified sigmoid with steeper curve for more responsiveness
            exact_match_score = (1 / (1 + math.exp(-12 * (raw_match_ratio - 0.4)))) * 55  # Increased weight from 50 to 55
        
        # Calculate section coverage component
        important_sections = ['experience', 'skills', 'education', 'summary']  # Added 'summary' as important
        covered_sections = sum(1 for section in important_sections if section in section_scores and section_scores[section] > 0)
        section_coverage_score = (covered_sections / len(important_sections)) * 12  # Increased from 10 to 12
        
        # Calculate semantic match component
        semantic_matches_count = len(match_results['semantic_matches'])
        semantic_match_score = min(semantic_matches_count * 1.8, 18)  # Increased from 1.5 and 15 to 1.8 and 18
        
        # Calculate keyword density component
        optimal_density = 5.0  # 5% is generally considered optimal
        density = match_results['keyword_density']
        if density <= optimal_density:
            density_score = (density / optimal_density) * 10
        else:
            # Less penalization for keyword density over optimal
            density_score = 10 - min(((density - optimal_density) / 7) * 10, 8)  # Reduced penalty
        
        # Calculate bonus for high-value keywords (typically job titles, critical skills)
        high_value_keywords = sum(1 for kw in match_results.get('exact_matches', {}) 
                               if kw in match_results.get('top_matching_keywords', [])[:5])
        high_value_bonus = min(high_value_keywords * 1.5, 5)  # Up to 5 points bonus
        
        # Calculate overall score with industry-calibrated baseline
        raw_score = self.BASE_SCORE_ADJUSTMENT + (
            exact_match_score + semantic_match_score + section_coverage_score + 
            density_score + high_value_bonus
        ) * self.SCALING_FACTOR
        
        # Ensure score is within 0-100 range
        final_score = max(0, min(100, raw_score))
        
        return final_score
    
    def _calculate_confidence(self, match_results):
        """Calculate confidence level of the ATS score"""
        # Factors affecting confidence
        total_keywords = match_results['total_job_keywords']
        exact_matches = len(match_results['exact_matches'])
        semantic_matches = len(match_results['semantic_matches'])
        
        # Determine confidence
        if total_keywords < 5:
            return "low"  # Too few keywords to be confident
        elif exact_matches / total_keywords > 0.7:
            return "high"  # High exact match ratio
        elif (exact_matches + semantic_matches) / total_keywords > 0.5:
            return "medium"  # Decent combined match ratio
        else:
            return "low"  # Low match ratio
    
    def _generate_suggestions(self, match_results, section_scores, jd_elements):
        """Generate specific improvement suggestions based on analysis"""
        suggestions = []
        
        # 1. Missing critical keywords
        if match_results['top_missing_keywords']:
            critical_keywords = match_results['top_missing_keywords'][:5]
            suggestions.append({
                'type': 'missing_keywords',
                'title': 'Add these critical keywords',
                'content': f"Consider incorporating these key terms: {', '.join(critical_keywords)}"
            })
        
        # 2. Section-specific suggestions
        low_scoring_sections = [
            section for section, score in section_scores.items() 
            if score < 50 and section in ['experience', 'skills', 'education']
        ]
        
        for section in low_scoring_sections:
            suggestions.append({
                'type': 'section_improvement',
                'title': f"Improve your {section.title()} section",
                'content': f"Your {section} section could better align with job requirements."
            })
        
        # 3. Keyword density suggestion
        density = match_results['keyword_density']
        if density < 3:
            suggestions.append({
                'type': 'keyword_density',
                'title': "Increase relevant keyword density",
                'content': "Your resume has lower than optimal keyword density. Consider adding more relevant terms."
            })
        elif density > 7:
            suggestions.append({
                'type': 'keyword_density',
                'title': "Reduce keyword density",
                'content': "Your resume may have too many keywords which could appear as 'keyword stuffing'."
            })
        
        # 4. Missing qualifications
        if jd_elements['requirements'] and len(suggestions) < 5:
            resume_text = ' '.join(section_scores.keys())
            missing_reqs = []
            
            for req in jd_elements['requirements'][:5]:
                req_tokens = self._process_text(req.lower())
                req_text = ' '.join(req_tokens)
                
                # Check if this requirement is covered in the resume
                if not any(term in resume_text for term in req_tokens if len(term) > 3):
                    missing_reqs.append(req)
            
            if missing_reqs:
                suggestions.append({
                    'type': 'missing_qualifications',
                    'title': "Address missing qualifications",
                    'content': f"Your resume doesn't appear to address these requirements: {missing_reqs[0]}"
                })
        
        return suggestions[:5]  # Limit to top 5 suggestions


class ATSAnalyzer(EnhancedATSAnalyzer):
    """Legacy class that maintains the original interface while using the enhanced implementation"""
    
    def analyze(self, resume_text, job_description):
        """
        Analyze resume against job description using the enhanced analyzer
        but return results in the original format for backward compatibility
        """
        # Get the enhanced analysis
        enhanced_result = super().analyze(resume_text, job_description)
        
        # Convert to original format
        legacy_result = {
            'score': enhanced_result['score'],
            'matching_keywords': enhanced_result['matching_keywords'][:10],  # Keep only top 10
            'missing_keywords': enhanced_result['missing_keywords'][:10]  # Keep only top 10
        }
        
        return legacy_result