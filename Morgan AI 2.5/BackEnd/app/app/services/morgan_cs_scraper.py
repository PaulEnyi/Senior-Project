"""
Morgan State CS Department Web Scraper Service
Automatically fetches and updates information from Morgan CS website
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

class MorganCSScraperService:
    """
    Service to scrape and update information from Morgan State CS website
    Fetches:
    - Faculty information
    - Course catalog
    - News and announcements
    - Events
    - Research areas
    - Student resources
    """
    
    def __init__(self):
        self.base_url = "https://www.morgan.edu/school-of-computer-mathematical-and-natural-sciences/departments/computer-science"
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_scrape: Optional[datetime] = None
        self.scraped_data: Dict[str, Any] = {
            'faculty': [],
            'courses': [],
            'news': [],
            'events': [],
            'resources': [],
            'research_areas': []
        }
        
    async def initialize(self):
        """Initialize the scraper service"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=60)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'MorganAI-Assistant/2.5 (Academic Information Aggregator)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
            )
        logger.info("Morgan CS Scraper service initialized")
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def scrape_all(self) -> Dict[str, Any]:
        """
        Scrape all information from Morgan CS website
        
        Returns:
            Complete scraped data from all sources
        """
        try:
            await self.initialize()
            
            logger.info("Starting comprehensive Morgan CS website scrape...")
            
            # Run all scraping tasks concurrently
            results = await asyncio.gather(
                self.scrape_faculty(),
                self.scrape_courses(),
                self.scrape_news(),
                self.scrape_events(),
                self.scrape_resources(),
                self.scrape_research_areas(),
                return_exceptions=True
            )
            
            # Update scraped data with results
            self.scraped_data['faculty'] = results[0] if not isinstance(results[0], Exception) else []
            self.scraped_data['courses'] = results[1] if not isinstance(results[1], Exception) else []
            self.scraped_data['news'] = results[2] if not isinstance(results[2], Exception) else []
            self.scraped_data['events'] = results[3] if not isinstance(results[3], Exception) else []
            self.scraped_data['resources'] = results[4] if not isinstance(results[4], Exception) else []
            self.scraped_data['research_areas'] = results[5] if not isinstance(results[5], Exception) else []
            
            self.last_scrape = datetime.now()
            
            logger.info("Completed Morgan CS website scrape")
            
            return {
                'success': True,
                'data': self.scraped_data,
                'timestamp': self.last_scrape.isoformat(),
                'summary': {
                    'faculty_count': len(self.scraped_data['faculty']),
                    'courses_count': len(self.scraped_data['courses']),
                    'news_count': len(self.scraped_data['news']),
                    'events_count': len(self.scraped_data['events']),
                    'resources_count': len(self.scraped_data['resources']),
                    'research_areas_count': len(self.scraped_data['research_areas'])
                }
            }
            
        except Exception as e:
            logger.error(f"Error during comprehensive scrape: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': self.scraped_data
            }
    
    async def scrape_faculty(self) -> List[Dict[str, Any]]:
        """
        Scrape faculty information
        
        Returns:
            List of faculty members with details
        """
        try:
            faculty_url = urljoin(self.base_url, "/faculty-and-staff")
            
            async with self.session.get(faculty_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    faculty = []
                    
                    # Find faculty listings
                    faculty_sections = soup.find_all(['div', 'article'], class_=re.compile(r'faculty|profile|staff'))
                    
                    for section in faculty_sections:
                        name_elem = section.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'name|title'))
                        title_elem = section.find(['p', 'span'], class_=re.compile(r'title|position|role'))
                        email_elem = section.find('a', href=re.compile(r'mailto:'))
                        office_elem = section.find(['p', 'span'], string=re.compile(r'office|room', re.I))
                        phone_elem = section.find(['p', 'span'], string=re.compile(r'phone|\(\d{3}\)', re.I))
                        
                        if name_elem:
                            faculty_info = {
                                'name': name_elem.get_text(strip=True),
                                'title': title_elem.get_text(strip=True) if title_elem else 'Faculty',
                                'email': email_elem.get('href').replace('mailto:', '') if email_elem else '',
                                'office': office_elem.get_text(strip=True) if office_elem else '',
                                'phone': phone_elem.get_text(strip=True) if phone_elem else '',
                                'department': 'Computer Science',
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            # Get bio/research interests if available
                            bio_elem = section.find(['p', 'div'], class_=re.compile(r'bio|description|research'))
                            if bio_elem:
                                faculty_info['bio'] = bio_elem.get_text(strip=True)[:500]  # Limit length
                            
                            faculty.append(faculty_info)
                    
                    logger.info(f"Scraped {len(faculty)} faculty members")
                    return faculty
                else:
                    logger.error(f"Failed to scrape faculty: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error scraping faculty: {str(e)}")
            return []
    
    async def scrape_courses(self) -> List[Dict[str, Any]]:
        """
        Scrape course catalog information
        
        Returns:
            List of courses with details
        """
        try:
            courses_url = urljoin(self.base_url, "/courses")
            
            async with self.session.get(courses_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    courses = []
                    
                    # Find course listings
                    course_sections = soup.find_all(['div', 'li'], class_=re.compile(r'course'))
                    
                    for section in course_sections:
                        # Extract course code (e.g., "COSC 111")
                        code_elem = section.find(['strong', 'b', 'span'], string=re.compile(r'COSC\s+\d{3}'))
                        title_elem = section.find(['h3', 'h4', 'strong'])
                        desc_elem = section.find(['p', 'div'], class_=re.compile(r'description'))
                        credits_match = re.search(r'(\d+)\s+credit', section.get_text())
                        
                        if code_elem or title_elem:
                            course_text = code_elem.get_text(strip=True) if code_elem else title_elem.get_text(strip=True)
                            code_match = re.search(r'(COSC)\s+(\d{3})', course_text)
                            
                            if code_match:
                                course_info = {
                                    'subject': code_match.group(1),
                                    'course_number': code_match.group(2),
                                    'code': f"{code_match.group(1)} {code_match.group(2)}",
                                    'title': title_elem.get_text(strip=True) if title_elem else course_text,
                                    'description': desc_elem.get_text(strip=True) if desc_elem else '',
                                    'credits': int(credits_match.group(1)) if credits_match else 3,
                                    'department': 'Computer Science',
                                    'scraped_at': datetime.now().isoformat()
                                }
                                
                                # Extract prerequisites if mentioned
                                prereq_match = re.search(r'Prerequisite[s]?:\s*([^.]+)', section.get_text(), re.I)
                                if prereq_match:
                                    course_info['prerequisites'] = prereq_match.group(1).strip()
                                
                                courses.append(course_info)
                    
                    logger.info(f"Scraped {len(courses)} courses")
                    return courses
                else:
                    logger.error(f"Failed to scrape courses: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error scraping courses: {str(e)}")
            return []
    
    async def scrape_news(self) -> List[Dict[str, Any]]:
        """
        Scrape department news and announcements
        
        Returns:
            List of news items
        """
        try:
            news_url = urljoin(self.base_url, "/news")
            
            async with self.session.get(news_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    news_items = []
                    
                    # Find news articles
                    articles = soup.find_all(['article', 'div'], class_=re.compile(r'news|article|post'))
                    
                    for article in articles[:20]:  # Limit to 20 most recent
                        title_elem = article.find(['h2', 'h3', 'h4', 'a'])
                        date_elem = article.find(['time', 'span'], class_=re.compile(r'date|time'))
                        summary_elem = article.find(['p', 'div'], class_=re.compile(r'summary|excerpt'))
                        link_elem = article.find('a', href=True)
                        
                        if title_elem:
                            news_info = {
                                'title': title_elem.get_text(strip=True),
                                'date': date_elem.get_text(strip=True) if date_elem else 'Recent',
                                'summary': summary_elem.get_text(strip=True)[:300] if summary_elem else '',
                                'url': urljoin(self.base_url, link_elem['href']) if link_elem else '',
                                'category': 'Department News',
                                'scraped_at': datetime.now().isoformat()
                            }
                            news_items.append(news_info)
                    
                    logger.info(f"Scraped {len(news_items)} news items")
                    return news_items
                else:
                    logger.error(f"Failed to scrape news: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error scraping news: {str(e)}")
            return []
    
    async def scrape_events(self) -> List[Dict[str, Any]]:
        """
        Scrape upcoming department events
        
        Returns:
            List of events
        """
        try:
            events_url = urljoin(self.base_url, "/events")
            
            async with self.session.get(events_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    events = []
                    
                    # Find event listings
                    event_sections = soup.find_all(['div', 'li', 'article'], class_=re.compile(r'event'))
                    
                    for section in event_sections[:15]:  # Limit to 15 upcoming
                        title_elem = section.find(['h2', 'h3', 'h4'])
                        date_elem = section.find(['time', 'span'], class_=re.compile(r'date'))
                        location_elem = section.find(['span', 'p'], class_=re.compile(r'location|venue'))
                        desc_elem = section.find(['p', 'div'], class_=re.compile(r'description'))
                        
                        if title_elem:
                            event_info = {
                                'title': title_elem.get_text(strip=True),
                                'date': date_elem.get_text(strip=True) if date_elem else 'TBA',
                                'location': location_elem.get_text(strip=True) if location_elem else 'TBA',
                                'description': desc_elem.get_text(strip=True)[:300] if desc_elem else '',
                                'department': 'Computer Science',
                                'scraped_at': datetime.now().isoformat()
                            }
                            events.append(event_info)
                    
                    logger.info(f"Scraped {len(events)} events")
                    return events
                else:
                    logger.error(f"Failed to scrape events: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error scraping events: {str(e)}")
            return []
    
    async def scrape_resources(self) -> List[Dict[str, Any]]:
        """
        Scrape student resources
        
        Returns:
            List of resources
        """
        try:
            resources_url = urljoin(self.base_url, "/student-resources")
            
            async with self.session.get(resources_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    resources = []
                    
                    # Find resource listings
                    resource_sections = soup.find_all(['div', 'li'], class_=re.compile(r'resource|service'))
                    
                    for section in resource_sections:
                        title_elem = section.find(['h3', 'h4', 'a', 'strong'])
                        desc_elem = section.find(['p', 'span'])
                        link_elem = section.find('a', href=True)
                        
                        if title_elem:
                            resource_info = {
                                'title': title_elem.get_text(strip=True),
                                'description': desc_elem.get_text(strip=True) if desc_elem else '',
                                'url': urljoin(self.base_url, link_elem['href']) if link_elem else '',
                                'category': 'Student Resource',
                                'scraped_at': datetime.now().isoformat()
                            }
                            resources.append(resource_info)
                    
                    logger.info(f"Scraped {len(resources)} resources")
                    return resources
                else:
                    logger.error(f"Failed to scrape resources: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error scraping resources: {str(e)}")
            return []
    
    async def scrape_research_areas(self) -> List[Dict[str, Any]]:
        """
        Scrape research areas and focus topics
        
        Returns:
            List of research areas
        """
        try:
            research_url = urljoin(self.base_url, "/research")
            
            async with self.session.get(research_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    research_areas = []
                    
                    # Find research area listings
                    area_sections = soup.find_all(['div', 'li'], class_=re.compile(r'research|area'))
                    
                    for section in area_sections:
                        title_elem = section.find(['h3', 'h4', 'strong'])
                        desc_elem = section.find(['p', 'div'])
                        
                        if title_elem:
                            area_info = {
                                'area': title_elem.get_text(strip=True),
                                'description': desc_elem.get_text(strip=True)[:500] if desc_elem else '',
                                'department': 'Computer Science',
                                'scraped_at': datetime.now().isoformat()
                            }
                            research_areas.append(area_info)
                    
                    logger.info(f"Scraped {len(research_areas)} research areas")
                    return research_areas
                else:
                    logger.error(f"Failed to scrape research areas: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error scraping research areas: {str(e)}")
            return []
    
    async def update_knowledge_base(self) -> Dict[str, Any]:
        """
        Update knowledge base with freshly scraped data
        
        Returns:
            Update status and statistics
        """
        try:
            # Scrape all data
            scrape_result = await self.scrape_all()
            
            if not scrape_result['success']:
                return scrape_result
            
            # Save scraped data to knowledge base directory
            from app.core.config import settings
            from pathlib import Path
            
            knowledge_base_dir = settings.KNOWLEDGE_BASE_DIR
            cs_dept_dir = knowledge_base_dir / "department_info"
            cs_dept_dir.mkdir(parents=True, exist_ok=True)
            
            # Save faculty data
            faculty_file = cs_dept_dir / "faculty.json"
            with open(faculty_file, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data['faculty'], f, indent=2, ensure_ascii=False)
            
            # Save courses data
            courses_file = cs_dept_dir / "courses.json"
            with open(courses_file, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data['courses'], f, indent=2, ensure_ascii=False)
            
            # Save news data
            news_file = cs_dept_dir / "news.json"
            with open(news_file, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data['news'], f, indent=2, ensure_ascii=False)
            
            # Save events data
            events_file = cs_dept_dir / "events.json"
            with open(events_file, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data['events'], f, indent=2, ensure_ascii=False)
            
            # Save resources data
            resources_file = cs_dept_dir / "resources.json"
            with open(resources_file, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data['resources'], f, indent=2, ensure_ascii=False)
            
            # Save research areas data
            research_file = cs_dept_dir / "research_areas.json"
            with open(research_file, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data['research_areas'], f, indent=2, ensure_ascii=False)
            
            # Create consolidated text file for RAG
            consolidated_file = cs_dept_dir / "cs_department_info.txt"
            with open(consolidated_file, 'w', encoding='utf-8') as f:
                f.write("MORGAN STATE UNIVERSITY - COMPUTER SCIENCE DEPARTMENT\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("FACULTY MEMBERS\n")
                f.write("-" * 80 + "\n")
                for faculty in self.scraped_data['faculty']:
                    f.write(f"Name: {faculty['name']}\n")
                    f.write(f"Title: {faculty['title']}\n")
                    f.write(f"Email: {faculty['email']}\n")
                    if faculty.get('office'):
                        f.write(f"Office: {faculty['office']}\n")
                    if faculty.get('phone'):
                        f.write(f"Phone: {faculty['phone']}\n")
                    if faculty.get('bio'):
                        f.write(f"Bio: {faculty['bio']}\n")
                    f.write("\n")
                
                f.write("\n" + "=" * 80 + "\n\n")
                f.write("COURSE CATALOG\n")
                f.write("-" * 80 + "\n")
                for course in self.scraped_data['courses']:
                    f.write(f"Course: {course['code']} - {course['title']}\n")
                    f.write(f"Credits: {course['credits']}\n")
                    f.write(f"Description: {course['description']}\n")
                    if course.get('prerequisites'):
                        f.write(f"Prerequisites: {course['prerequisites']}\n")
                    f.write("\n")
                
                f.write("\n" + "=" * 80 + "\n\n")
                f.write("RECENT NEWS & ANNOUNCEMENTS\n")
                f.write("-" * 80 + "\n")
                for news in self.scraped_data['news'][:10]:
                    f.write(f"Title: {news['title']}\n")
                    f.write(f"Date: {news['date']}\n")
                    f.write(f"Summary: {news['summary']}\n")
                    f.write("\n")
                
                f.write("\n" + "=" * 80 + "\n\n")
                f.write("UPCOMING EVENTS\n")
                f.write("-" * 80 + "\n")
                for event in self.scraped_data['events'][:10]:
                    f.write(f"Event: {event['title']}\n")
                    f.write(f"Date: {event['date']}\n")
                    f.write(f"Location: {event['location']}\n")
                    f.write(f"Description: {event['description']}\n")
                    f.write("\n")
                
                f.write("\n" + "=" * 80 + "\n\n")
                f.write("STUDENT RESOURCES\n")
                f.write("-" * 80 + "\n")
                for resource in self.scraped_data['resources']:
                    f.write(f"Resource: {resource['title']}\n")
                    f.write(f"Description: {resource['description']}\n")
                    if resource['url']:
                        f.write(f"URL: {resource['url']}\n")
                    f.write("\n")
                
                f.write("\n" + "=" * 80 + "\n\n")
                f.write("RESEARCH AREAS\n")
                f.write("-" * 80 + "\n")
                for area in self.scraped_data['research_areas']:
                    f.write(f"Area: {area['area']}\n")
                    f.write(f"Description: {area['description']}\n")
                    f.write("\n")
            
            logger.info("Successfully updated knowledge base with scraped data")
            
            return {
                'success': True,
                'message': 'Knowledge base updated successfully',
                'files_created': 7,
                'summary': scrape_result['summary']
            }
            
        except Exception as e:
            logger.error(f"Error updating knowledge base: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_cached_data(self) -> Dict[str, Any]:
        """
        Get cached scraped data
        
        Returns:
            Cached data with timestamp
        """
        return {
            'data': self.scraped_data,
            'last_scrape': self.last_scrape.isoformat() if self.last_scrape else None,
            'is_fresh': (datetime.now() - self.last_scrape) < timedelta(hours=24) if self.last_scrape else False
        }


# Singleton instance
morgan_cs_scraper = MorganCSScraperService()
