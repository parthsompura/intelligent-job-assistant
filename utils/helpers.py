import re
import hashlib
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


def generate_job_id(url: str, platform: str) -> str:
    """Generate unique job ID from URL and platform"""
    try:
        # Create hash from URL
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"{platform}_{url_hash}"
    except Exception as e:
        logger.error(f"Error generating job ID: {e}")
        return f"{platform}_{hash(url) % 1000000}"


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-.,!?()]', '', text)
    
    return text


def extract_skills_from_text(text: str, skill_list: List[str] = None) -> List[str]:
    """Extract skills from text using a predefined skill list"""
    if not skill_list:
        skill_list = [
            "python", "java", "javascript", "typescript", "react", "angular", "vue",
            "node.js", "express", "django", "flask", "spring", "sql", "mongodb",
            "postgresql", "mysql", "aws", "azure", "gcp", "docker", "kubernetes",
            "git", "github", "jenkins", "ci/cd", "agile", "scrum", "jira",
            "machine learning", "ml", "ai", "artificial intelligence", "data science",
            "data analysis", "statistics", "r", "matlab", "tensorflow", "pytorch",
            "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
            "html", "css", "bootstrap", "tailwind", "sass", "less",
            "php", "ruby", "go", "rust", "c++", "c#", ".net", "asp.net",
            "devops", "linux", "unix", "bash", "shell scripting", "powershell",
            "microservices", "api", "rest", "graphql", "soap", "xml", "json",
            "testing", "unit testing", "integration testing", "tdd", "bdd",
            "design patterns", "oop", "functional programming", "clean code"
        ]
    
    extracted_skills = []
    text_lower = text.lower()
    
    for skill in skill_list:
        if skill.lower() in text_lower:
            # Clean up skill name
            clean_skill = skill.replace("/", " ").title()
            if clean_skill not in extracted_skills:
                extracted_skills.append(clean_skill)
    
    return extracted_skills[:20]  # Limit to top 20 skills


def parse_experience(experience_text: str) -> Optional[Dict[str, Any]]:
    """Parse experience requirements from text"""
    if not experience_text:
        return None
    
    experience_text = experience_text.lower()
    
    # Extract years
    years_pattern = r'(\d+)[-+](\d+)?\s*years?'
    years_match = re.search(years_pattern, experience_text)
    
    if years_match:
        min_years = int(years_match.group(1))
        max_years = int(years_match.group(2)) if years_match.group(2) else min_years + 2
        avg_years = (min_years + max_years) / 2
        
        return {
            "min_years": min_years,
            "max_years": max_years,
            "avg_years": avg_years,
            "range": f"{min_years}-{max_years} years"
        }
    
    # Check for level indicators
    level_mapping = {
        "entry level": {"min": 0, "max": 2, "avg": 1},
        "junior": {"min": 1, "max": 3, "avg": 2},
        "mid level": {"min": 3, "max": 6, "avg": 4.5},
        "intermediate": {"min": 3, "max": 6, "avg": 4.5},
        "senior": {"min": 5, "max": 10, "avg": 7.5},
        "lead": {"min": 8, "max": 15, "avg": 11.5},
        "principal": {"min": 10, "max": 20, "avg": 15},
        "architect": {"min": 12, "max": 25, "avg": 18.5}
    }
    
    for level, years in level_mapping.items():
        if level in experience_text:
            return {
                "min_years": years["min"],
                "max_years": years["max"],
                "avg_years": years["avg"],
                "level": level.title()
            }
    
    return None


def parse_salary(salary_text: str) -> Optional[Dict[str, Any]]:
    """Parse salary information from text"""
    if not salary_text:
        return None
    
    salary_text = salary_text.lower()
    
    # Extract currency and amount
    currency_patterns = {
        "₹": "INR",
        "$": "USD",
        "€": "EUR",
        "£": "GBP"
    }
    
    currency = None
    for symbol, code in currency_patterns.items():
        if symbol in salary_text:
            currency = code
            break
    
    # Extract amount ranges
    amount_pattern = r'(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)'
    amount_match = re.search(amount_pattern, salary_text)
    
    if amount_match:
        min_amount = float(amount_match.group(1))
        max_amount = float(amount_match.group(2))
        
        # Check for units (LPA, K, etc.)
        if "lpa" in salary_text or "lakh" in salary_text:
            unit = "LPA"
            min_amount *= 100000  # Convert to actual amount
            max_amount *= 100000
        elif "k" in salary_text:
            unit = "K"
            min_amount *= 1000
            max_amount *= 1000
        else:
            unit = "per annum"
        
        return {
            "min_amount": min_amount,
            "max_amount": max_amount,
            "avg_amount": (min_amount + max_amount) / 2,
            "currency": currency or "INR",
            "unit": unit,
            "range": f"{amount_match.group(1)}-{amount_match.group(2)} {unit}"
        }
    
    return None


