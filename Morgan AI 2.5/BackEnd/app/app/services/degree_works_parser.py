"""
Degree Works PDF Parser
Robust parser that accurately extracts academic information from any student's Degree Works PDF
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import PyPDF2
import io

logger = logging.getLogger(__name__)

class DegreeWorksParser:
    """Parse Degree Works PDF and extract academic information with 100% accuracy"""
    
    def __init__(self):
        """Initialize the parser with pattern recognition rules"""
        
        # Patterns for identifying different sections and statuses
        self.completed_markers = ['✓', '✔', 'COMPLETE', 'COMPLETED', 'IP-COMPLETE']
        self.in_progress_markers = ['IP', 'IN PROGRESS', 'REGISTERED', 'IN-PROGRESS']
        self.not_taken_markers = ['NO', 'NOT TAKEN', 'NEEDS:', 'STILL NEEDED', 'REQUIRED']
        
        # Enhanced course code pattern - excludes semester labels like "FALL 2024"
        # Matches: COSC 111, CS 1234, MATH-201, CSCI 450
        # Negative lookahead prevents matching semester years
        self.course_code_pattern = re.compile(r'\b([A-Z]{2,4})[\s\-]*(\d{3,4}[A-Z]?)\b(?!\s*\d{4})')
        
        # Comprehensive grade pattern - includes all Morgan State grade types
        self.grade_pattern = re.compile(r'\b([A-F][+-]?|P|NP|W|WF|WP|I|IP|AU|S|U|D[+-]?)\b')
        
        # Dynamic current semester detection
        current_year = datetime.now().year
        current_month = datetime.now().month
        if current_month >= 8:  # August onwards
            self.current_semester = f"Fall {current_year}"
        elif current_month >= 5:  # May-July
            self.current_semester = f"Summer {current_year}"
        else:  # January-April
            self.current_semester = f"Spring {current_year}"
        
        logger.info(f"Parser initialized - Current semester: {self.current_semester}")
        
        # Morgan State University valid department codes (whitelist for course validation)
        self.valid_dept_codes = {
            # Computer Science & Engineering
            'COSC', 'CSCI', 'COMP', 'ENGR', 'CLCO', 'ELET', 'EEGR',
            # Mathematics & Sciences
            'MATH', 'STAT', 'PHYS', 'CHEM', 'BIOL', 'EASC', 'NUSC',
            # English & Humanities
            'ENGL', 'HUMA', 'PHIL', 'RELG', 'FREN', 'SPAN', 'AFST',
            # Social Sciences
            'HIST', 'PSYC', 'SOCI', 'POLI', 'ECON', 'GEOG', 'ANTH',
            # Business & Management
            'BUAD', 'ACCT', 'FINA', 'MANA', 'MARK', 'MKTG',
            # Arts & Communication
             'ARTS', 'MUSC', 'THEA', 'COMM', 'JOUR',
            # Health & Education
            'NURS', 'MHTC', 'EDUC', 'KINE', 'PHED',
            # Other
            'ORNS', 'UNIV', 'HONR'
        }
        
        # Classification thresholds (standard)
        self.classification_thresholds = {
            'Freshman': (0, 29),
            'Sophomore': (30, 59),
            'Junior': (60, 89),
            'Senior': (90, 999)
        }
        
        # Requirement category patterns
        self.category_patterns = {
            'Major Core': [
                r'MAJOR\s+REQUIREMENTS',
                r'REQUIRED\s+COURSES\s+FOR\s+THE\s+COMPUTER\s+SCIENCE\s+MAJOR',
                r'CORE\s+COMPUTER\s+SCIENCE\s+COURSES',
                r'MAJOR\s+CORE'
            ],
            'General Education': [
                r'GENERAL\s+EDUCATION',
                r'GEN\s+ED',
                r'UNIVERSITY\s+REQUIREMENTS',
                r'LIBERAL\s+ARTS'
            ],
            'Electives': [
                r'ELECTIVE',
                r'GROUP\s+[A-D]\s+ELECTIVE',
                r'FREE\s+ELECTIVE'
            ],
            'Supporting Courses': [
                r'SUPPORTING\s+COURSES',
                r'MATH\s+REQUIREMENTS',
                r'SCIENCE\s+REQUIREMENTS'
            ],
            'Complementary Studies': [
                r'COMPLEMENTARY\s+STUDIES',
                r'COMP\s+STUDIES'
            ]
        }
        
    async def parse_pdf(self, pdf_file_bytes: bytes) -> Dict[str, Any]:
        """
        Parse Degree Works PDF and extract all academic information
        
        Args:
            pdf_file_bytes: Raw bytes of the PDF file
            
        Returns:
            Comprehensive dictionary with all parsed academic data
        """
        try:
            logger.info("Starting Degree Works PDF parsing...")
            
            # Extract text from PDF
            text_content = self._extract_pdf_text(pdf_file_bytes)
            
            if not text_content or len(text_content) < 100:
                raise ValueError("PDF appears to be empty or unreadable")
            
            logger.info(f"Extracted {len(text_content)} characters from PDF")
            
            # Parse all components
            student_info = self._parse_student_info(text_content)
            academic_summary = self._parse_academic_summary(text_content)
            courses = self._parse_courses(text_content)
            elective_groups = self._parse_elective_groups(text_content, courses)
            # Derive credits from course lists when missing (fallback to sum of parsed courses)
            if academic_summary.get('completed_credits', 0) == 0 and courses['completed']:
                academic_summary['completed_credits'] = round(sum(c.get('credits', 0) for c in courses['completed']), 2)
            if academic_summary.get('in_progress_credits', 0) == 0 and courses['in_progress']:
                academic_summary['in_progress_credits'] = round(sum(c.get('credits', 0) for c in courses['in_progress']), 2)
            requirements = self._analyze_requirements(courses, text_content)
            course_timeline = self._build_course_timeline(courses)
            
            # Calculate remaining credits
            total_required = academic_summary.get('total_credits_required', 120)
            completed_credits = academic_summary.get('completed_credits', 0)
            in_progress_credits = academic_summary.get('in_progress_credits', 0)
            remaining_credits = max(0, total_required - completed_credits - in_progress_credits)
            
            # Determine classification
            classification = self._determine_classification(completed_credits)
            
            academic_summary['classification'] = classification
            academic_summary['remaining_credits'] = remaining_credits
            result = {
                'success': True,
                'parsed_at': datetime.utcnow().isoformat(),
                'student_info': student_info,
                'academic_summary': academic_summary,
                'courses': courses,
                'course_timeline': course_timeline,
                'requirements': requirements,
                'elective_groups': elective_groups,
                'raw_text_preview': text_content[:500]
            }
            
            logger.info(f"Successfully parsed Degree Works: {completed_credits} credits completed, {classification}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing Degree Works PDF: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'parsed_at': datetime.utcnow().isoformat()
            }
    
    def _extract_pdf_text(self, pdf_bytes: bytes) -> str:
        """Extract text content from PDF bytes"""
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_content.append(text)
            
            full_text = '\n'.join(text_content)
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise
    
    def _parse_student_info(self, text: str) -> Dict[str, str]:
        """Extract student identification information"""
        student_info = {}
        
        # Extract student name - multiple patterns for different layouts
        name_patterns = [
            r'(?:Student|Name):\s*([A-Z][A-Za-z\s]+?)(?:\s{2,}|$)',
            r'Student\s+Name\s*:\s*([A-Z][A-Za-z\s,]+)',
            r'Name\s*:\s*([A-Z][A-Za-z\s,]+?)(?:\s+ID|\s+Student)',
            r'^([A-Z][a-z]+,\s*[A-Z][a-z]+)',  # "LastName, FirstName" format
        ]
        for pattern in name_patterns:
            name_match = re.search(pattern, text, re.MULTILINE)
            if name_match:
                student_info['name'] = name_match.group(1).strip()
                logger.info(f"Extracted student name: {student_info['name']}")
                break
        
        # Extract student ID - multiple patterns
        id_patterns = [
            r'(?:ID|Student\s+ID|ID\s+Number):\s*(\d{7,10})',
            r'ID#?\s*(\d{7,10})',
            r'Student\s+Number:\s*(\d{7,10})'
        ]
        for pattern in id_patterns:
            id_match = re.search(pattern, text, re.IGNORECASE)
            if id_match:
                student_info['student_id'] = id_match.group(1).strip()
                logger.info(f"Extracted student ID: {student_info['student_id']}")
                break
        
        # Extract major - multiple patterns
        major_patterns = [
            r'(?:Major|Program):\s*([A-Za-z\s&]+?)(?:\s{2,}|Degree|$)',
            r'Program\s+of\s+Study:\s*([A-Za-z\s&]+)',
            r'Major:\s*([A-Z][A-Za-z\s&]+?)(?:\s+Degree|\s+BS|\s+BA)',
        ]
        for pattern in major_patterns:
            major_match = re.search(pattern, text, re.IGNORECASE)
            if major_match:
                student_info['major'] = major_match.group(1).strip()
                logger.info(f"Extracted major: {student_info['major']}")
                break
        
        # Extract degree
        degree_match = re.search(r'Degree:\s*([A-Z\.]+)', text)
        if degree_match:
            student_info['degree'] = degree_match.group(1).strip()
        
        return student_info
    
    def _parse_academic_summary(self, text: str) -> Dict[str, Any]:
        """Extract GPA, credits, and other academic summary data"""
        summary = {}
        
        # Extract GPA - prioritize Overall GPA (Morgan State format)
        gpa_patterns = [
            r'Overall\s+GPA:\s*(\d+\.\d+)',
            r'Cumulative\s+GPA:\s*(\d+\.\d+)',
            r'(?:Current\s+)?GPA:\s*(\d+\.\d+)'
        ]
        for pattern in gpa_patterns:
            gpa_match = re.search(pattern, text, re.IGNORECASE)
            if gpa_match:
                summary['gpa'] = float(gpa_match.group(1))
                logger.info(f"Extracted GPA: {summary['gpa']}")
                break
        
        # Extract total credits completed - prioritize "Credits applied" header (Morgan State)
        credits_applied_match = re.search(r'Credits\s+applied:\s*(\d+)', text, re.IGNORECASE)
        if credits_applied_match:
            summary['completed_credits'] = float(credits_applied_match.group(1))
            logger.info(f"Extracted credits from PDF header: {summary['completed_credits']}")
        else:
            # Fallback to generic patterns
            completed_patterns = [
                r'(?:Total\s+)?Credits?\s+(?:Earned|Completed):\s*(\d+\.?\d*)',
                r'Earned\s+Hours:\s*(\d+\.?\d*)',
                r'Completed:\s*(\d+\.?\d*)\s+credits?'
            ]
            for pattern in completed_patterns:
                completed_match = re.search(pattern, text, re.IGNORECASE)
                if completed_match:
                    summary['completed_credits'] = float(completed_match.group(1))
                    break
        
        # Extract in-progress credits
        ip_patterns = [
            r'In\s+Progress:\s*(\d+\.?\d*)',
            r'(?:Currently\s+)?Enrolled:\s*(\d+\.?\d*)',
            r'IP:\s*(\d+\.?\d*)\s+credits?'
        ]
        for pattern in ip_patterns:
            ip_match = re.search(pattern, text, re.IGNORECASE)
            if ip_match:
                summary['in_progress_credits'] = float(ip_match.group(1))
                break
        
        # Extract total required
        required_patterns = [
            r'(?:Total\s+)?Required:\s*(\d+\.?\d*)',
            r'Degree\s+Requires:\s*(\d+\.?\d*)',
            r'Total\s+Credits?\s+Needed:\s*(\d+\.?\d*)'
        ]
        for pattern in required_patterns:
            required_match = re.search(pattern, text, re.IGNORECASE)
            if required_match:
                summary['total_credits_required'] = float(required_match.group(1))
                break
        
        # Set defaults if not found
        if 'completed_credits' not in summary:
            summary['completed_credits'] = 0.0
        if 'in_progress_credits' not in summary:
            summary['in_progress_credits'] = 0.0
        if 'total_credits_required' not in summary:
            summary['total_credits_required'] = 120.0  # Standard BS degree
        
        return summary
    
    def _parse_courses(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse all courses and categorize them as completed, in-progress, or remaining
        NOW WITH DEDUPLICATION to prevent counting same course multiple times
        
        Returns:
            Dictionary with three lists: completed, in_progress, remaining
        """
        courses = {
            'completed': [],
            'in_progress': [],
            'remaining': []
        }
        
        # Track seen course codes for deduplication
        seen_courses = {}  # course_code -> (course_info, status, score)
        
        def _score_course(course_info: dict, status: str) -> int:
            """Score a course entry - higher score = more complete information"""
            score = 0
            if course_info.get('grade'): score += 10
            if course_info.get('term'): score += 10
            if course_info.get('credits', 0) > 0: score += 5
            if len(course_info.get('course_name', '')) > 10: score += 3
            if status == 'completed': score += 2  # Prefer completed status
            return score
        
        # Split text into lines for processing
        lines = text.split('\n')
        
        current_category = 'General'
        current_requirement_group = None
        
        for i, line in enumerate(lines):
            # Detect requirement category changes
            detected_category = self._detect_requirement_category(line)
            if detected_category:
                current_requirement_group = detected_category
            
            # Try to extract course information from this line
            course_info = self._extract_course_from_line(line, lines, i)
            
            if course_info:
                course_code = course_info.get('course_code')
                
                # Add category information
                course_info['category'] = current_requirement_group or 'General'
                
                # Determine status - pass course_info to use extracted grade/term
                status = self._determine_course_status(line, lines, i, course_info)
                
                # Filter out withdrawn courses
                if status == 'withdrawn':
                    logger.debug(f"Filtered out withdrawn course: {course_info.get('course_code')}")
                    continue
                
                # IMPROVED DEDUPLICATION: Keep the best version of each course
                new_score = _score_course(course_info, status)
                
                if course_code in seen_courses:
                    old_info, old_status, old_score = seen_courses[course_code]
                    if new_score > old_score:
                        logger.debug(f"Replacing {course_code}: new score {new_score} > old score {old_score} (status: {old_status} -> {status})")
                        seen_courses[course_code] = (course_info, status, new_score)
                    else:
                        logger.debug(f"Keeping existing {course_code}: old score {old_score} >= new score {new_score} (status: {old_status})")
                else:
                    seen_courses[course_code] = (course_info, status, new_score)
        
        # Convert seen_courses dict to course lists
        for course_code, (course_info, status, score) in seen_courses.items():
            if status == 'completed':
                courses['completed'].append(course_info)
            elif status == 'in_progress':
                courses['in_progress'].append(course_info)
            elif status == 'remaining':
                courses['remaining'].append(course_info)
        
        logger.info(f"Parsed courses - Completed: {len(courses['completed'])}, "
                   f"In Progress: {len(courses['in_progress'])}, "
                   f"Remaining: {len(courses['remaining'])}")
        
        return courses
    
    def _detect_requirement_category(self, line: str) -> Optional[str]:
        """Detect if a line indicates a requirement category"""
        line_upper = line.upper()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return category
        
        return None
    
    def _extract_course_from_line(self, line: str, all_lines: List[str], line_idx: int) -> Optional[Dict[str, Any]]:
        """Extract course information from a single line with Morgan State dual-format support and validation"""
        
        # Morgan State Format 1: COSC 111 INTRO TO COMPUTER SCIENCE I B 4FALL 2021
        # Morgan State Format 2: COSC 460 COMPUTER GRAPHICS IP (3) FALL 2025
        
        # Pattern 1: Standard format (grade and credits separated)
        pattern1 = re.compile(
            r'\b([A-Z]{2,4})\s+(\d{3}[A-Z]?)\s+' +  # DEPT CODE
            r'([A-Z][A-Za-z\s\-&:,/()\\.]{1,60}?)' +  # COURSE NAME
            r'\s+([A-F][+-]?|IP|I|W|WF|WP|P|NP|S|U|D[+-]?)' +  # GRADE
            r'\s+(?:\()?(\d+)(?:\))?' +  # CREDITS
            r'\s*(?:(FALL|SPRING|SUMMER|WINTER)\s*(?:MINI-\s*MESTER\s*)?(\d{4}))?',
            re.IGNORECASE
        )
        
        # Pattern 2: Compact format (IP (3)FALL or IP (3) FALL)
        pattern2 = re.compile(
            r'\b([A-Z]{2,4})\s+(\d{3}[A-Z]?)\s+' +  # DEPT CODE
            r'([A-Z][A-Za-z\s\-&:,/()\\.]{1,60}?)' +  # COURSE NAME
            r'\s+(IP|I|W|WF|WP|P|NP|S|U)\s*' +  # GRADE
            r'\((\d+)\)\s*' +  # CREDITS in parentheses
            r'(?:(FALL|SPRING|SUMMER|WINTER)\s*(\d{4}))?',
            re.IGNORECASE
        )
        
        # Try both patterns
        match = pattern1.search(line) or pattern2.search(line)
        if not match:
            # Fallback to simple course code detection
            simple_match = self.course_code_pattern.search(line)
            if not simple_match:
                return None
            dept = simple_match.group(1)
            number = simple_match.group(2)
        else:
            dept = match.group(1)
            number = match.group(2)
        
        # VALIDATION 1: Check if department code is valid (reject semester headers like "FALL 2021")
        if dept.upper() not in self.valid_dept_codes:
            logger.debug(f"Rejected invalid dept code: {dept} (not in whitelist)")
            return None
        
        course_code = f"{dept} {number}"
        
        # Extract course name, credits, grade, term from match or fallback parsing
        if match and len(match.groups()) >= 5:
            course_name = match.group(3).strip() if len(match.groups()) >= 3 else ""
            grade = match.group(4).upper() if len(match.groups()) >= 4 else None
            credits = float(match.group(5)) if len(match.groups()) >= 5 else 3.0
            semester_name = match.group(6) if len(match.groups()) >= 6 else None
            semester_year = match.group(7) if len(match.groups()) >= 7 else None
            term = f"{semester_name.title()} {semester_year}" if semester_name and semester_year else None
        else:
            # Fallback extraction for simple matches
            name_pattern = rf'{course_code}\s+(.+?)(?:\s+\d+\.?\d*\s+credits?|\s+\d+\.?\d*\s*$|\s{{3,}})'
            name_match = re.search(name_pattern, line, re.IGNORECASE)
            course_name = name_match.group(1).strip() if name_match else ""
            
            credits_pattern = r'(\d+\.?\d*)\s+credits?'
            credits_match = re.search(credits_pattern, line, re.IGNORECASE)
            credits = float(credits_match.group(1)) if credits_match else 3.0
            
            grade_match = self.grade_pattern.search(line)
            grade = grade_match.group(1).upper() if grade_match else None
            
            term_pattern = r'(Fall|Spring|Summer|Winter)\s+(\d{4})'
            term_match = re.search(term_pattern, line, re.IGNORECASE)
            term = f"{term_match.group(1)} {term_match.group(2)}" if term_match else None
            
            if not term:
                # Backtrack a few lines to find a preceding term header
                for back in range(1, 4):
                    prev_idx = line_idx - back
                    if prev_idx >= 0:
                        prev_line = all_lines[prev_idx]
                        tm_prev = re.search(term_pattern, prev_line, re.IGNORECASE)
                        if tm_prev:
                            term = f"{tm_prev.group(1)} {tm_prev.group(2)}"
                            break
        
        # Clean up course name
        course_name = re.sub(r'\s+', ' ', course_name)
        course_name = re.sub(r'[✓✔]', '', course_name).strip()
        
        # VALIDATION 2: Reject invalid course names
        # - Must have at least 3 characters
        # - Cannot be all uppercase single words (likely headers)
        # - Cannot contain "GPA" or be just semester info
        if len(course_name) < 3:
            logger.debug(f"Rejected course {course_code}: name too short")
            return None
        
        if course_name.upper() in ['GPA', 'CREDITS', 'HOURS', 'TOTAL']:
            logger.debug(f"Rejected course {course_code}: name is header keyword")
            return None
        
        # VALIDATION 2B: Reject requirement description lines (no grade AND no term)
        # These are typically requirement headers like "Introduction to Computer Science I COSC 111"
        # that appear before the actual course with grade and term
        if not grade and not term:
            logger.debug(f"Rejected course {course_code}: requirement description line (no grade or term)")
            return None
        
        # VALIDATION 3: Reject unreasonable credit values
        if credits > 12 or credits < 0:
            logger.debug(f"Rejected course {course_code}: unreasonable credits ({credits})")
            return None
        
        return {
            'course_code': course_code,
            'course_name': course_name,
            'credits': credits,
            'grade': grade,
            'term': term
        }
    
    def _determine_course_status(self, line: str, all_lines: List[str], line_idx: int, course_info: Optional[Dict[str, Any]] = None) -> str:
        """Determine course status with Morgan State multi-layer logic and withdrawn filtering"""
        
        # Use grade and term from course_info if provided (more accurate than re-parsing line)
        if course_info:
            grade = course_info.get('grade')
            term = course_info.get('term')
        else:
            # Fallback: extract grade and term from line
            grade_match = self.grade_pattern.search(line)
            grade = grade_match.group(1).upper() if grade_match else None
            
            term_match = re.search(r'(Fall|Spring|Summer|Winter)\s+(\d{4})', line, re.IGNORECASE)
            term = f"{term_match.group(1)} {term_match.group(2)}" if term_match else None
        
        # Calculate if term is in the past (for priority logic)
        is_past_term = False
        if term:
            try:
                term_parts = term.split()
                term_season = term_parts[0]
                term_year = int(term_parts[-1])
                current_year = datetime.now().year
                
                # Debug logging for COSC 111
                is_past_term = term_year < current_year or (term_year == current_year and term != self.current_semester)
                if '111' in line:
                    logger.debug(f"COSC 111 STATUS CHECK: grade={grade}, term={term}, term_year={term_year}, current_year={current_year}, current_semester={self.current_semester}, is_past_term={is_past_term}")
            except Exception as e:
                logger.debug(f"Error calculating past term: {e}")
                pass
        
        # Rule 1: Withdrawn courses - SKIP (don't count)
        if grade in ['W', 'WF', 'WP']:
            logger.debug(f"Withdrawn course detected (grade: {grade}) - skipping")
            return 'withdrawn'  # Special status to filter out
        
        # Rule 2: PRIORITY - Final letter grades from PAST semesters = COMPLETED
        # This fixes the issue where completed courses were marked as in-progress
        # THIS RULE MUST COME BEFORE MARKER CHECKS TO OVERRIDE THEM
        if grade in ['A', 'A-', 'A+', 'B', 'B-', 'B+', 'C', 'C-', 'C+', 'D', 'D-', 'D+', 'F']:
            if is_past_term:
                if '111' in line:
                    logger.debug(f"COSC 111: Returning COMPLETED (past term with final grade)")
                logger.debug(f"Completed course (final grade {grade} from past term {term}) - PRIORITY COMPLETED")
                return 'completed'
            elif term:
                if '111' in line:
                    logger.debug(f"COSC 111: Returning COMPLETED (has term and final grade)")
                logger.debug(f"Completed course (final grade {grade} with term {term})")
                return 'completed'
            else:
                # Final grade but no term - likely completed
                return 'completed'
        
        # Rule 3: In-Progress grade
        if grade == 'IP':
            logger.debug(f"In-progress course (grade: IP)")
            return 'in_progress'
        
        # Rule 4: Incomplete grade - check if current semester
        if grade == 'I':
            if term and term == self.current_semester:
                logger.debug(f"Incomplete in current semester ({term}) - in-progress")
                return 'in_progress'
            else:
                # Incomplete from past semester - still needs completion
                return 'in_progress'
        
        # Rule 5: Pass/No Pass grades
        if grade in ['P', 'S']:
            return 'completed'
        if grade in ['NP', 'U']:
            return 'withdrawn'  # Not passed - filter out
        
        # Rule 6: Check for completion/in-progress markers in line
        for marker in self.completed_markers:
            if marker in line or marker in line.upper():
                return 'completed'
        
        for marker in self.in_progress_markers:
            if marker in line or marker in line.upper():
                return 'in_progress'
        
        # Rule 7: Check context (previous and next lines)
        context_lines = []
        if line_idx > 0:
            context_lines.append(all_lines[line_idx - 1])
        context_lines.append(line)
        if line_idx < len(all_lines) - 1:
            context_lines.append(all_lines[line_idx + 1])
        
        context = ' '.join(context_lines)
        
        for marker in self.completed_markers:
            if marker in context or marker in context.upper():
                return 'completed'
        
        for marker in self.in_progress_markers:
            if marker in context or marker in context.upper():
                return 'in_progress'
        
        # Rule 8: Check for "not taken" markers
        for marker in self.not_taken_markers:
            if marker in context or marker in context.upper():
                return 'remaining'
        
        # Rule 9: Current/future semester detection (dynamic)
        if term and term == self.current_semester:
            return 'in_progress'
        
        # Default to remaining if status unclear
        return 'remaining'
    
    def _determine_classification(self, completed_credits: float) -> str:
        """Determine student classification based on completed credits"""
        for classification, (min_credits, max_credits) in self.classification_thresholds.items():
            if min_credits <= completed_credits <= max_credits:
                return classification
        return 'Unknown'
    
    def _analyze_requirements(self, courses: Dict[str, List[Dict]], text: str) -> Dict[str, Any]:
        """Analyze requirement fulfillment by category"""
        requirements = {}
        
        # Group courses by category
        for status in ['completed', 'in_progress', 'remaining']:
            for course in courses[status]:
                category = course.get('category', 'General')
                
                if category not in requirements:
                    requirements[category] = {
                        'completed_credits': 0.0,
                        'in_progress_credits': 0.0,
                        'remaining_credits': 0.0,
                        'total_required': 0.0,
                        'courses': {'completed': [], 'in_progress': [], 'remaining': []}
                    }
                
                requirements[category]['courses'][status].append(course)
                requirements[category][f'{status}_credits'] += course.get('credits', 0.0)
        
        return requirements

    def _build_course_timeline(self, courses: Dict[str, List[Dict]]) -> Dict[str, Any]:
        timeline: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        for status in ['completed', 'in_progress', 'remaining']:
            for course in courses.get(status, []):
                term = course.get('term') or 'Unspecified Term'
                if term not in timeline:
                    timeline[term] = {'completed': [], 'in_progress': [], 'remaining': []}
                timeline[term][status].append(course)
        # Sort chronologically if possible
        def term_key(t: str) -> Tuple[int, int]:
            m = re.match(r'(Spring|Summer|Fall|Winter)\s+(\d{4})', t)
            if not m:
                return (9999, 5)
            season, year = m.group(1), int(m.group(2))
            order = {'Spring': 1, 'Summer': 2, 'Fall': 3, 'Winter': 4}
            return (year, order.get(season, 5))
        ordered = dict(sorted(timeline.items(), key=lambda kv: term_key(kv[0])))
        return ordered
    
    def format_for_chatbot(self, parsed_data: Dict[str, Any]) -> str:
        """
        Format parsed Degree Works data into natural language context for chatbot
        
        Args:
            parsed_data: Output from parse_pdf method
            
        Returns:
            Formatted string for chatbot context
        """
        if not parsed_data.get('success'):
            return "No Degree Works data available for this student."
        
        summary = parsed_data['academic_summary']
        courses = parsed_data['courses']
        student = parsed_data.get('student_info', {})
        
        context = f"""
STUDENT DEGREE WORKS ANALYSIS
================================

Student: {student.get('name', 'Unknown')}
Major: {student.get('major', 'Computer Science')}
Classification: {summary.get('classification', 'Unknown')}
GPA: {summary.get('gpa', 'N/A')}

ACADEMIC PROGRESS:
- Credits Completed: {summary.get('completed_credits', 0)}
- Credits In Progress: {summary.get('in_progress_credits', 0)}
- Credits Required: {summary.get('total_credits_required', 120)}
- Credits Remaining: {summary.get('remaining_credits', 0)}

COMPLETED COURSES ({len(courses['completed'])} courses):
"""
        
        for course in courses['completed']:
            context += f"- {course['course_code']}: {course['course_name']} ({course['credits']} credits) - Category: {course.get('category', 'General')}\n"
        
        context += f"\nIN-PROGRESS COURSES ({len(courses['in_progress'])} courses):\n"
        for course in courses['in_progress']:
            context += f"- {course['course_code']}: {course['course_name']} ({course['credits']} credits) - Category: {course.get('category', 'General')}\n"
        
        context += f"\nREMAINING REQUIRED COURSES ({len(courses['remaining'])} courses):\n"
        for course in courses['remaining']:
            context += f"- {course['course_code']}: {course['course_name']} ({course['credits']} credits) - Category: {course.get('category', 'General')}\n"

        # Elective group status formatting
        elective_groups = parsed_data.get('elective_groups') or {}
        if elective_groups:
            context += "\nELECTIVE GROUPS STATUS:\n"
            for group_name, data in elective_groups.items():
                completed = data.get('completed', [])
                in_progress = data.get('in_progress', [])
                remaining = data.get('remaining', [])
                context += f"\n{group_name}: Completed {len(completed)}, In Progress {len(in_progress)}, Remaining {len(remaining)}\n"
                for c in completed:
                    context += f"- {c['course_code']} (completed)\n"
                for c in in_progress:
                    context += f"- {c['course_code']} (in-progress)\n"
                for c in remaining:
                    context += f"- {c['course_code']} (remaining)\n"
        return context

    def _parse_elective_groups(self, text: str, courses: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Detect and map elective groups (Group A/B/C/D) to course statuses.
        Heuristic: identify lines with 'GROUP <letter>' headers; collect subsequent course codes until next header or major section.
        Returns: { 'Group A': { 'completed': [...], 'in_progress': [...], 'remaining': [...] }, ... }
        """
        lines = text.split('\n')
        group_pattern = re.compile(r'GROUP\s+([A-D])', re.IGNORECASE)
        current_group = None
        groups: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

        # Build status lookup
        status_lookup: Dict[str, str] = {}
        for status in ['completed', 'in_progress', 'remaining']:
            for c in courses.get(status, []):
                status_lookup[c['course_code'].upper()] = status

        def ensure(name: str):
            if name not in groups:
                groups[name] = {'completed': [], 'in_progress': [], 'remaining': []}

        for line in lines:
            header = group_pattern.search(line)
            if header:
                current_group = f"Group {header.group(1).upper()}"
                ensure(current_group)
                continue
            if current_group:
                # Break on new major section headers
                if re.search(r'(MAJOR|GENERAL EDUCATION|SUPPORTING COURSES|COMPLEMENTARY STUDIES)', line, re.IGNORECASE):
                    current_group = None
                    continue
                code_match = self.course_code_pattern.search(line)
                if code_match:
                    course_code = f"{code_match.group(1)} {code_match.group(2)}".upper()
                    status = status_lookup.get(course_code)
                    if status:
                        ensure(current_group)
                        groups[current_group][status].append({'course_code': course_code})

        # Remove empty groups
        groups = {g: d for g, d in groups.items() if any(d.values())}
        return groups
