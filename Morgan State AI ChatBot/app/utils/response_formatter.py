import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """
    Utility class for formatting AI responses for the Morgan AI Chatbot
    
    Handles text formatting, markdown conversion, and response enhancement
    specifically for Morgan State University Computer Science department queries
    """
    
    def __init__(self):
        self.morgan_keywords = [
            "morgan state", "morgan", "msu", "computer science", "cosc",
            "faculty", "professor", "course", "degree", "major",
            "tuition", "registration", "advising", "prerequisite"
        ]
        
        self.dept_abbreviations = {
            "CS": "Computer Science",
            "COSC": "Computer Science",
            "MSU": "Morgan State University",
            "WiCS": "Women in Computer Science",
            "GDSC": "Google Developer Student Club",
            "SACS": "Student Association for Computing Systems"
        }
    
    def format_response(
        self, 
        raw_response: str, 
        context_sources: List[str] = None,
        user_query: str = None
    ) -> Dict[str, Any]:
        """
        Format the AI response with proper structure and enhancements
        
        Args:
            raw_response: Raw response from OpenAI
            context_sources: List of sources used in generating response
            user_query: Original user query for context
            
        Returns:
            Formatted response dictionary
        """
        try:
            # Clean and normalize the response
            cleaned_response = self._clean_response(raw_response)
            
            # Expand abbreviations
            expanded_response = self._expand_abbreviations(cleaned_response)
            
            # Format for markdown
            markdown_response = self._format_markdown(expanded_response)
            
            # Add Morgan State specific formatting
            enhanced_response = self._enhance_morgan_content(markdown_response)
            
            # Extract structured information
            structured_info = self._extract_structured_info(enhanced_response)
            
            return {
                "formatted_text": enhanced_response,
                "raw_text": raw_response,
                "markdown_formatted": True,
                "word_count": len(enhanced_response.split()),
                "character_count": len(enhanced_response),
                "sources_used": context_sources or [],
                "structured_info": structured_info,
                "formatting_applied": [
                    "text_cleaning",
                    "abbreviation_expansion", 
                    "markdown_formatting",
                    "morgan_enhancement"
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return {
                "formatted_text": raw_response,
                "raw_text": raw_response,
                "error": f"Formatting failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _clean_response(self, text: str) -> str:
        """Clean and normalize the response text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common formatting issues
        text = re.sub(r'\s+([.!?])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)  # Ensure space after sentences
        
        # Remove any potential harmful content markers
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        
        # Ensure proper capitalization after periods
        text = re.sub(r'(\.)(\s*)([a-z])', lambda m: m.group(1) + m.group(2) + m.group(3).upper(), text)
        
        return text.strip()
    
    def _expand_abbreviations(self, text: str) -> str:
        """Expand common abbreviations related to Morgan State"""
        expanded_text = text
        
        for abbrev, full_form in self.dept_abbreviations.items():
            # Replace abbreviations while preserving context
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            
            # Don't replace if it's already part of a longer phrase
            if abbrev in ["CS", "COSC"]:
                # Special handling for course codes like "COSC 111"
                expanded_text = re.sub(
                    pattern + r'(?=\s+\d)', 
                    abbrev, 
                    expanded_text
                )
            else:
                expanded_text = re.sub(pattern, full_form, expanded_text)
        
        return expanded_text
    
    def _format_markdown(self, text: str) -> str:
        """Apply markdown formatting for better readability"""
        
        # Bold important terms
        important_terms = [
            "Morgan State University", "Computer Science", 
            "prerequisite", "graduation", "degree", "major"
        ]
        
        for term in important_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            text = re.sub(pattern, f"**{term}**", text, flags=re.IGNORECASE)
        
        # Format course codes (e.g., COSC 111 -> **COSC 111**)
        text = re.sub(r'\b(COSC|MATH|ENGL|PHYS)\s+(\d{3})\b', r'**\1 \2**', text)
        
        # Format email addresses
        text = re.sub(r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b', r'[\1](mailto:\1)', text)
        
        # Format phone numbers
        text = re.sub(r'\((\d{3})\)\s*(\d{3})-(\d{4})', r'[(443) 885-\3](tel:+1\1\2\3)', text)
        
        # Format lists
        text = self._format_lists(text)
        
        return text
    
    def _format_lists(self, text: str) -> str:
        """Convert comma-separated lists to markdown lists where appropriate"""
        
        # Look for patterns like "courses include: A, B, C, and D"
        list_pattern = r'(courses? (?:include|are|offered):\s*)([^.!?]+)'
        
        def format_list_match(match):
            intro = match.group(1)
            items_text = match.group(2)
            
            # Split by commas and "and"
            items = re.split(r',\s*(?:and\s+)?|,\s*|\s+and\s+', items_text)
            items = [item.strip() for item in items if item.strip()]
            
            if len(items) > 2:
                formatted_list = intro + "\n" + "\n".join(f"- {item}" for item in items)
                return formatted_list
            else:
                return match.group(0)  # Return original if not enough items
        
        text = re.sub(list_pattern, format_list_match, text, flags=re.IGNORECASE)
        
        return text
    
    def _enhance_morgan_content(self, text: str) -> str:
        """Add Morgan State specific enhancements"""
        
        # Add helpful links for common terms
        link_replacements = {
            "Morgan State University": "[Morgan State University](https://www.morgan.edu)",
            "Computer Science department": "[Computer Science department](https://www.morgan.edu/scmns/computerscience)",
            "Canvas": "[Canvas](https://morganstate.instructure.com)",
            "WebSIS": "[WebSIS](https://websis.morgan.edu)"
        }
        
        for term, replacement in link_replacements.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Add context for office hours
        text = re.sub(
            r'\boffice hours\b',
            'office hours (check with individual faculty for current schedules)',
            text,
            flags=re.IGNORECASE
        )
        
        return text
    
    def _extract_structured_info(self, text: str) -> Dict[str, Any]:
        """Extract structured information from the response"""
        
        structured = {
            "courses_mentioned": [],
            "faculty_mentioned": [],
            "organizations_mentioned": [],
            "contact_info": [],
            "deadlines_mentioned": [],
            "links_included": []
        }
        
        # Extract course codes
        courses = re.findall(r'\b(COSC|MATH|ENGL|PHYS)\s+(\d{3})\b', text)
        structured["courses_mentioned"] = [f"{course[0]} {course[1]}" for course in courses]
        
        # Extract organizations
        orgs = ["WiCS", "GDSC", "SACS", "Women in Computer Science", 
                "Google Developer Student Club", "Student Association for Computing Systems"]
        for org in orgs:
            if org.lower() in text.lower():
                structured["organizations_mentioned"].append(org)
        
        # Extract email addresses
        emails = re.findall(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', text)
        structured["contact_info"].extend([{"type": "email", "value": email} for email in emails])
        
        # Extract phone numbers
        phones = re.findall(r'\((\d{3})\)\s*(\d{3})-(\d{4})', text)
        structured["contact_info"].extend([
            {"type": "phone", "value": f"({phone[0]}) {phone[1]}-{phone[2]}"} 
            for phone in phones
        ])
        
        # Extract links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
        structured["links_included"] = [{"text": link[0], "url": link[1]} for link in links]
        
        return structured
    
    def format_error_response(self, error_message: str, user_query: str = None) -> Dict[str, Any]:
        """Format error responses in a user-friendly way"""
        
        friendly_error = self._make_error_friendly(error_message, user_query)
        
        return {
            "formatted_text": friendly_error,
            "raw_text": error_message,
            "is_error": True,
            "suggestions": self._get_error_suggestions(error_message),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _make_error_friendly(self, error_message: str, user_query: str = None) -> str:
        """Convert technical error messages to user-friendly responses"""
        
        friendly_responses = {
            "timeout": "I'm sorry, but I'm taking longer than usual to respond. Please try asking your question again.",
            "connection": "I'm having trouble connecting to my knowledge base right now. Please try again in a moment.",
            "rate_limit": "I'm receiving a lot of questions right now. Please wait a moment and try again.",
            "invalid_query": "I didn't quite understand your question. Could you please rephrase it?",
            "no_context": "I don't have specific information about that topic in my Morgan State knowledge base. You might want to contact the Computer Science department directly."
        }
        
        error_lower = error_message.lower()
        
        for error_type, friendly_msg in friendly_responses.items():
            if error_type in error_lower:
                return friendly_msg
        
        # Default friendly error
        return ("I apologize, but I encountered an issue while processing your question. "
                "Please try rephrasing your question or contact the Morgan State Computer Science "
                "department for direct assistance.")
    
    def _get_error_suggestions(self, error_message: str) -> List[str]:
        """Provide helpful suggestions based on error type"""
        
        suggestions = [
            "Try rephrasing your question",
            "Check if you're asking about Morgan State Computer Science topics",
            "Contact the CS department directly at (443) 885-3130"
        ]
        
        if "connection" in error_message.lower():
            suggestions.insert(0, "Check your internet connection and try again")
        elif "timeout" in error_message.lower():
            suggestions.insert(0, "Try asking a simpler or more specific question")
        
        return suggestions
    
    def format_quick_response(self, response_type: str, **kwargs) -> str:
        """Generate quick formatted responses for common queries"""
        
        quick_responses = {
            "greeting": "Hello! I'm Morgan AI, your Computer Science department assistant. How can I help you today?",
            "department_location": "The Computer Science department is located in the **Science Complex, Room 325** at Morgan State University.",
            "contact_info": "You can reach the Computer Science department at **(443) 885-3130** or [computer.science@morgan.edu](mailto:computer.science@morgan.edu).",
            "office_hours": "Department office hours are **Monday-Friday, 9:00 AM - 5:00 PM**. Individual faculty office hours vary - please check with specific professors.",
            "unknown": "I don't have specific information about that topic. For the most current information, please contact the Computer Science department directly."
        }
        
        return quick_responses.get(response_type, quick_responses["unknown"])


def format_response(raw_response: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for formatting responses"""
    formatter = ResponseFormatter()
    return formatter.format_response(raw_response, **kwargs)

def format_error(error_message: str, user_query: str = None) -> Dict[str, Any]:
    """Convenience function for formatting error responses"""
    formatter = ResponseFormatter()
    return formatter.format_error_response(error_message, user_query)