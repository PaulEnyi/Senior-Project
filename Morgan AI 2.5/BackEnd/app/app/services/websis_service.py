"""
WebSIS Integration Service
Securely connects to Morgan State University's WebSIS to fetch student academic data
"""

import logging
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import json

logger = logging.getLogger(__name__)

class WebSISService:
    """
    Service to interact with Morgan State University's WebSIS system
    Fetches student academic data including:
    - Course registration information
    - Academic history
    - Grade reports
    - Class schedules
    - Registration holds
    """
    
    def __init__(self):
        self.base_url = "https://websis.morgan.edu"
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)  # Cache data for 1 hour
        
    async def initialize(self):
        """Initialize the service and create HTTP session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'MorganAI-Assistant/2.5 (Academic Integration)',
                    'Accept': 'text/html,application/json'
                }
            )
        logger.info("WebSIS service initialized")
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key from endpoint and parameters"""
        param_str = json.dumps(params, sort_keys=True)
        return f"{endpoint}:{param_str}"
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry:
            return False
        timestamp = cache_entry.get('timestamp')
        if not timestamp:
            return False
        return datetime.now() - timestamp < self.cache_ttl
    
    async def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate with WebSIS using student credentials
        
        Args:
            username: Student username/ID
            password: Student password
            
        Returns:
            Authentication result with session token
        """
        try:
            await self.initialize()
            
            # WebSIS authentication endpoint
            auth_url = urljoin(self.base_url, "/pls/prod/twbkwbis.P_ValLogin")
            
            auth_data = {
                'sid': username,
                'PIN': password
            }
            
            async with self.session.post(auth_url, data=auth_data, allow_redirects=True) as response:
                if response.status == 200:
                    # Check if authentication was successful
                    text = await response.text()
                    if "Invalid" not in text and "Error" not in text:
                        logger.info(f"Successfully authenticated user: {username}")
                        return {
                            'success': True,
                            'message': 'Authentication successful',
                            'session_id': response.cookies.get('SESSID'),
                            'user_id': username
                        }
                    else:
                        logger.warning(f"Authentication failed for user: {username}")
                        return {
                            'success': False,
                            'message': 'Invalid credentials'
                        }
                else:
                    logger.error(f"WebSIS authentication error: HTTP {response.status}")
                    return {
                        'success': False,
                        'message': f'Authentication failed: HTTP {response.status}'
                    }
                    
        except Exception as e:
            logger.error(f"WebSIS authentication exception: {str(e)}")
            return {
                'success': False,
                'message': f'Authentication error: {str(e)}'
            }
    
    async def fetch_student_schedule(self, session_id: str, term_code: str = None) -> Dict[str, Any]:
        """
        Fetch student's current class schedule
        
        Args:
            session_id: Authenticated session ID
            term_code: Term code (e.g., "202501" for Spring 2025)
            
        Returns:
            Student's class schedule with course details
        """
        cache_key = self._get_cache_key('schedule', {'session_id': session_id, 'term': term_code})
        cached = self.cache.get(cache_key)
        if cached and self._is_cache_valid(cached):
            logger.info("Returning cached schedule data")
            return cached['data']
        
        try:
            await self.initialize()
            
            # Default to current term if not specified
            if not term_code:
                term_code = self._get_current_term_code()
            
            schedule_url = urljoin(self.base_url, f"/pls/prod/bwskfshd.P_CrseSchdDetl")
            
            params = {
                'term_in': term_code
            }
            
            cookies = {'SESSID': session_id}
            
            async with self.session.get(schedule_url, params=params, cookies=cookies) as response:
                if response.status == 200:
                    html = await response.text()
                    schedule_data = self._parse_schedule_html(html)
                    
                    # Cache the result
                    self.cache[cache_key] = {
                        'data': schedule_data,
                        'timestamp': datetime.now()
                    }
                    
                    logger.info(f"Successfully fetched schedule for term {term_code}")
                    return schedule_data
                else:
                    logger.error(f"Failed to fetch schedule: HTTP {response.status}")
                    return {
                        'success': False,
                        'message': f'Failed to fetch schedule: HTTP {response.status}',
                        'courses': []
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching student schedule: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'courses': []
            }
    
    async def fetch_grades(self, session_id: str, term_code: str = None) -> Dict[str, Any]:
        """
        Fetch student's grades
        
        Args:
            session_id: Authenticated session ID
            term_code: Term code (optional, defaults to all terms)
            
        Returns:
            Student's grades and GPA information
        """
        cache_key = self._get_cache_key('grades', {'session_id': session_id, 'term': term_code})
        cached = self.cache.get(cache_key)
        if cached and self._is_cache_valid(cached):
            logger.info("Returning cached grades data")
            return cached['data']
        
        try:
            await self.initialize()
            
            grades_url = urljoin(self.base_url, "/pls/prod/bwskogrd.P_ViewGrde")
            
            cookies = {'SESSID': session_id}
            
            async with self.session.get(grades_url, cookies=cookies) as response:
                if response.status == 200:
                    html = await response.text()
                    grades_data = self._parse_grades_html(html, term_code)
                    
                    # Cache the result
                    self.cache[cache_key] = {
                        'data': grades_data,
                        'timestamp': datetime.now()
                    }
                    
                    logger.info("Successfully fetched grades")
                    return grades_data
                else:
                    logger.error(f"Failed to fetch grades: HTTP {response.status}")
                    return {
                        'success': False,
                        'message': f'Failed to fetch grades: HTTP {response.status}',
                        'grades': []
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching grades: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'grades': []
            }
    
    async def fetch_registration_status(self, session_id: str) -> Dict[str, Any]:
        """
        Check registration status and holds
        
        Args:
            session_id: Authenticated session ID
            
        Returns:
            Registration status, holds, and eligibility information
        """
        try:
            await self.initialize()
            
            reg_url = urljoin(self.base_url, "/pls/prod/bwsksreg.p_reg_status")
            
            cookies = {'SESSID': session_id}
            
            async with self.session.get(reg_url, cookies=cookies) as response:
                if response.status == 200:
                    html = await response.text()
                    reg_data = self._parse_registration_html(html)
                    
                    logger.info("Successfully fetched registration status")
                    return reg_data
                else:
                    logger.error(f"Failed to fetch registration status: HTTP {response.status}")
                    return {
                        'success': False,
                        'message': f'Failed to fetch registration status: HTTP {response.status}',
                        'holds': [],
                        'can_register': False
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching registration status: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'holds': [],
                'can_register': False
            }
    
    async def search_courses(self, term_code: str, subject: str = None, course_number: str = None) -> Dict[str, Any]:
        """
        Search for available courses
        
        Args:
            term_code: Term code (e.g., "202501")
            subject: Subject code (e.g., "COSC" for Computer Science)
            course_number: Specific course number (optional)
            
        Returns:
            List of available courses with details
        """
        try:
            await self.initialize()
            
            search_url = urljoin(self.base_url, "/pls/prod/bwckschd.p_get_crse_unsec")
            
            params = {
                'term_in': term_code,
                'sel_subj': 'dummy',
                'sel_subj': subject or 'COSC',
                'SEL_CRSE': course_number or '',
                'SEL_TITLE': '',
                'BEGIN_HH': '0',
                'BEGIN_MI': '0',
                'BEGIN_AP': 'a',
                'SEL_DAY': 'dummy',
                'SEL_PTRM': 'dummy',
                'END_HH': '0',
                'END_MI': '0',
                'END_AP': 'a',
                'SEL_CAMP': 'dummy',
                'SEL_SCHD': 'dummy',
                'SEL_SESS': 'dummy',
                'SEL_INSTR': 'dummy',
                'SEL_ATTR': 'dummy',
                'SEL_LEVL': 'dummy',
                'SEL_INSM': 'dummy',
                'sel_dunt_code': '',
                'sel_dunt_unit': '',
                'call_value_in': '',
                'rsts': 'dummy',
                'crn': 'dummy',
                'path': '1',
                'SUB_BTN': 'Course Search'
            }
            
            async with self.session.post(search_url, data=params) as response:
                if response.status == 200:
                    html = await response.text()
                    courses_data = self._parse_course_search_html(html)
                    
                    logger.info(f"Successfully searched courses for {subject} {course_number or ''}")
                    return courses_data
                else:
                    logger.error(f"Failed to search courses: HTTP {response.status}")
                    return {
                        'success': False,
                        'message': f'Failed to search courses: HTTP {response.status}',
                        'courses': []
                    }
                    
        except Exception as e:
            logger.error(f"Error searching courses: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'courses': []
            }
    
    def _get_current_term_code(self) -> str:
        """
        Generate current term code based on date
        Format: YYYYMM where MM is 01 (Spring), 05 (Summer), 09 (Fall)
        """
        now = datetime.now()
        year = now.year
        month = now.month
        
        if month >= 1 and month <= 5:
            return f"{year}01"  # Spring
        elif month >= 6 and month <= 8:
            return f"{year}05"  # Summer
        else:
            return f"{year}09"  # Fall
    
    def _parse_schedule_html(self, html: str) -> Dict[str, Any]:
        """Parse HTML response for class schedule"""
        soup = BeautifulSoup(html, 'html.parser')
        courses = []
        
        try:
            # Find all course entries
            course_tables = soup.find_all('table', class_='datadisplaytable')
            
            for table in course_tables:
                course_info = {}
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        if 'CRN' in label:
                            course_info['crn'] = value
                        elif 'Course' in label:
                            course_info['course'] = value
                        elif 'Title' in label:
                            course_info['title'] = value
                        elif 'Instructor' in label:
                            course_info['instructor'] = value
                        elif 'Time' in label:
                            course_info['time'] = value
                        elif 'Location' in label:
                            course_info['location'] = value
                        elif 'Credits' in label:
                            course_info['credits'] = value
                
                if course_info:
                    courses.append(course_info)
            
            return {
                'success': True,
                'courses': courses,
                'total_courses': len(courses)
            }
            
        except Exception as e:
            logger.error(f"Error parsing schedule HTML: {str(e)}")
            return {
                'success': False,
                'message': f'Parsing error: {str(e)}',
                'courses': []
            }
    
    def _parse_grades_html(self, html: str, term_code: str = None) -> Dict[str, Any]:
        """Parse HTML response for grades"""
        soup = BeautifulSoup(html, 'html.parser')
        grades = []
        gpa_info = {}
        
        try:
            # Find grade tables
            tables = soup.find_all('table', class_='datadisplaytable')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 5:
                        grade_entry = {
                            'course': cells[0].get_text(strip=True),
                            'title': cells[1].get_text(strip=True),
                            'credits': cells[2].get_text(strip=True),
                            'grade': cells[3].get_text(strip=True),
                            'quality_points': cells[4].get_text(strip=True) if len(cells) > 4 else ''
                        }
                        grades.append(grade_entry)
            
            # Extract GPA information
            gpa_section = soup.find('table', class_='plaintable')
            if gpa_section:
                gpa_text = gpa_section.get_text()
                gpa_match = re.search(r'GPA:\s*(\d+\.\d+)', gpa_text)
                if gpa_match:
                    gpa_info['current_gpa'] = float(gpa_match.group(1))
            
            return {
                'success': True,
                'grades': grades,
                'gpa_info': gpa_info,
                'total_courses': len(grades)
            }
            
        except Exception as e:
            logger.error(f"Error parsing grades HTML: {str(e)}")
            return {
                'success': False,
                'message': f'Parsing error: {str(e)}',
                'grades': []
            }
    
    def _parse_registration_html(self, html: str) -> Dict[str, Any]:
        """Parse HTML response for registration status"""
        soup = BeautifulSoup(html, 'html.parser')
        holds = []
        can_register = True
        
        try:
            # Find holds section
            hold_tables = soup.find_all('table', class_='datadisplaytable')
            
            for table in hold_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if cells and 'HOLD' in cells[0].get_text().upper():
                        hold_info = {
                            'type': cells[0].get_text(strip=True),
                            'description': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                            'date': cells[2].get_text(strip=True) if len(cells) > 2 else ''
                        }
                        holds.append(hold_info)
                        can_register = False
            
            return {
                'success': True,
                'holds': holds,
                'can_register': can_register,
                'message': 'No registration holds' if can_register else 'Registration holds present'
            }
            
        except Exception as e:
            logger.error(f"Error parsing registration HTML: {str(e)}")
            return {
                'success': False,
                'message': f'Parsing error: {str(e)}',
                'holds': [],
                'can_register': False
            }
    
    def _parse_course_search_html(self, html: str) -> Dict[str, Any]:
        """Parse HTML response for course search results"""
        soup = BeautifulSoup(html, 'html.parser')
        courses = []
        
        try:
            # Find course listing tables
            course_sections = soup.find_all('table', class_='datadisplaytable')
            
            for table in course_sections:
                course_info = {}
                caption = table.find('caption')
                if caption:
                    course_info['title'] = caption.get_text(strip=True)
                
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        if 'CRN' in label:
                            course_info['crn'] = value
                        elif 'Subject' in label:
                            course_info['subject'] = value
                        elif 'Course' in label:
                            course_info['course_number'] = value
                        elif 'Seats' in label:
                            course_info['seats'] = value
                        elif 'Instructor' in label:
                            course_info['instructor'] = value
                        elif 'Days' in label:
                            course_info['days'] = value
                        elif 'Time' in label:
                            course_info['time'] = value
                        elif 'Location' in label:
                            course_info['location'] = value
                
                if course_info:
                    courses.append(course_info)
            
            return {
                'success': True,
                'courses': courses,
                'total_results': len(courses)
            }
            
        except Exception as e:
            logger.error(f"Error parsing course search HTML: {str(e)}")
            return {
                'success': False,
                'message': f'Parsing error: {str(e)}',
                'courses': []
            }


# Singleton instance
websis_service = WebSISService()
