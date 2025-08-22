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


class NaukriScraper(BaseScraper):
    """Naukri.com job scraper"""
    
    def __init__(self, headless: bool = True, delay: float = 2.0):
        super().__init__(headless, delay)
        self.base_url = "https://www.naukri.com"
        self.search_url = "https://www.naukri.com/jobs-in-"
        
    def scrape_jobs(self, query: str, limit: int = 100) -> List[Job]:
        """Scrape jobs from Naukri based on query"""
        jobs = []
        try:
            # Navigate to search page
            search_url = f"{self.base_url}/job-listings-{query.replace(' ', '-')}"
            self.driver.get(search_url)
            self.wait_for_page_load()
            
            # Handle location popup if present
            self.handle_location_popup()
            
            # Scroll and collect jobs
            page = 1
            while len(jobs) < limit and page <= 10:  # Limit to 10 pages
                logger.info(f"Scraping page {page} from Naukri")
                
                # Wait for job listings to load
                job_elements = self.safe_find_elements(
                    By.CSS_SELECTOR, 
                    "div[data-testid='jobTuple']", 
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
            
            logger.info(f"Successfully scraped {len(jobs)} jobs from Naukri")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping jobs from Naukri: {e}")
            return jobs
    
    def parse_job_listing(self, job_element) -> Optional[Job]:
        """Parse individual job listing from Naukri"""
        try:
            # Extract job title
            title_element = job_element.find_element(By.CSS_SELECTOR, "a[data-testid='jobTitle']")
            title = self.safe_get_text(title_element)
            job_url = self.safe_get_attribute(title_element, "href")
            
            # Extract company name
            company_element = job_element.find_element(By.CSS_SELECTOR, "a[data-testid='companyName']")
            company = self.safe_get_text(company_element)
            
            # Extract location
            location_element = job_element.find_element(By.CSS_SELECTOR, "span[data-testid='location']")
            location = self.safe_get_text(location_element)
            
            # Extract experience
            experience_element = job_element.find_element(By.CSS_SELECTOR, "span[data-testid='experience']")
            experience = self.safe_get_text(experience_element)
            
            # Extract skills
            skills = []
            try:
                skill_elements = job_element.find_elements(By.CSS_SELECTOR, "span[data-testid='skill']")
                skills = [self.safe_get_text(skill) for skill in skill_elements]
            except:
                pass
            
            # Extract job description (basic)
            description = ""
            try:
                desc_element = job_element.find_element(By.CSS_SELECTOR, "div[data-testid='jobDescription']")
                description = self.safe_get_text(desc_element)
            except:
                description = f"Job opening for {title} at {company}"
            
            # Extract salary if available
            salary = ""
            try:
                salary_element = job_element.find_element(By.CSS_SELECTOR, "span[data-testid='salary']")
                salary = self.safe_get_text(salary_element)
            except:
                pass
            
            # Generate unique job ID
            job_id = f"naukri_{hash(job_url) % 1000000}"
            
            # Create Job object
            job = Job(
                job_id=job_id,
                title=title,
                company=company,
                location=location,
                experience=experience,
                skills=skills,
                description=description,
                posted_date=datetime.utcnow(),  # Naukri doesn't always show exact date
                url=job_url,
                platform=JobPlatform.NAUKRI,
                salary=salary if salary else None
            )
            
            return job
            
        except Exception as e:
            logger.error(f"Error parsing job listing: {e}")
            return None
    
    def handle_location_popup(self):
        """Handle location selection popup if present"""
        try:
            # Look for location popup
            popup = self.safe_find_element(
                By.CSS_SELECTOR, 
                "div[data-testid='locationPopup']", 
                timeout=5
            )
            
            if popup:
                # Try to close popup or select default location
                close_button = self.safe_find_element(
                    By.CSS_SELECTOR, 
                    "button[data-testid='closeButton']", 
                    timeout=3
                )
                if close_button:
                    self.safe_click(close_button)
                    time.sleep(1)
                    
        except Exception as e:
            logger.debug(f"Location popup handling: {e}")
    
    def go_to_next_page(self) -> bool:
        """Navigate to next page of results"""
        try:
            # Look for next page button
            next_button = self.safe_find_element(
                By.CSS_SELECTOR, 
                "a[data-testid='nextPage']", 
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
            # Modify search to include location
            location_query = f"{query} in {location}"
            return self.scrape_jobs(location_query, limit)
        except Exception as e:
            logger.error(f"Error searching by location: {e}")
            return []
    
    def search_by_experience(self, query: str, experience: str, limit: int = 100) -> List[Job]:
        """Search jobs by experience level"""
        try:
            # Modify search to include experience
            experience_query = f"{query} {experience} experience"
            return self.scrape_jobs(experience_query, limit)
        except Exception as e:
            logger.error(f"Error searching by experience: {e}")
            return []

