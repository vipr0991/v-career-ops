"""
Adzuna API Provider for Career-Ops
Provides real job listings via RapidAPI's Adzuna endpoint
Third backup search source when SerpAPI and JSearch are exhausted
"""
import os
import time
import httpx
from typing import Optional, List
from pydantic import BaseModel


class AdzunaResult(BaseModel):
    """Adzuna job result"""
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


async def search_adzuna(
    title: str,
    location: str,
    currency: str = "AED",
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None
) -> List[AdzunaResult]:
    """
    Search for jobs using Adzuna API via RapidAPI.
    
    Adzuna is a job aggregator covering:
    - Indeed
    - LinkedIn
    - Glassdoor
    - CareerBuilder
    - Monster
    - Government job boards
    - Niche job sites
    
    Args:
        title: Job title to search for
        location: Job location
        currency: Currency for salary display
        salary_min: Minimum salary filter
        salary_max: Maximum salary filter
    
    Returns:
        List of AdzunaResult objects
    """
    adzuna_key = os.environ.get("ADZUNA_API_KEY", "")
    if not adzuna_key:
        adzuna_key = os.getenv("ADZUNA_API_KEY", "")
    
    if not adzuna_key:
        raise ValueError("ADZUNA_API_KEY not configured in .env")
    
    # Map currency to Adzuna country code
    country_map = {
        "AED": "ae",
        "SAR": "sa",
        "QAR": "qa",
        "INR": "in",
        "USD": "us",
        "GBP": "gb",
        "EUR": "nl",
    }
    
    country = country_map.get(currency, "ae")
    
    url = f"https://adzuna.p.rapidapi.com/v1/search/{country}"
    headers = {
        "X-RapidAPI-Key": adzuna_key,
        "X-RapidAPI-Host": "adzuna.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    
    params = {
        "app_id": "adzuna",
        "app_key": adzuna_key,
        "what": title,
        "where": location,
        "results_per_page": "30",
        "full": "true",
        "sort_by": "date",
        "sort_direction": "decrease"
    }
    
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
                raise Exception(f"Adzuna API error: {response.status_code} - {response.text[:200]}")
            
            data = response.json()
            jobs = data.get("results", [])
            
            if not jobs:
                return []
            
            for idx, job in enumerate(jobs):
                # Extract salary if available
                salary_range = "Not disclosed"
                if job.get("salary_min") and job.get("salary_max"):
                    salary_range = f"{currency} {job.get('salary_min'):,.0f} - {job.get('salary_max'):,.0f}"
                elif job.get("salary_min"):
                    salary_range = f"{currency} {job.get('salary_min'):,.0f}+"
                elif job.get("salary_max"):
                    salary_range = f"{currency} up to {job.get('salary_max'):,.0f}"
                
                # Apply salary filter
                if not salary_in_range(salary_range, salary_min, salary_max):
                    continue
                
                # Extract location parts
                job_location = location
                if job.get("location"):
                    location_data = job["location"]
                    if isinstance(location_data, dict):
                        job_location = location_data.get("display_name", location)
                    else:
                        job_location = str(location_data)
                
                # Parse company from description if needed
                company = job.get("company", {})
                if isinstance(company, dict):
                    company_name = company.get("display_name", "Unknown")
                else:
                    company_name = str(company) if company else "Unknown"
                
                result = AdzunaResult(
                    id=f"adzuna-{int(time.time())}-{idx + 1}",
                    title=job.get("title", "Unknown"),
                    company=company_name,
                    location=job_location,
                    currency=currency,
                    salary_range=salary_range,
                    source=job.get("source", "Adzuna"),
                    url=job.get("redirect_url", "https://www.adzuna.com/jobs"),
                    posted=job.get("created", "Recently")[:10],
                    status="new",
                    description=(job.get("description", ""))[:500],
                    employment_type=job.get("contract_type", "Full-time"),
                    required_skills=[],  # Adzuna doesn't provide required_skills
                )
                results.append(result)
    
    except httpx.ConnectError as e:
        raise Exception(f"Unable to connect to Adzuna API: {str(e)}")
    except httpx.TimeoutException:
        raise Exception("Adzuna API request timed out")
    except Exception as e:
        raise Exception(f"Adzuna error: {str(e)[:200]}")
    
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
