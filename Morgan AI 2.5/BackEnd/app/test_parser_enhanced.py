"""
Test the enhanced Degree Works parser with actual PDF data
"""
import sys
import asyncio
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.degree_works_parser import DegreeWorksParser

async def test_parser():
    """Test parser with actual Degree Works PDFs"""
    
    parser = DegreeWorksParser()
    
    # Test PDFs
    pdf_paths = [
        Path("/app/data/users/1d3c9472-0b91-44be-a834-b135824ed0db/degree_works/old DegreeWorks.pdf"),
        Path("/app/data/users/555b67b9-d8fe-4171-b15e-4121d379c904/degree_works/degree_work_20251121_204518.pdf")
    ]
    
    for pdf_path in pdf_paths:
        if not pdf_path.exists():
            print(f"❌ PDF not found: {pdf_path}")
            continue
            
        print(f"\n{'='*80}")
        print(f"Testing: {pdf_path.name}")
        print(f"{'='*80}\n")
        
        # Read PDF bytes
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        # Parse PDF
        result = await parser.parse_pdf(pdf_bytes)
        
        if not result.get('success'):
            print(f"❌ Parsing failed: {result.get('error')}")
            continue
        
        # Display results
        print("✅ PARSING SUCCESSFUL\n")
        
        # Student Info
        student_info = result.get('student_info', {})
        print("📋 STUDENT INFORMATION:")
        print(f"  Name: {student_info.get('name', 'N/A')}")
        print(f"  ID: {student_info.get('student_id', 'N/A')}")
        print(f"  Major: {student_info.get('major', 'N/A')}")
        print(f"  Degree: {student_info.get('degree', 'N/A')}")
        
        # Academic Summary
        summary = result.get('academic_summary', {})
        print(f"\n📊 ACADEMIC SUMMARY:")
        print(f"  Classification: {summary.get('classification', 'N/A')}")
        print(f"  Current GPA: {summary.get('gpa', 'N/A')}")
        print(f"  Credits Completed: {summary.get('completed_credits', 0)}")
        print(f"  Credits In Progress: {summary.get('in_progress_credits', 0)}")
        print(f"  Total Required: {summary.get('total_credits_required', 120)}")
        print(f"  Credits Remaining: {summary.get('remaining_credits', 0)}")
        
        # Course Breakdown
        courses = result.get('courses', {})
        completed = courses.get('completed', [])
        in_progress = courses.get('in_progress', [])
        remaining = courses.get('remaining', [])
        
        print(f"\n📚 COURSE BREAKDOWN:")
        print(f"  ✓ Completed: {len(completed)} courses")
        print(f"  ⏳ In Progress: {len(in_progress)} courses")
        print(f"  📝 Remaining: {len(remaining)} courses")
        
        # Show sample completed courses (first 10)
        if completed:
            print(f"\n✓ COMPLETED COURSES (showing first 10):")
            for i, course in enumerate(completed[:10], 1):
                print(f"  {i}. {course.get('course_code')}: {course.get('course_name', 'N/A')[:40]}")
                print(f"     Grade: {course.get('grade', 'N/A')} | Credits: {course.get('credits', 0)} | Term: {course.get('term', 'N/A')}")
        
        # Show in-progress courses
        if in_progress:
            print(f"\n⏳ IN-PROGRESS COURSES:")
            for i, course in enumerate(in_progress, 1):
                print(f"  {i}. {course.get('course_code')}: {course.get('course_name', 'N/A')[:40]}")
                print(f"     Grade: {course.get('grade', 'N/A')} | Credits: {course.get('credits', 0)} | Term: {course.get('term', 'N/A')}")
        
        # Show remaining courses (first 10)
        if remaining:
            print(f"\n📝 REMAINING REQUIRED COURSES (showing first 10):")
            for i, course in enumerate(remaining[:10], 1):
                print(f"  {i}. {course.get('course_code')}: {course.get('course_name', 'N/A')[:40]}")
                print(f"     Credits: {course.get('credits', 0)} | Category: {course.get('category', 'General')}")
        
        # Course Timeline
        timeline = result.get('course_timeline', {})
        if timeline:
            print(f"\n📅 COURSE TIMELINE ({len(timeline)} terms):")
            for term, term_courses in list(timeline.items())[:5]:  # Show first 5 terms
                term_completed = len(term_courses.get('completed', []))
                term_ip = len(term_courses.get('in_progress', []))
                print(f"  {term}: {term_completed} completed, {term_ip} in-progress")
        
        # Requirements by Category
        requirements = result.get('requirements', {})
        if requirements:
            print(f"\n📑 REQUIREMENTS BY CATEGORY:")
            for category, req_data in requirements.items():
                completed_cred = req_data.get('completed_credits', 0)
                ip_cred = req_data.get('in_progress_credits', 0)
                remaining_cred = req_data.get('remaining_credits', 0)
                print(f"  {category}:")
                print(f"    Completed: {completed_cred} credits | In Progress: {ip_cred} | Remaining: {remaining_cred}")

if __name__ == "__main__":
    asyncio.run(test_parser())
