#!/usr/bin/env python3
"""Debug script to test what Playwright extracts from faculty pages"""

import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


async def test_playwright_extraction():
    """Test Playwright rendering and content extraction"""
    
    urls = [
        "https://www.morgan.edu/computer-science/current-students/academic-advisers",
        "https://www.morgan.edu/computer-science/faculty",
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        for url in urls:
            print(f"\n{'='*80}")
            print(f"Testing: {url}")
            print('='*80)
            
            page = await browser.new_page()
            page.set_default_timeout(20000)
            
            try:
                # Navigate to page
                await page.goto(url, wait_until='networkidle')
                
                # Wait for faculty markers
                try:
                    await page.wait_for_function(
                        """() => {
                            const text = document.body.innerText.toLowerCase();
                            return (text.includes('dr.') || text.includes('professor') || 
                                    text.includes('office hours')) && text.length > 2000;
                        }""",
                        timeout=5000
                    )
                    print("✓ Faculty markers found in page")
                except:
                    print("⚠ Faculty markers NOT found (timeout)")
                
                # Get page content
                html = await page.content()
                text = await page.evaluate('document.body.innerText')
                
                print(f"\nHTML Length: {len(html)}")
                print(f"Text Length: {len(text)}")
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Try to extract faculty info
                faculty_info = ""
                
                # Pattern 1: Look for divs/articles with faculty markers
                print("\n[Pattern 1: Searching divs/articles/sections for faculty markers]")
                count = 0
                for elem in soup.find_all(['div', 'article', 'section']):
                    elem_text = elem.get_text(separator='\n', strip=True)
                    if any(marker in elem_text.lower() for marker in ['dr.', 'professor', 'ph.d', 'office hours', 'email:']):
                        count += 1
                        snippet = elem_text[:200].replace('\n', ' ')
                        print(f"  Found {count}: {snippet}...")
                        faculty_info += elem_text + "\n"
                
                # Pattern 2: Look for list items
                print("\n[Pattern 2: Searching list items for faculty]")
                count = 0
                for li in soup.find_all('li'):
                    li_text = li.get_text(separator=' ', strip=True)
                    if len(li_text) > 30 and any(marker in li_text.lower() for marker in ['dr.', 'professor', '@']):
                        count += 1
                        snippet = li_text[:200]
                        print(f"  Found {count}: {snippet}...")
                        faculty_info += li_text + "\n"
                
                print(f"\nTotal faculty_info extracted: {len(faculty_info)} chars")
                
                # Show first part of extracted text
                print(f"\n[First 500 chars of extracted text]")
                print(text[:500])
                
                print(f"\n[First 500 chars of faculty_info]")
                print(faculty_info[:500])
                
            except Exception as e:
                print(f"✗ Error: {e}")
            finally:
                await page.close()
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_playwright_extraction())
