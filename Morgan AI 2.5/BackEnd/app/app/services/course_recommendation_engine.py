"""
Intelligent Course Recommendation Engine
Analyzes academic progress and recommends optimal course sequences
"""

import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class CourseRecommendationEngine:
    """
    Intelligent engine that analyzes student academic progress from Degree Works
    and recommends optimal course sequences based on:
    - Completed courses
    - Prerequisites
    - Graduation requirements
    - Course availability
    - Student classification (Freshman, Sophomore, Junior, Senior)
    """
    
    def __init__(self):
        self.course_prerequisites = self._initialize_prerequisites()
        self.graduation_requirements = self._initialize_requirements()
        self.course_sequences = self._initialize_sequences()
    
    def _initialize_prerequisites(self) -> Dict[str, List[str]]:
        """
        Initialize course prerequisites for CS major
        
        Returns:
            Dictionary mapping course codes to required prerequisites
        """
        return {
            # Foundational Courses
            'COSC 111': [],  # Introduction to Computer Science I
            'COSC 112': ['COSC 111'],  # Introduction to Computer Science II
            'COSC 211': ['COSC 112'],  # Data Structures
            'COSC 214': ['COSC 112'],  # Computer Organization and Assembly Language
            
            # Core Upper-Level Courses
            'COSC 311': ['COSC 211'],  # Algorithms
            'COSC 341': ['COSC 211'],  # Programming Languages
            'COSC 355': ['COSC 214'],  # Computer Architecture
            'COSC 360': ['COSC 211'],  # Database Systems
            'COSC 370': ['COSC 211'],  # Operating Systems
            'COSC 420': ['COSC 311'],  # Analysis of Algorithms
            'COSC 425': ['COSC 311'],  # Software Engineering
            
            # Electives
            'COSC 330': ['COSC 211'],  # Web Development
            'COSC 345': ['COSC 211'],  # Mobile Application Development
            'COSC 380': ['COSC 211'],  # Computer Networks
            'COSC 415': ['COSC 211'],  # Artificial Intelligence
            'COSC 430': ['COSC 311'],  # Machine Learning
            'COSC 440': ['COSC 360'],  # Big Data Analytics
            'COSC 450': ['COSC 370'],  # Cybersecurity
            'COSC 460': ['COSC 341'],  # Compiler Design
            'COSC 480': ['COSC 311'],  # Computer Graphics
            
            # Math Requirements
            'MATH 211': [],  # Calculus I
            'MATH 212': ['MATH 211'],  # Calculus II
            'MATH 245': ['MATH 211'],  # Discrete Mathematics
            'MATH 325': ['MATH 212'],  # Linear Algebra
            
            # Science Requirements
            'PHYS 211': ['MATH 211'],  # Physics I
            'PHYS 212': ['PHYS 211', 'MATH 212'],  # Physics II
        }
    
    def _initialize_requirements(self) -> Dict[str, Any]:
        """
        Initialize graduation requirements for CS major
        
        Returns:
            Dictionary with graduation requirements
        """
        return {
            'total_credits': 120,
            'core_cs_courses': [
                'COSC 111', 'COSC 112', 'COSC 211', 'COSC 214',
                'COSC 311', 'COSC 341', 'COSC 355', 'COSC 360',
                'COSC 370', 'COSC 420', 'COSC 425'
            ],
            'required_math': [
                'MATH 211', 'MATH 212', 'MATH 245', 'MATH 325'
            ],
            'required_science': [
                'PHYS 211', 'PHYS 212'
            ],
            'cs_electives_required': 4,  # Number of CS elective courses
            'general_ed_credits': 42,
            'free_electives_credits': 15
        }
    
    def _initialize_sequences(self) -> Dict[str, List[List[str]]]:
        """
        Initialize recommended course sequences by classification
        
        Returns:
            Dictionary with recommended sequences for each year
        """
        return {
            'freshman': [
                ['COSC 111', 'MATH 211', 'ENGL 101'],  # Fall
                ['COSC 112', 'MATH 212', 'ENGL 102']   # Spring
            ],
            'sophomore': [
                ['COSC 211', 'MATH 245', 'PHYS 211'],  # Fall
                ['COSC 214', 'MATH 325', 'PHYS 212']   # Spring
            ],
            'junior': [
                ['COSC 311', 'COSC 341', 'COSC 360'],  # Fall
                ['COSC 355', 'COSC 370', 'CS_ELECTIVE']  # Spring
            ],
            'senior': [
                ['COSC 420', 'COSC 425', 'CS_ELECTIVE'],  # Fall
                ['CS_ELECTIVE', 'CS_ELECTIVE', 'CAPSTONE']  # Spring
            ]
        }
    
    def analyze_student_progress(self, degree_works_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze student's academic progress from Degree Works data
        
        Args:
            degree_works_data: Parsed Degree Works data
            
        Returns:
            Analysis of student progress including completed requirements
        """
        try:
            completed_courses = self._extract_completed_courses(degree_works_data)
            in_progress_courses = self._extract_in_progress_courses(degree_works_data)
            
            # Analyze completion status
            core_cs_completed = [
                course for course in self.graduation_requirements['core_cs_courses']
                if self._course_completed(course, completed_courses)
            ]
            
            math_completed = [
                course for course in self.graduation_requirements['required_math']
                if self._course_completed(course, completed_courses)
            ]
            
            science_completed = [
                course for course in self.graduation_requirements['required_science']
                if self._course_completed(course, completed_courses)
            ]
            
            # Count CS electives
            cs_electives_completed = len([
                course for course in completed_courses
                if course.startswith('COSC') and course not in self.graduation_requirements['core_cs_courses']
            ])
            
            # Calculate credits
            total_credits = degree_works_data.get('total_credits_completed', 0)
            credits_needed = self.graduation_requirements['total_credits'] - total_credits
            
            # Determine next courses
            next_recommended = self._recommend_next_courses(
                completed_courses,
                in_progress_courses,
                degree_works_data.get('classification', 'Freshman')
            )
            
            return {
                'success': True,
                'total_credits': total_credits,
                'credits_needed': max(0, credits_needed),
                'completion_percentage': min(100, round((total_credits / self.graduation_requirements['total_credits']) * 100, 1)),
                'core_cs_progress': {
                    'completed': core_cs_completed,
                    'remaining': [c for c in self.graduation_requirements['core_cs_courses'] if c not in core_cs_completed],
                    'completion_rate': f"{len(core_cs_completed)}/{len(self.graduation_requirements['core_cs_courses'])}"
                },
                'math_progress': {
                    'completed': math_completed,
                    'remaining': [c for c in self.graduation_requirements['required_math'] if c not in math_completed],
                    'completion_rate': f"{len(math_completed)}/{len(self.graduation_requirements['required_math'])}"
                },
                'science_progress': {
                    'completed': science_completed,
                    'remaining': [c for c in self.graduation_requirements['required_science'] if c not in science_completed],
                    'completion_rate': f"{len(science_completed)}/{len(self.graduation_requirements['required_science'])}"
                },
                'cs_electives': {
                    'completed': cs_electives_completed,
                    'required': self.graduation_requirements['cs_electives_required'],
                    'remaining': max(0, self.graduation_requirements['cs_electives_required'] - cs_electives_completed)
                },
                'next_recommended_courses': next_recommended,
                'classification': degree_works_data.get('classification', 'Unknown'),
                'estimated_graduation': self._estimate_graduation_date(credits_needed, degree_works_data.get('classification'))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing student progress: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_completed_courses(self, degree_works_data: Dict[str, Any]) -> List[str]:
        """Extract list of completed courses from Degree Works data"""
        completed = []
        
        for course in degree_works_data.get('courses_completed', []):
            course_code = course.get('course_code', '')
            if course_code:
                completed.append(course_code)
        
        return completed
    
    def _extract_in_progress_courses(self, degree_works_data: Dict[str, Any]) -> List[str]:
        """Extract list of in-progress courses from Degree Works data"""
        in_progress = []
        
        for course in degree_works_data.get('courses_in_progress', []):
            course_code = course.get('course_code', '')
            if course_code:
                in_progress.append(course_code)
        
        return in_progress
    
    def _course_completed(self, course_code: str, completed_courses: List[str]) -> bool:
        """Check if a course has been completed"""
        return any(
            course_code == completed or
            course_code.replace(' ', '') == completed.replace(' ', '')
            for completed in completed_courses
        )
    
    def _recommend_next_courses(
        self,
        completed_courses: List[str],
        in_progress_courses: List[str],
        classification: str
    ) -> List[Dict[str, Any]]:
        """
        Recommend next courses based on completed courses and classification
        
        Args:
            completed_courses: List of completed course codes
            in_progress_courses: List of currently enrolled courses
            classification: Student classification (Freshman, Sophomore, Junior, Senior)
            
        Returns:
            List of recommended courses with priorities
        """
        recommendations = []
        
        # Normalize classification
        classification_lower = classification.lower()
        
        # Get all courses student can take (prerequisites met)
        available_courses = self._get_available_courses(completed_courses, in_progress_courses)
        
        # Prioritize required core courses
        for course in self.graduation_requirements['core_cs_courses']:
            if (not self._course_completed(course, completed_courses) and
                not self._course_completed(course, in_progress_courses) and
                course in available_courses):
                
                recommendations.append({
                    'course_code': course,
                    'priority': 'HIGH',
                    'type': 'Core CS Requirement',
                    'reason': 'Required for CS major',
                    'prerequisites_met': True
                })
        
        # Add required math courses
        for course in self.graduation_requirements['required_math']:
            if (not self._course_completed(course, completed_courses) and
                not self._course_completed(course, in_progress_courses) and
                course in available_courses):
                
                recommendations.append({
                    'course_code': course,
                    'priority': 'HIGH',
                    'type': 'Math Requirement',
                    'reason': 'Required math course',
                    'prerequisites_met': True
                })
        
        # Add required science courses
        for course in self.graduation_requirements['required_science']:
            if (not self._course_completed(course, completed_courses) and
                not self._course_completed(course, in_progress_courses) and
                course in available_courses):
                
                recommendations.append({
                    'course_code': course,
                    'priority': 'MEDIUM',
                    'type': 'Science Requirement',
                    'reason': 'Required science course',
                    'prerequisites_met': True
                })
        
        # Add CS electives if core requirements are mostly complete
        core_completion_rate = len([c for c in self.graduation_requirements['core_cs_courses'] 
                                   if self._course_completed(c, completed_courses)])
        
        if core_completion_rate >= 7:  # At least 7/11 core courses done
            elective_courses = [
                'COSC 330', 'COSC 345', 'COSC 380', 'COSC 415',
                'COSC 430', 'COSC 440', 'COSC 450', 'COSC 460', 'COSC 480'
            ]
            
            for course in elective_courses:
                if (not self._course_completed(course, completed_courses) and
                    not self._course_completed(course, in_progress_courses) and
                    course in available_courses):
                    
                    recommendations.append({
                        'course_code': course,
                        'priority': 'MEDIUM',
                        'type': 'CS Elective',
                        'reason': 'Recommended elective based on career paths',
                        'prerequisites_met': True
                    })
        
        # Sort by priority
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        # Limit to top 8 recommendations
        return recommendations[:8]
    
    def _get_available_courses(
        self,
        completed_courses: List[str],
        in_progress_courses: List[str]
    ) -> Set[str]:
        """
        Get all courses student can take based on completed prerequisites
        
        Args:
            completed_courses: List of completed course codes
            in_progress_courses: List of currently enrolled courses
            
        Returns:
            Set of available course codes
        """
        available = set()
        
        for course, prerequisites in self.course_prerequisites.items():
            # Check if all prerequisites are met
            prereqs_met = all(
                self._course_completed(prereq, completed_courses) or
                self._course_completed(prereq, in_progress_courses)
                for prereq in prerequisites
            )
            
            if prereqs_met:
                available.add(course)
        
        return available
    
    def _estimate_graduation_date(self, credits_needed: int, classification: str) -> str:
        """
        Estimate graduation date based on remaining credits and current classification
        
        Args:
            credits_needed: Number of credits still needed
            classification: Current student classification
            
        Returns:
            Estimated graduation semester and year
        """
        # Assume average of 15 credits per semester
        semesters_needed = max(1, round(credits_needed / 15))
        
        # Map classification to semesters from now
        classification_semesters = {
            'freshman': 8,
            'sophomore': 6,
            'junior': 4,
            'senior': 2
        }
        
        typical_semesters = classification_semesters.get(classification.lower(), 4)
        actual_semesters = max(semesters_needed, typical_semesters)
        
        # Calculate target year and semester
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # Determine current semester
        if current_month >= 8:
            current_semester = 'Fall'
            years_ahead = (actual_semesters - 1) // 2
            if actual_semesters % 2 == 0:
                target_semester = 'Spring'
                target_year = current_year + years_ahead + 1
            else:
                target_semester = 'Fall'
                target_year = current_year + years_ahead + 1
        elif current_month >= 1:
            current_semester = 'Spring'
            years_ahead = actual_semesters // 2
            if actual_semesters % 2 == 0:
                target_semester = 'Spring'
                target_year = current_year + years_ahead
            else:
                target_semester = 'Fall'
                target_year = current_year + years_ahead
        
        return f"{target_semester} {target_year}"
    
    def generate_course_plan(
        self,
        degree_works_data: Dict[str, Any],
        semesters_ahead: int = 4
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive course plan for upcoming semesters
        
        Args:
            degree_works_data: Parsed Degree Works data
            semesters_ahead: Number of semesters to plan (default: 4)
            
        Returns:
            Detailed semester-by-semester course plan
        """
        try:
            completed_courses = self._extract_completed_courses(degree_works_data)
            in_progress_courses = self._extract_in_progress_courses(degree_works_data)
            
            plan = {
                'success': True,
                'semesters': [],
                'total_planned_credits': 0
            }
            
            # Track what's been planned
            planned_courses = set(in_progress_courses)
            
            for semester_num in range(1, semesters_ahead + 1):
                # Get available courses
                available = self._get_available_courses(
                    completed_courses,
                    list(planned_courses)
                )
                
                # Recommend courses for this semester
                semester_courses = []
                semester_credits = 0
                target_credits = 15  # Target 15 credits per semester
                
                # Get recommendations
                recommendations = self._recommend_next_courses(
                    completed_courses,
                    list(planned_courses),
                    degree_works_data.get('classification', 'Sophomore')
                )
                
                # Add courses until we hit target credits
                for rec in recommendations:
                    if semester_credits < target_credits:
                        course_code = rec['course_code']
                        if course_code in available and course_code not in planned_courses:
                            semester_courses.append({
                                'course_code': course_code,
                                'credits': 3,  # Assume 3 credits per course
                                'type': rec['type'],
                                'priority': rec['priority']
                            })
                            semester_credits += 3
                            planned_courses.add(course_code)
                
                # Determine semester name
                current_month = datetime.now().month
                if current_month >= 8:
                    base_semester = 'Fall'
                    base_year = datetime.now().year
                else:
                    base_semester = 'Spring'
                    base_year = datetime.now().year
                
                # Calculate semester name
                semester_offset = semester_num - 1
                if base_semester == 'Fall':
                    if semester_offset % 2 == 0:
                        sem_name = f"Fall {base_year + semester_offset // 2}"
                    else:
                        sem_name = f"Spring {base_year + (semester_offset + 1) // 2}"
                else:
                    if semester_offset % 2 == 0:
                        sem_name = f"Spring {base_year + semester_offset // 2}"
                    else:
                        sem_name = f"Fall {base_year + semester_offset // 2}"
                
                plan['semesters'].append({
                    'semester': sem_name,
                    'courses': semester_courses,
                    'total_credits': semester_credits
                })
                
                plan['total_planned_credits'] += semester_credits
            
            return plan
            
        except Exception as e:
            logger.error(f"Error generating course plan: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
course_recommendation_engine = CourseRecommendationEngine()
