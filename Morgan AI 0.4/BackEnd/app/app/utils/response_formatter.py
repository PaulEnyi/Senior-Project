"""
Functions for formatting and enhancing chat responses
"""


from typing import Dict, Any, List, Optional, Union
import re
import json
import logging
from datetime import datetime
from markdown import markdown
import html

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Format and enhance chatbot responses"""
    
    def __init__(self):
        self.max_response_length = 4000
        self.code_languages = [
            "python", "javascript", "java", "cpp", "c", "html", 
            "css", "sql", "bash", "json", "yaml", "markdown"
        ]
    
    def format_response(
        self,
        content: str,
        sources: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        format_type: str = "markdown"
    ) -> Dict[str, Any]:
        """Format a complete response with content and metadata"""
        
        # Clean and process content
        formatted_content = self.clean_text(content)
        
        # Apply formatting based on type
        if format_type == "markdown":
            formatted_content = self.enhance_markdown(formatted_content)
        elif format_type == "html":
            formatted_content = self.markdown_to_html(formatted_content)
        elif format_type == "plain":
            formatted_content = self.strip_formatting(formatted_content)
        
        # Add source citations if provided
        if sources:
            formatted_content = self.add_sources(formatted_content, sources)
        
        # Truncate if too long
        if len(formatted_content) > self.max_response_length:
            formatted_content = self.truncate_response(formatted_content)
        
        # Build response
        response = {
            "content": formatted_content,
            "format": format_type,
            "timestamp": datetime.utcnow().isoformat(),
            "word_count": len(formatted_content.split()),
            "char_count": len(formatted_content)
        }
        
        # Add sources
        if sources:
            response["sources"] = sources
        
        # Add metadata
        if metadata:
            response["metadata"] = metadata
        
        return response
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Fix common encoding issues
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('—', '-').replace('–', '-')
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    def enhance_markdown(self, text: str) -> str:
        """Enhance markdown formatting"""
        # Add proper headers
        text = self._format_headers(text)
        
        # Format lists
        text = self._format_lists(text)
        
        # Format code blocks
        text = self._format_code_blocks(text)
        
        # Add emphasis to important terms
        text = self._add_emphasis(text)
        
        # Format links
        text = self._format_links(text)
        
        return text
    
    def _format_headers(self, text: str) -> str:
        """Format headers properly"""
        lines = text.split('\n')
        formatted = []
        
        for line in lines:
            # Convert uppercase lines to headers
            if line.isupper() and len(line) > 3 and len(line) < 50:
                formatted.append(f"## {line.title()}")
            else:
                formatted.append(line)
        
        return '\n'.join(formatted)
    
    def _format_lists(self, text: str) -> str:
        """Format bullet points and numbered lists"""
        # Convert dash lists to proper markdown
        text = re.sub(r'^- ', '- ', text, flags=re.MULTILINE)
        
        # Convert numbered lists
        text = re.sub(r'^(\d+)\. ', r'\1. ', text, flags=re.MULTILINE)
        
        return text
    
    def _format_code_blocks(self, text: str) -> str:
        """Format code blocks with language detection"""
        # Find code blocks
        code_pattern = r'```(.*?)\n(.*?)```'
        
        def replace_code(match):
            lang = match.group(1).strip().lower()
            code = match.group(2)
            
            # Auto-detect language if not specified
            if not lang:
                lang = self._detect_language(code)
            
            return f"```{lang}\n{code}```"
        
        text = re.sub(code_pattern, replace_code, text, flags=re.DOTALL)
        
        return text
    
    def _detect_language(self, code: str) -> str:
        """Simple language detection for code blocks"""
        if 'def ' in code or 'import ' in code or 'print(' in code:
            return 'python'
        elif 'function' in code or 'const ' in code or 'var ' in code:
            return 'javascript'
        elif 'public class' in code or 'public static' in code:
            return 'java'
        elif '#include' in code:
            return 'cpp'
        elif 'SELECT' in code.upper() or 'FROM' in code.upper():
            return 'sql'
        elif '<html' in code or '<div' in code:
            return 'html'
        else:
            return ''
    
    def _add_emphasis(self, text: str) -> str:
        """Add emphasis to important terms"""
        # Bold important keywords
        important_terms = [
            'IMPORTANT', 'NOTE', 'WARNING', 'REQUIRED', 'DEADLINE',
            'Prerequisites', 'Requirements', 'Steps'
        ]
        
        for term in important_terms:
            text = re.sub(
                f'\\b({term})\\b',
                f'**{term}**',
                text,
                flags=re.IGNORECASE
            )
        
        return text
    
    def _format_links(self, text: str) -> str:
        """Format URLs as proper markdown links"""
        # Format URLs that aren't already in markdown
        url_pattern = r'(?<![\[\(])(https?://[^\s\)]+)(?![\]\)])'
        text = re.sub(url_pattern, r'[\1](\1)', text)
        
        # Format email addresses
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        text = re.sub(email_pattern, r'[\1](mailto:\1)', text)
        
        return text
    
    def markdown_to_html(self, text: str) -> str:
        """Convert markdown to HTML"""
        try:
            html_content = markdown(text, extensions=['extra', 'codehilite'])
            # Sanitize HTML
            return self.sanitize_html(html_content)
        except Exception as e:
            logger.error(f"Markdown conversion error: {str(e)}")
            return html.escape(text)
    
    def sanitize_html(self, html_content: str) -> str:
        """Sanitize HTML to prevent XSS"""
        # Allow safe tags only
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'span', 'div'
        ]
        
        # This is a basic implementation
        return html_content
    
    def strip_formatting(self, text: str) -> str:
        """Remove all formatting and return plain text"""
        # Remove markdown formatting
        text = re.sub(r'[*_`#\[\]()]', '', text)
        
        # Remove HTML tags if present
        text = re.sub(r'<[^>]+>', '', text)
        
        return text
    
    def add_sources(self, content: str, sources: List[str]) -> str:
        """Add source citations to response"""
        if not sources:
            return content
        
        # Add sources section
        sources_section = "\n\n---\n### Sources\n"
        for i, source in enumerate(sources, 1):
            sources_section += f"{i}. {source}\n"
        
        return content + sources_section
    
    def truncate_response(
        self,
        text: str,
        max_length: Optional[int] = None
    ) -> str:
        """Truncate response while preserving structure"""
        max_length = max_length or self.max_response_length
        
        if len(text) <= max_length:
            return text
        
        # Try to truncate at sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        last_newline = truncated.rfind('\n')
        
        # Choose the best truncation point
        if last_period > max_length - 200:
            truncated = truncated[:last_period + 1]
        elif last_newline > max_length - 200:
            truncated = truncated[:last_newline]
        else:
            truncated = truncated[:max_length - 3] + '...'
        
        # Add continuation notice
        truncated += "\n\n*[Response truncated due to length]*"
        
        return truncated
    
    def format_error_response(
        self,
        error_message: str,
        error_code: Optional[str] = None,
        suggestions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Format an error response"""
        response = {
            "error": True,
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if error_code:
            response["error_code"] = error_code
        
        if suggestions:
            response["suggestions"] = suggestions
        
        return response
    
    def format_list_response(
        self,
        items: List[Any],
        title: Optional[str] = None,
        format_type: str = "bullet"
    ) -> str:
        """Format a list of items"""
        formatted = ""
        
        if title:
            formatted += f"## {title}\n\n"
        
        if format_type == "bullet":
            for item in items:
                formatted += f"- {item}\n"
        elif format_type == "numbered":
            for i, item in enumerate(items, 1):
                formatted += f"{i}. {item}\n"
        elif format_type == "table":
            formatted = self._format_table(items)
        
        return formatted
    
    def _format_table(self, items: List[Dict[str, Any]]) -> str:
        """Format items as a markdown table"""
        if not items:
            return ""
        
        # Get headers from first item
        headers = list(items[0].keys())
        
        # Build table
        table = "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join(["-" * len(h) for h in headers]) + " |\n"
        
        for item in items:
            row = "| " + " | ".join([str(item.get(h, "")) for h in headers]) + " |\n"
            table += row
        
        return table
    
    def format_code_snippet(
        self,
        code: str,
        language: Optional[str] = None,
        title: Optional[str] = None
    ) -> str:
        """Format a code snippet"""
        formatted = ""
        
        if title:
            formatted += f"### {title}\n\n"
        
        if not language:
            language = self._detect_language(code)
        
        formatted += f"```{language}\n{code}\n```"
        
        return formatted
    
    def highlight_text(
        self,
        text: str,
        terms: List[str],
        highlight_format: str = "bold"
    ) -> str:
        """Highlight specific terms in text"""
        for term in terms:
            if highlight_format == "bold":
                replacement = f"**{term}**"
            elif highlight_format == "italic":
                replacement = f"*{term}*"
            elif highlight_format == "code":
                replacement = f"`{term}`"
            else:
                replacement = term
            
            text = re.sub(
                f'\\b{re.escape(term)}\\b',
                replacement,
                text,
                flags=re.IGNORECASE
            )
        
        return text

class ConversationFormatter:
    """Format conversation threads and messages"""
    
    @staticmethod
    def format_message(
        role: str,
        content: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format a single message"""
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp.isoformat() if timestamp else datetime.utcnow().isoformat()
        }
        
        if metadata:
            message["metadata"] = metadata
        
        return message
    
    @staticmethod
    def format_thread(
        messages: List[Dict[str, Any]],
        thread_id: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Format a conversation thread"""
        return {
            "thread_id": thread_id,
            "title": title or "Conversation",
            "messages": messages,
            "message_count": len(messages),
            "created_at": messages[0]["timestamp"] if messages else None,
            "updated_at": messages[-1]["timestamp"] if messages else None
        }
    
    @staticmethod
    def summarize_thread(messages: List[Dict[str, Any]], max_length: int = 100) -> str:
        """Create a summary of a conversation thread"""
        if not messages:
            return "Empty conversation"
        
        # Get first user message
        for msg in messages:
            if msg.get("role") == "user":
                summary = msg.get("content", "")[:max_length]
                if len(msg.get("content", "")) > max_length:
                    summary += "..."
                return summary
        
        return "Conversation"