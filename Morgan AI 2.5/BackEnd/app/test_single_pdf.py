"""
Test the enhanced parser with a specific Degree Works PDF
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.degree_works_parser import DegreeWorksParser

async def test_single_pdf():
    """Test parser with specific PDF"""
    
    parser = DegreeWorksParser()
    
    pdf_path = Path("/app/test_degree_work.pdf")
    
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    print(f"\n{'='*80}")
    print(f"Testing Degree Works PDF")
    print(f"{'='*80}\n")
    
    # Read PDF bytes
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    print(f"PDF size: {len(pdf_bytes)} bytes\n")
    
    # Parse PDF
    result = await parser.parse_pdf(pdf_bytes)
    
    if not result.get('success'):
        print(f"❌ PARSING FAILED: {result.get('error')}")
        return
    
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
    
    # Show ALL completed courses
    if completed:
        print(f"\n✓ COMPLETED COURSES (all {len(completed)}):")
        for i, course in enumerate(completed, 1):
            print(f"  {i}. {course.get('course_code')}: {course.get('course_name', 'N/A')[:50]}")
            print(f"     Grade: {course.get('grade', 'N/A')} | Credits: {course.get('credits', 0)} | Term: {course.get('term', 'N/A')}")
    
    # Show ALL in-progress courses
    if in_progress:
        print(f"\n⏳ IN-PROGRESS COURSES (all {len(in_progress)}):")
        for i, course in enumerate(in_progress, 1):
            print(f"  {i}. {course.get('course_code')}: {course.get('course_name', 'N/A')[:50]}")
            print(f"     Grade: {course.get('grade', 'N/A')} | Credits: {course.get('credits', 0)} | Term: {course.get('term', 'N/A')}")
    
    # Show remaining courses
    if remaining:
        print(f"\n📝 REMAINING REQUIRED COURSES ({len(remaining)}):")
        for i, course in enumerate(remaining, 1):
            print(f"  {i}. {course.get('course_code')}: {course.get('course_name', 'N/A')[:50]}")
            print(f"     Credits: {course.get('credits', 0)} | Category: {course.get('category', 'General')}")
    
    # Course Timeline
    timeline = result.get('course_timeline', {})
    if timeline:
        print(f"\n📅 COURSE TIMELINE ({len(timeline)} terms):")
        for term, term_courses in timeline.items():
            term_completed = len(term_courses.get('completed', []))
            term_ip = len(term_courses.get('in_progress', []))
            term_remaining = len(term_courses.get('remaining', []))
            print(f"  {term}: {term_completed} completed, {term_ip} in-progress, {term_remaining} remaining")
    
    # Validate accuracy
    print(f"\n🔍 ACCURACY VALIDATION:")
    print(f"  Duplicate detection: Looking for duplicate course codes...")
    seen_codes = set()
    duplicates = []
    for status_list in [completed, in_progress, remaining]:
        for course in status_list:
            code = course.get('course_code')
            if code in seen_codes:
                duplicates.append(code)
            seen_codes.add(code)
    
    if duplicates:
        print(f"  ❌ Found {len(duplicates)} duplicates: {duplicates}")
    else:
        print(f"  ✅ No duplicates found!")
    
    # Check for false positives (semester headers as courses)
    print(f"\n  False positive check: Looking for semester headers...")
    false_positives = []
    for course in completed + in_progress + remaining:
        code = course.get('course_code', '')
        name = course.get('course_name', '')
        if 'FALL' in code or 'SPRING' in code or 'GPA' in name.upper():
            false_positives.append(f"{code}: {name}")
    
    if false_positives:
        print(f"  ❌ Found {len(false_positives)} false positives: {false_positives}")
    else:
        print(f"  ✅ No false positives found!")
    
    # Calculate total credits
    total_completed_credits = sum(c.get('credits', 0) for c in completed)
    total_ip_credits = sum(c.get('credits', 0) for c in in_progress)
    
    print(f"\n  Credit totals:")
    print(f"    Completed from courses: {total_completed_credits}")
    print(f"    Completed from header: {summary.get('completed_credits', 0)}")
    print(f"    In-progress from courses: {total_ip_credits}")
    print(f"    In-progress from header: {summary.get('in_progress_credits', 0)}")
    
    header_completed = summary.get('completed_credits', 0)
    if abs(total_completed_credits - header_completed) < 5:
        print(f"  ✅ Completed credits match!")
    else:
        print(f"  ⚠️  Completed credits mismatch (courses: {total_completed_credits}, header: {header_completed})")

if __name__ == "__main__":
    asyncio.run(test_single_pdf())