def extract_location_info(location_text: str) -> Dict[str, Any]:
    """Extract location information from text"""
    if not location_text:
        return {}
    
    location_text = location_text.lower()
    
    # Check for remote work indicators
    is_remote = any(word in location_text for word in ["remote", "work from home", "wfh"])
    is_hybrid = any(word in location_text for word in ["hybrid", "flexible"])
    
    # Extract city and state
    city_state_pattern = r'([a-z\s]+),\s*([a-z\s]+)'
    city_state_match = re.search(city_state_pattern, location_text)
    
    city = None
    state = None
    
    if city_state_match:
        city = city_state_match.group(1).strip().title()
        state = city_state_match.group(2).strip().title()
    
    return {
        "full_location": location_text.title(),
        "city": city,
        "state": state,
        "is_remote": is_remote,
        "is_hybrid": is_hybrid,
        "work_type": "remote" if is_remote else "hybrid" if is_hybrid else "onsite"
    }


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings"""
    if not text1 or not text2:
        return 0.0
    
    # Convert to lowercase and split into words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def format_date(date_obj: datetime) -> str:
    """Format date for display"""
    if not date_obj:
        return "Unknown"
    
    now = datetime.utcnow()
    diff = now - date_obj
    
    if diff.days == 0:
        if diff.seconds < 3600:
            return "Just now"
        elif diff.seconds < 7200:
            return "1 hour ago"
        else:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks} weeks ago"
    else:
        return date_obj.strftime("%B %d, %Y")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = re.sub(r'_+', '_', filename)
    
    # Limit length
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')
    
    return filename


def create_search_query(query: str, filters: Dict[str, Any] = None) -> str:
    """Create optimized search query from user input and filters"""
    if not filters:
        return query
    
    # Build enhanced query
    enhanced_parts = [query]
    
    if filters.get("location"):
        enhanced_parts.append(f"in {filters['location']}")
    
    if filters.get("experience"):
        enhanced_parts.append(f"{filters['experience']} experience")
    
    if filters.get("skills"):
        skills_str = ", ".join(filters["skills"][:3])  # Limit to 3 skills
        enhanced_parts.append(f"with {skills_str}")
    
    if filters.get("remote"):
        enhanced_parts.append("remote")
    
    return " ".join(enhanced_parts)


def rate_limit_check(last_request_time: datetime, min_interval: float = 1.0) -> bool:
    """Check if enough time has passed for rate limiting"""
    if not last_request_time:
        return True
    
    time_since_last = (datetime.utcnow() - last_request_time).total_seconds()
    return time_since_last >= min_interval


def log_api_request(endpoint: str, method: str, status_code: int, response_time: float, user_id: str = None):
    """Log API request details"""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "response_time": response_time,
        "user_id": user_id
    }
    
    logger.info(f"API Request: {json.dumps(log_data)}")


def validate_email(email: str) -> bool:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


def mask_sensitive_data(data: str, mask_char: str = "*") -> str:
    """Mask sensitive data like API keys"""
    if not data or len(data) < 8:
        return mask_char * len(data) if data else ""
    
    # Show first 4 and last 4 characters
    return data[:4] + mask_char * (len(data) - 8) + data[-4:]


def generate_session_token(user_id: str, timestamp: datetime = None) -> str:
    """Generate session token for user"""
    if not timestamp:
        timestamp = datetime.utcnow()
    
    token_data = f"{user_id}:{timestamp.isoformat()}"
    return hashlib.sha256(token_data.encode()).hexdigest()


def parse_query_parameters(query_string: str) -> Dict[str, Any]:
    """Parse query parameters from string"""
    try:
        return parse_qs(query_string)
    except Exception as e:
        logger.error(f"Error parsing query parameters: {e}")
        return {}


def is_valid_json(data: str) -> bool:
    """Check if string is valid JSON"""
    try:
        json.loads(data)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def normalize_company_name(company_name: str) -> str:
    """Normalize company name for consistent matching"""
    if not company_name:
        return ""
    
    # Remove common suffixes
    suffixes = [" inc", " corp", " ltd", " llc", " pvt", " limited", " corporation"]
    normalized = company_name.lower()
    
    for suffix in suffixes:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)]
            break
    
    # Remove extra whitespace and capitalize
    normalized = " ".join(normalized.split()).title()
    
    return normalized

