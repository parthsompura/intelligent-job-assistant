import time
import logging
from datetime import datetime
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_scraper import BaseScraper
from models.job import Job, JobPlatform
import re

logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    """LinkedIn job scraper"""
    
    def __init__(self, headless: bool = True, delay: float = 2.0):
        super().__init__(headless, delay)
        self.base_url = "https://www.linkedin.com"
        self.jobs_url = "https://www.linkedin.com/jobs"
        
    def scrape_jobs(self, query: str, limit: int = 100) -> List[Job]:
        """Scrape jobs from LinkedIn based on query"""
        jobs = []
        try:
            # Navigate to LinkedIn jobs page
            self.driver.get(self.jobs_url)
            self.wait_for_page_load()
            
            # Handle login popup if present
            self.handle_login_popup()
            
            # Search for jobs
            search_box = self.safe_find_element(
                By.CSS_SELECTOR, 
                "input[aria-label='Search by title, skill, or company']", 
                timeout=15
            )
            
            if search_box:
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.RETURN)
                self.wait_for_page_load()
                
                # Scroll and collect jobs
                page = 1
                while len(jobs) < limit and page <= 10:  # Limit to 10 pages
                    logger.info(f"Scraping page {page} from LinkedIn")
                    
                    # Wait for job listings to load
                    job_elements = self.safe_find_elements(
                        By.CSS_SELECTOR, 
                        "div.base-card", 
                        timeout=15
                    )
                    
                    if not job_elements:
                        logger.warning(f"No job elements found on page {page}")
                        break
                    
                    # Parse jobs from current page
                    for job_element in job_elements:
                        if len(jobs) >= limit:
                            break
                        
                        try:
                            job = self.parse_job_listing(job_element)
                            if job:
                                jobs.append(job)
                                logger.debug(f"Parsed job: {job.title} at {job.company}")
                        except Exception as e:
                            logger.error(f"Error parsing job element: {e}")
                            continue
                    
                    # Try to go to next page
                    if len(jobs) < limit:
                        if not self.go_to_next_page():
                            logger.info("No more pages available")
                            break
                        page += 1
                        self.rate_limit()
                
                logger.info(f"Successfully scraped {len(jobs)} jobs from LinkedIn")
                return jobs
            else:
                logger.error("Search box not found on LinkedIn jobs page")
                return jobs
                
        except Exception as e:
            logger.error(f"Error scraping jobs from LinkedIn: {e}")
            return jobs
    
    def parse_job_listing(self, job_element) -> Optional[Job]:
        """Parse individual job listing from LinkedIn"""
        try:
            # Extract job title
            title_element = job_element.find_element(By.CSS_SELECTOR, "h3.base-search-card__title")
            title = self.safe_get_text(title_element)
            
            # Extract company name
            company_element = job_element.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle")
            company = self.safe_get_text(company_element)
            
            # Extract location
            location_element = job_element.find_element(By.CSS_SELECTOR, "span.job-search-card__location")
            location = self.safe_get_text(location_element)
            
            # Extract job URL
            job_link = job_element.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
            job_url = self.safe_get_attribute(job_link, "href")
            
            # Extract posted time
            posted_element = job_element.find_element(By.CSS_SELECTOR, "time.job-search-card__listdate")
            posted_text = self.safe_get_attribute(posted_element, "datetime")
            
            # Parse posted date
            posted_date = datetime.utcnow()
            if posted_text:
                try:
                    posted_date = datetime.fromisoformat(posted_text.replace('Z', '+00:00'))
                except:
                    pass
            
            # Extract job type and remote work info
            job_type = ""
            remote_work = False
            try:
                job_type_element = job_element.find_element(By.CSS_SELECTOR, "span.job-search-card__job-type")
                job_type = self.safe_get_text(job_type_element)
                remote_work = "remote" in job_type.lower()
            except:
                pass
            
            # Extract skills (LinkedIn doesn't show skills in list view)
            skills = []
            
            # Basic description
            description = f"Job opening for {title} at {company}"
            
            # Generate unique job ID
            job_id = f"linkedin_{hash(job_url) % 1000000}"
            
            # Create Job object
            job = Job(
                job_id=job_id,
                title=title,
                company=company,
                location=location,
                experience="",  # LinkedIn doesn't show experience in list view
                skills=skills,
                description=description,
                posted_date=posted_date,
                url=job_url,
                platform=JobPlatform.LINKEDIN,
                job_type=job_type if job_type else None,
                remote_work=remote_work
            )
            
            return job
            
        except Exception as e:
            logger.error(f"Error parsing job listing: {e}")
            return None
    
    def handle_login_popup(self):
        """Handle login popup if present"""
        try:
            # Look for login popup
            popup = self.safe_find_element(
                By.CSS_SELECTOR, 
                "div[data-testid='login-modal']", 
                timeout=5
            )
            
            if popup:
                # Try to close popup
                close_button = self.safe_find_element(
                    By.CSS_SELECTOR, 
                    "button[aria-label='Dismiss']", 
                    timeout=3
                )
                if close_button:
                    self.safe_click(close_button)
                    time.sleep(1)
                    
        except Exception as e:
            logger.debug(f"Login popup handling: {e}")
    
    def go_to_next_page(self) -> bool:
        """Navigate to next page of results"""
        try:
            # Look for next page button
            next_button = self.safe_find_element(
                By.CSS_SELECTOR, 
                "button[aria-label='Next']", 
                timeout=5
            )
            
            if next_button and next_button.is_enabled():
                self.safe_click(next_button)
                self.wait_for_page_load()
                return True
            else:
                return False
                
        except Exception as e:
            logger.debug(f"Next page navigation: {e}")
            return False
    
    def search_by_location(self, query: str, location: str, limit: int = 100) -> List[Job]:
        """Search jobs by specific location"""
        try:
            # Navigate to jobs page
            self.driver.get(self.jobs_url)
            self.wait_for_page_load()
            
            # Handle login popup
            self.handle_login_popup()
            
            # Search for jobs with location
            search_box = self.safe_find_element(
                By.CSS_SELECTOR, 
                "input[aria-label='Search by title, skill, or company']", 
                timeout=15
            )
            
            if search_box:
                search_box.clear()
                search_box.send_keys(f"{query} in {location}")
                search_box.send_keys(Keys.RETURN)
                self.wait_for_page_load()
                
                # Use the same scraping logic
                return self.scrape_jobs_from_current_page(limit)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error searching by location: {e}")
            return []
    
    def scrape_jobs_from_current_page(self, limit: int) -> List[Job]:
        """Scrape jobs from the current page"""
        jobs = []
        try:
            job_elements = self.safe_find_elements(
                By.CSS_SELECTOR, 
                "div.base-card", 
                timeout=15
            )
            
            for job_element in job_elements[:limit]:
                try:
                    job = self.parse_job_listing(job_element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing job element: {e}")
                    continue
                    
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping jobs from current page: {e}")
            return jobs
    
    def get_detailed_job_info(self, job_url: str) -> Optional[Job]:
        """Get detailed job information by visiting the job page"""
        try:
            self.driver.get(job_url)
            self.wait_for_page_load()
            
            # Extract detailed information
            title = self.safe_get_text(
                self.safe_find_element(By.CSS_SELECTOR, "h1.top-card-layout__title")
            )
            
            company = self.safe_get_text(
                self.safe_find_element(By.CSS_SELECTOR, "a.topcard__org-name-link")
            )
            
            location = self.safe_get_text(
                self.safe_find_element(By.CSS_SELECTOR, "span.topcard__flavor--bullet")
            )
            
            description = self.safe_get_text(
                self.safe_find_element(By.CSS_SELECTOR, "div.show-more-less-html__markup")
            )
            
            # Extract skills from description
            skills = self.extract_skills_from_description(description)
            
            # Create enhanced job object
            job = Job(
                job_id=f"linkedin_detailed_{hash(job_url) % 1000000}",
                title=title,
                company=company,
                location=location,
                experience="",
                skills=skills,
                description=description,
                posted_date=datetime.utcnow(),
                url=job_url,
                platform=JobPlatform.LINKEDIN
            )
            
            return job
            
        except Exception as e:
            logger.error(f"Error getting detailed job info: {e}")
            return None
    
    def extract_skills_from_description(self, description: str) -> List[str]:
        """Extract skills from job description"""
        # Common technical skills
        common_skills = [
            "python", "java", "javascript", "react", "angular", "vue", "node.js",
            "sql", "mongodb", "aws", "azure", "docker", "kubernetes", "git",
            "machine learning", "ai", "data science", "devops", "agile"
        ]
        
        skills = []
        description_lower = description.lower()
        
        for skill in common_skills:
            if skill in description_lower:
                skills.append(skill.title())
        
        return skills

