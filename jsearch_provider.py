"""
JSearch API Provider for Career-Ops
Provides real job listings via RapidAPI's JSearch endpoint
"""
import os
import time
import httpx
from typing import Optional, List
from pydantic import BaseModel


class JSearchResult(BaseModel):
    """JSearch job result"""
    id: str
    title: str
    company: str
    location: str
    currency: str
    salary_range: str
    source: str
    url: str
    posted: str
    status: str
    description: str
    employment_type: Optional[str] = None
    required_skills: Optional[List[str]] = None


async def search_jsearch(
    title: str,
    location: str,
    currency: str = "AED",
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None
) -> List[JSearchResult]:
    """
    Search for jobs using JSearch API via RapidAPI.
    
    Args:
        title: Job title to search for
        location: Job location
        currency: Currency for salary display
        salary_min: Minimum salary filter
        salary_max: Maximum salary filter
    
    Returns:
        List of JSearchResult objects
    """
    jsearch_key = os.environ.get("JSEARCH_API_KEY", "")
    if not jsearch_key:
        jsearch_key = os.getenv("JSEARCH_API_KEY", "")
    
    if not jsearch_key:
        raise ValueError("JSEARCH_API_KEY not configured in .env")
    
    query = f"{title} {location}" if location else title
    
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": jsearch_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    
    params = {
        "query": query,
        "page": "1",
        "num_pages": "3",
        "date_posted": "week",
        "employment_type": "FULLTIME,CONTRACT"
    }
    
    if location:
        params["location"] = location
    
    results = []
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
                params=params,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"JSearch API error: {response.status_code} - {response.text[:200]}")
            
            data = response.json()
            jobs = data.get("data", [])
            
            if not jobs:
                return []
            
            for idx, job in enumerate(jobs):
                # Extract salary if available
                salary_range = "Not disclosed"
                if job.get("salary_min") and job.get("salary_max"):
                    job_currency = job.get("salary_currency", currency)
                    salary_range = f"{job_currency} {job.get('salary_min'):,} - {job.get('salary_max'):,}"
                elif job.get("salary_min"):
                    job_currency = job.get("salary_currency", currency)
                    salary_range = f"{job_currency} {job.get('salary_min'):,}+"
                
                # Apply salary filter
                if not salary_in_range(salary_range, salary_min, salary_max):
                    continue
                
                result = JSearchResult(
                    id=f"jsearch-{int(time.time())}-{idx + 1}",
                    title=job.get("job_title", "Unknown"),
                    company=job.get("employer_name", "Unknown"),
                    location=job.get("job_city", job.get("job_country", location or "Remote")),
                    currency=currency,
                    salary_range=salary_range,
                    source=job.get("job_source", "JSearch"),
                    url=job.get("job_apply_link") or job.get("job_link", "https://www.linkedin.com/jobs"),
                    posted=job.get("job_posted_at_datetime_utc", "Recently")[:10],
                    status="new",
                    description=(job.get("job_description", ""))[:500],
                    employment_type=job.get("job_employment_type", "Full-time"),
                    required_skills=job.get("job_required_skills", [])[:5],
                )
                results.append(result)
    
    except httpx.ConnectError as e:
        raise Exception(f"Unable to connect to JSearch API: {str(e)}")
    except httpx.TimeoutException:
        raise Exception("JSearch API request timed out")
    except Exception as e:
        raise Exception(f"JSearch error: {str(e)[:200]}")
    
    return results


def salary_in_range(salary_str: str, min_filter: Optional[float], max_filter: Optional[float]) -> bool:
    """Check if salary range overlaps with filter"""
    import re
    
    if min_filter is None and max_filter is None:
        return True
    
    if not salary_str or not isinstance(salary_str, str):
        return True  # No salary data, include by default
    
    # Extract numbers
    numbers = re.findall(r'\d+(?:,\d{3})*(?:\.\d{2})?', salary_str.replace(',', ''))
    if len(numbers) >= 2:
        try:
            sal_min = float(numbers[0])
            sal_max = float(numbers[1])
        except (ValueError, IndexError):
            return True
    elif len(numbers) == 1:
        try:
            sal_min = sal_max = float(numbers[0])
        except ValueError:
            return True
    else:
        return True  # Can't parse, include
    
    # Check overlap
    if min_filter is not None and sal_max < min_filter:
        return False
    if max_filter is not None and sal_min > max_filter:
        return False
    
    return True
