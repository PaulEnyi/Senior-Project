from typing import List, Dict, Any, Optional, Tuple
import re
import string
import unicodedata
import logging
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('wordnet')
except LookupError:
    nltk.download('wordnet')

class TextProcessor:
    """Main text processing utility class"""
    
    def __init__(self, language: str = 'english'):
        self.language = language
        self.stop_words = set(stopwords.words(language))
        self.lemmatizer = WordNetLemmatizer()
        
        # Common abbreviations in academic context
        self.abbreviations = {
            'CS': 'Computer Science',
            'AI': 'Artificial Intelligence',
            'ML': 'Machine Learning',
            'DB': 'Database',
            'OS': 'Operating System',
            'GPA': 'Grade Point Average',
            'MSU': 'Morgan State University',
            'COSC': 'Computer Science Course'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\(\)]', '', text)
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Fix common encoding issues
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        return text.strip()
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize text into sentences"""
        try:
            sentences = sent_tokenize(text)
            return [s.strip() for s in sentences if s.strip()]
        except Exception as e:
            logger.error(f"Sentence tokenization error: {str(e)}")
            # Fallback to simple splitting
            return text.split('. ')
    
    def tokenize_words(self, text: str) -> List[str]:
        """Tokenize text into words"""
        try:
            return word_tokenize(text.lower())
        except Exception as e:
            logger.error(f"Word tokenization error: {str(e)}")
            # Fallback to simple splitting
            return text.lower().split()
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from token list"""
        return [token for token in tokens if token not in self.stop_words]
    
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """Lemmatize tokens"""
        try:
            return [self.lemmatizer.lemmatize(token) for token in tokens]
        except Exception as e:
            logger.error(f"Lemmatization error: {str(e)}")
            return tokens
    
    def expand_abbreviations(self, text: str) -> str:
        """Expand known abbreviations"""
        for abbr, full in self.abbreviations.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(abbr) + r'\b'
            text = re.sub(pattern, full, text)
        
        return text
    
    def extract_keywords(
        self,
        text: str,
        max_keywords: int = 10,
        min_length: int = 3
    ) -> List[Tuple[str, int]]:
        """Extract keywords from text using frequency analysis"""
        # Tokenize and clean
        tokens = self.tokenize_words(text)
        tokens = self.remove_stopwords(tokens)
        tokens = self.lemmatize_tokens(tokens)
        
        # Filter by length
        tokens = [t for t in tokens if len(t) >= min_length]
        
        # Count frequencies
        counter = Counter(tokens)
        
        # Return top keywords
        return counter.most_common(max_keywords)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts"""
        # Tokenize and clean
        tokens1 = set(self.tokenize_words(text1.lower()))
        tokens2 = set(self.tokenize_words(text2.lower()))
        
        # Calculate Jaccard similarity
        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union)
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 200,
        method: str = 'character'
    ) -> List[str]:
        """Split text into chunks"""
        chunks = []
        
        if method == 'character':
            # Character-based chunking
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk = text[start:end]
                
                # Try to break at sentence boundary
                if end < len(text):
                    last_period = chunk.rfind('. ')
                    if last_period > chunk_size - 200:
                        end = start + last_period + 2
                        chunk = text[start:end]
                
                chunks.append(chunk)
                start = end - overlap
                
        elif method == 'sentence':
            # Sentence-based chunking
            sentences = self.tokenize_sentences(text)
            current_chunk = []
            current_size = 0
            
            for sentence in sentences:
                sentence_size = len(sentence)
                
                if current_size + sentence_size > chunk_size and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    # Keep some overlap
                    if overlap > 0:
                        keep_sentences = []
                        kept_size = 0
                        for s in reversed(current_chunk):
                            kept_size += len(s)
                            if kept_size >= overlap:
                                break
                            keep_sentences.insert(0, s)
                        current_chunk = keep_sentences
                        current_size = kept_size
                    else:
                        current_chunk = []
                        current_size = 0
                
                current_chunk.append(sentence)
                current_size += sentence_size
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = {
            'courses': [],
            'professors': [],
            'rooms': [],
            'dates': [],
            'times': [],
            'emails': [],
            'phones': []
        }
        
        # Extract course codes (e.g., COSC 111)
        course_pattern = r'\b(COSC|MATH|PHYS|CHEM)\s+\d{3}\b'
        entities['courses'] = re.findall(course_pattern, text)
        
        # Extract professor names (Dr./Prof. LastName)
        prof_pattern = r'\b(Dr\.|Prof\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?'
        entities['professors'] = re.findall(prof_pattern, text)
        
        # Extract room numbers
        room_pattern = r'\b(Room|Suite|Office)\s+\d+[A-Z]?\b'
        entities['rooms'] = re.findall(room_pattern, text)
        
        # Extract dates (various formats)
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        entities['dates'] = re.findall(date_pattern, text)
        
        # Extract times
        time_pattern = r'\b\d{1,2}:\d{2}\s*(AM|PM|am|pm)?\b'
        entities['times'] = re.findall(time_pattern, text)
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['emails'] = re.findall(email_pattern, text)
        
        # Extract phone numbers
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        entities['phones'] = re.findall(phone_pattern, text)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def summarize_text(
        self,
        text: str,
        max_sentences: int = 3,
        method: str = 'frequency'
    ) -> str:
        """Generate a simple summary of text"""
        sentences = self.tokenize_sentences(text)
        
        if len(sentences) <= max_sentences:
            return text
        
        if method == 'frequency':
            # Frequency-based summarization
            word_freq = Counter()
            
            for sentence in sentences:
                tokens = self.tokenize_words(sentence.lower())
                tokens = self.remove_stopwords(tokens)
                word_freq.update(tokens)
            
            # Score sentences
            sentence_scores = {}
            for sentence in sentences:
                tokens = self.tokenize_words(sentence.lower())
                tokens = self.remove_stopwords(tokens)
                
                if tokens:
                    score = sum(word_freq[token] for token in tokens)
                    sentence_scores[sentence] = score / len(tokens)
            
            # Get top sentences
            top_sentences = sorted(
                sentence_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:max_sentences]
            
            # Return in original order
            summary_sentences = []
            for sentence in sentences:
                if any(sentence == s[0] for s in top_sentences):
                    summary_sentences.append(sentence)
                    if len(summary_sentences) >= max_sentences:
                        break
            
            return ' '.join(summary_sentences)
        
        else:
            # Simple first-N sentences
            return ' '.join(sentences[:max_sentences])
    
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """Get various statistics about the text"""
        sentences = self.tokenize_sentences(text)
        words = self.tokenize_words(text)
        
        # Calculate readability (simple version)
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Flesch Reading Ease approximation
        flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * (avg_word_length / 4.7)
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'paragraph_count': text.count('\n\n') + 1,
            'average_word_length': round(avg_word_length, 2),
            'average_sentence_length': round(avg_sentence_length, 2),
            'unique_words': len(set(words)),
            'lexical_diversity': len(set(words)) / len(words) if words else 0,
            'flesch_reading_ease': round(flesch_score, 2)
        }
    
    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove trailing whitespace from lines
        lines = text.split('\n')
        lines = [line.rstrip() for line in lines]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def extract_questions(self, text: str) -> List[str]:
        """Extract questions from text"""
        sentences = self.tokenize_sentences(text)
        questions = []
        
        for sentence in sentences:
            # Check if sentence ends with question mark
            if sentence.strip().endswith('?'):
                questions.append(sentence.strip())
            # Check for question words at start
            elif re.match(r'^(What|When|Where|Who|Why|How|Is|Are|Can|Could|Should|Would|Will)', sentence):
                questions.append(sentence.strip())
        
        return questions

class CourseTextProcessor(TextProcessor):
    """Specialized text processor for course-related content"""
    
    def __init__(self):
        super().__init__()
        
        # Course-specific patterns
        self.course_code_pattern = re.compile(r'[A-Z]{2,4}\s*\d{3}[A-Z]?')
        self.gpa_pattern = re.compile(r'\d\.\d{1,2}')
        self.credit_pattern = re.compile(r'\d+\s*credits?')
    
    def extract_course_codes(self, text: str) -> List[str]:
        """Extract course codes from text"""
        matches = self.course_code_pattern.findall(text)
        # Normalize format
        return [re.sub(r'\s+', ' ', match) for match in matches]
    
    def extract_prerequisites(self, text: str) -> List[str]:
        """Extract prerequisite courses from text"""
        prereq_keywords = ['prerequisite', 'prereq', 'required', 'must have completed']
        
        prerequisites = []
        for keyword in prereq_keywords:
            if keyword in text.lower():
                # Find course codes near the keyword
                pattern = f'{keyword}.*?({self.course_code_pattern.pattern})'
                matches = re.findall(pattern, text, re.IGNORECASE)
                prerequisites.extend(matches)
        
        return list(set(prerequisites))
    
    def extract_gpa(self, text: str) -> List[str]:
        """Extract GPA values from text"""
        return self.gpa_pattern.findall(text)
    
    def extract_credits(self, text: str) -> List[str]:
        """Extract credit information from text"""
        return self.credit_pattern.findall(text)
