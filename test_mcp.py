import asyncio
import sys
from career_ops_mcp import convert_currency, prioritize_by_geo, analyze_job_match, generate_latex_resume

def test_sync_tools():
    print("Testing convert_currency...")
    r1 = convert_currency(100000.0, "INR")
    print("INR 100K Conversion:", r1)
    
    r2 = convert_currency(12000.0, "AED")
    print("AED 12K Conversion:", r2)
    
    print("\nTesting prioritize_by_geo...")
    p1 = prioritize_by_geo("Dubai, UAE")
    print("Dubai priority:", p1)
    
    p2 = prioritize_by_geo("New York, USA")
    print("New York priority:", p2)

async def test_async_tools():
    test_jd = """
    We are looking for a Senior Marketing Manager in Dubai, UAE.
    Responsibilities:
    - Oversee marketing campaigns and budget
    - Optimize PPC and SEO strategies
    - Streamline marketing workflows using AI
    Requirements:
    - 5+ years of experience in MarTech or digital marketing
    - Experience with HubSpot and Google Analytics
    - Basic understanding of AI content automation tools
    """
    
    print("\nTesting analyze_job_match...")
    try:
        match_report = await analyze_job_match(test_jd)
        print("Job match report snippet:")
        print(match_report[:1000])
    except Exception as e:
        print("Job match analysis failed:", e)

    print("\nTesting generate_latex_resume...")
    try:
        resume_result = await generate_latex_resume(test_jd)
        print("LaTeX resume generation result:", resume_result)
    except Exception as e:
        print("LaTeX resume generation failed:", e)

if __name__ == "__main__":
    test_sync_tools()
    asyncio.run(test_async_tools())
