"""
Debug COSC 111 status determination
"""
import sys
import logging
import asyncio
from pathlib import Path

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

sys.path.insert(0, "/app")

from app.services.degree_works_parser import DegreeWorksParser

async def test():
    """Test parser and show COSC 111 processing details"""
    
    parser = DegreeWorksParser()
    
    pdf_path = Path("/app/test_degree_work.pdf")
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    print("\n" + "="*80)
    print("DEBUGGING COSC 111 PROCESSING")
    print("="*80 + "\n")
    
    result = await parser.parse_pdf(pdf_bytes)
    
    # Check results
    completed = result.get('courses', {}).get('completed', [])
    in_progress = result.get('courses', {}).get('in_progress', [])
    
    cosc_111_completed = [c for c in completed if c.get('course_code') == 'COSC 111']
    cosc_111_ip = [c for c in in_progress if c.get('course_code') == 'COSC 111']
    
    print(f"\n{'='*80}")
    print("FINAL RESULT:")
    print(f"{'='*80}")
    print(f"COSC 111 in completed: {len(cosc_111_completed)}")
    for c in cosc_111_completed:
        print(f"  Grade: {c.get('grade')}, Term: {c.get('term')}, Category: {c.get('category')}")
    
    print(f"\nCOSC 111 in in-progress: {len(cosc_111_ip)}")
    for c in cosc_111_ip:
        print(f"  Grade: {c.get('grade')}, Term: {c.get('term')}, Category: {c.get('category')}")

if __name__ == "__main__":
    asyncio.run(test())
