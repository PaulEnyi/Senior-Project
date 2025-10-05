import re
import string
from typing import List, Dict, Set, Optional, Tuple
import logging
from collections import Counter
import unicodedata

logger = logging.getLogger(__name__)

class TextProcessor:
    """Utility class for text preprocessing and cleaning operations"""
    
    def __init__(self):
        # Common stop words for English
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'would', 'you', 'your', 'this', 'but',
            'they', 'have', 'had', 'what', 'said', 'each', 'which', 'their',
            'time', 'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so',
            'some', 'her', 'would', 'make', 'like', 'into', 'him', 'has', 'two',
            'more', 'very', 'what', 'know', 'just', 'first', 'get', 'over',
            'think', 'also', 'back', 'after', 'use', 'work', 'life', 'only',
            'new', 'way', 'may', 'say'
        }
        
        # Academic/educational specific stop words for Morgan State context
        self.academic_stop_words = {
            'university', 'college', 'school', 'student', 'students', 'course',
            'class', 'semester', 'academic', 'faculty', 'professor', 'study',
            'learn', 'education', 'department', 'program'
        }
        
        # Common contractions
        self.contractions = {
            "won't": "will not", "can't": "cannot", "n't": " not",
            "'re": " are", "'ve": " have", "'ll": " will", "'d": " would",
            "'m": " am", "let's": "let us", "that's": "that is",
            "what's": "what is", "here's": "here is", "there's": "there is",
            "where's": "where is", "who's": "who is", "it's": "it is"
        }
    
    def clean_text(self, text: str, aggressive: bool = False) -> str:
        """
        Clean and normalize text for processing
        
        Args:
            text: Input text to clean
            aggressive: If True, applies more aggressive cleaning
        """
        if not text:
            return ""
        
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Normalize unicode characters
            text = unicodedata.normalize('NFKD', text)
            
            # Expand contractions
            text = self._expand_contractions(text)
            
            # Remove HTML tags if any
            text = re.sub(r'<[^>]+>', '', text)
            
            # Remove URLs
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            
            # Remove email addresses
            text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
            
            if aggressive:
                # Remove all punctuation except periods and hyphens
                text = re.sub(r'[^\w\s.-]', ' ', text)
                # Remove extra whitespace
                text = ' '.join(text.split())
            else:
                # Keep some punctuation that might be meaningful
                text = re.sub(r'[^\w\s.,-]', ' ', text)
                # Normalize whitespace
                text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Text cleaning failed: {str(e)}")
            return text
    
    def _expand_contractions(self, text: str) -> str:
        """Expand contractions in text"""
        for contraction, expansion in self.contractions.items():
            text = text.replace(contraction, expansion)
        return text
    
    def remove_stop_words(self, text: str, include_academic: bool = False) -> str:
        """
        Remove stop words from text
        
        Args:
            text: Input text
            include_academic: Whether to also remove academic stop words
        """
        try:
            words = text.split()
            stop_words_set = self.stop_words.copy()
            
            if include_academic:
                stop_words_set.update(self.academic_stop_words)
            
            filtered_words = [word for word in words if word not in stop_words_set]
            return ' '.join(filtered_words)
            
        except Exception as e:
            logger.error(f"Stop word removal failed: {str(e)}")
            return text
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, int]]:
        """
        Extract top keywords from text based on frequency
        
        Args:
            text: Input text
            top_k: Number of top keywords to return
            
        Returns:
            List of (keyword, frequency) tuples
        """
        try:
            # Clean text
            cleaned = self.clean_text(text)
            cleaned = self.remove_stop_words(cleaned, include_academic=True)
            
            # Split into words and filter by length
            words = [word for word in cleaned.split() if len(word) > 2]
            
            # Count word frequencies
            word_counts = Counter(words)
            
            # Return top keywords
            return word_counts.most_common(top_k)
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {str(e)}")
            return []
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks for processing
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
        """
        try:
            if len(text) <= chunk_size:
                return [text]
            
            chunks = []
            start = 0
            
            while start < len(text):
                end = start + chunk_size
                
                # If not at the end, try to break at sentence boundary
                if end < len(text):
                    # Look for sentence endings near the chunk boundary
                    sentence_end = text.rfind('.', start, end)
                    if sentence_end > start + chunk_size // 2:
                        end = sentence_end + 1
                    else:
                        # Look for other break points
                        space_pos = text.rfind(' ', start, end)
                        if space_pos > start:
                            end = space_pos
                
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                
                # Move start position (with overlap)
                start = max(start + 1, end - overlap)
                
                # Prevent infinite loop
                if start >= len(text):
                    break
            
            logger.info(f"Split text into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Text chunking failed: {str(e)}")
            return [text]
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract individual sentences from text"""
        try:
            # Simple sentence splitting - can be improved with NLTK
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            return sentences
            
        except Exception as e:
            logger.error(f"Sentence extraction failed: {str(e)}")
            return [text]
    
    def normalize_morgan_state_terms(self, text: str) -> str:
        """
        Normalize Morgan State University specific terms for consistency
        """
        try:
            # Common variations of Morgan State
            morgan_variations = {
                r'\bmsu\b': 'morgan state university',
                r'\bmorgan state\b': 'morgan state university',
                r'\bmorgan\b': 'morgan state university',
                r'\bcs department\b': 'computer science department',
                r'\bcosc\b': 'computer science',
                r'\bcomputer sci\b': 'computer science',
                r'\bcomp sci\b': 'computer science'
            }
            
            normalized_text = text.lower()
            for pattern, replacement in morgan_variations.items():
                normalized_text = re.sub(pattern, replacement, normalized_text, flags=re.IGNORECASE)
            
            return normalized_text
            
        except Exception as e:
            logger.error(f"Morgan State term normalization failed: {str(e)}")
            return text
    
    def extract_course_codes(self, text: str) -> List[str]:
        """Extract course codes (e.g., COSC 111, MATH 152) from text"""
        try:
            # Pattern for course codes: 2-4 letters followed by space and 3-4 digits
            pattern = r'\b[A-Z]{2,4}\s+\d{3,4}\b'
            course_codes = re.findall(pattern, text.upper())
            return list(set(course_codes))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Course code extraction failed: {str(e)}")
            return []
    
    def extract_contact_info(self, text: str) -> Dict[str, List[str]]:
        """Extract contact information from text"""
        try:
            contact_info = {
                'emails': [],
                'phones': [],
                'office_hours': []
            }
            
            # Email pattern
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            contact_info['emails'] = re.findall(email_pattern, text)
            
            # Phone pattern (various formats)
            phone_pattern = r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
            contact_info['phones'] = re.findall(phone_pattern, text)
            
            # Office hours pattern
            hours_pattern = r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)[\s\w,-]*\d{1,2}:\d{2}[\s\w]*(?:am|pm)'
            contact_info['office_hours'] = re.findall(hours_pattern, text, re.IGNORECASE)
            
            return contact_info
            
        except Exception as e:
            logger.error(f"Contact info extraction failed: {str(e)}")
            return {'emails': [], 'phones': [], 'office_hours': []}
    
    def calculate_readability_score(self, text: str) -> Dict[str, float]:
        """
        Calculate basic readability metrics for text
        """
        try:
            # Count sentences, words, syllables (simplified)
            sentences = len(self.extract_sentences(text))
            words = len(text.split())
            
            # Simple syllable count (vowel groups)
            syllables = 0
            for word in text.split():
                word = word.lower().strip('.,!?";')
                syllable_count = len(re.findall(r'[aeiouy]+', word))
                if syllable_count == 0:
                    syllable_count = 1
                syllables += syllable_count
            
            if sentences == 0 or words == 0:
                return {'flesch_score': 0, 'avg_words_per_sentence': 0, 'avg_syllables_per_word': 0}
            
            # Flesch Reading Ease Score (simplified)
            avg_sentence_length = words / sentences
            avg_syllables_per_word = syllables / words
            
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            
            return {
                'flesch_score': round(flesch_score, 2),
                'avg_words_per_sentence': round(avg_sentence_length, 2),
                'avg_syllables_per_word': round(avg_syllables_per_word, 2)
            }
            
        except Exception as e:
            logger.error(f"Readability calculation failed: {str(e)}")
            return {'flesch_score': 0, 'avg_words_per_sentence': 0, 'avg_syllables_per_word': 0}
    
    def preprocess_for_embedding(self, text: str) -> str:
        """
        Preprocess text specifically for embedding generation
        
        Less aggressive cleaning to preserve context for embeddings
        """
        try:
            # Basic cleaning
            text = unicodedata.normalize('NFKD', text)
            text = self._expand_contractions(text)
            text = re.sub(r'<[^>]+>', '', text)  # Remove HTML
            text = re.sub(r'http[s]?://\S+', '', text)  # Remove URLs
            
            # Normalize Morgan State terms
            text = self.normalize_morgan_state_terms(text)
            
            # Remove excessive whitespace but keep structure
            text = re.sub(r'\n+', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Embedding preprocessing failed: {str(e)}")
            return text
    
    def get_text_statistics(self, text: str) -> Dict[str, any]:
        """Get comprehensive statistics about the text"""
        try:
            words = text.split()
            sentences = self.extract_sentences(text)
            course_codes = self.extract_course_codes(text)
            contact_info = self.extract_contact_info(text)
            keywords = self.extract_keywords(text, top_k=5)
            readability = self.calculate_readability_score(text)
            
            return {
                'character_count': len(text),
                'word_count': len(words),
                'sentence_count': len(sentences),
                'paragraph_count': len(text.split('\n\n')),
                'course_codes_found': course_codes,
                'contact_info': contact_info,
                'top_keywords': keywords,
                'readability': readability,
                'avg_word_length': round(sum(len(word) for word in words) / len(words), 2) if words else 0
            }
            
        except Exception as e:
            logger.error(f"Text statistics calculation failed: {str(e)}")
            return {}

# Global instance
text_processor = TextProcessor()