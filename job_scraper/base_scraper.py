import time
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from models.job import Job, JobPlatform
import os

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for job scrapers"""
    
    def __init__(self, headless: bool = True, delay: float = 2.0):
        self.headless = headless
        self.delay = delay
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Use webdriver-manager to handle driver installation
            driver_path = ChromeDriverManager().install()
            self.driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            logger.info("WebDriver setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            return False
    
    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
    
    def safe_find_element(self, by: By, value: str, timeout: int = 10):
        """Safely find element with timeout"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {by} = {value}")
            return None
    
    def safe_find_elements(self, by: By, value: str, timeout: int = 10):
        """Safely find elements with timeout"""
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
            return elements
        except TimeoutException:
            logger.warning(f"Elements not found: {by} = {value}")
            return []
    
    def safe_click(self, element):
        """Safely click element"""
        try:
            if element:
                element.click()
                return True
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
        return False
    
    def safe_get_text(self, element):
        """Safely get text from element"""
        try:
            if element:
                return element.text.strip()
        except Exception as e:
            logger.error(f"Error getting text from element: {e}")
        return ""
    
    def safe_get_attribute(self, element, attribute):
        """Safely get attribute from element"""
        try:
            if element:
                return element.get_attribute(attribute)
        except Exception as e:
            logger.error(f"Error getting attribute {attribute}: {e}")
        return ""
    
    def scroll_to_bottom(self):
        """Scroll to bottom of page"""
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.delay)
        except Exception as e:
            logger.error(f"Error scrolling to bottom: {e}")
    
    def scroll_to_element(self, element):
        """Scroll to specific element"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(self.delay)
        except Exception as e:
            logger.error(f"Error scrolling to element: {e}")
    
    def wait_for_page_load(self, timeout: int = 10):
        """Wait for page to load completely"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(self.delay)
            return True
        except TimeoutException:
            logger.warning("Page load timeout")
            return False
    
    def handle_captcha(self):
        """Handle CAPTCHA if present (to be implemented by subclasses)"""
        # This is a placeholder - actual implementation depends on the platform
        logger.warning("CAPTCHA detected - manual intervention may be required")
        return False
    
    def rate_limit(self):
        """Apply rate limiting between requests"""
        time.sleep(self.delay)
    
    @abstractmethod
    def scrape_jobs(self, query: str, limit: int = 100) -> List[Job]:
        """Scrape jobs based on query - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def parse_job_listing(self, job_element) -> Optional[Job]:
        """Parse individual job listing - must be implemented by subclasses"""
        pass
    
    def __enter__(self):
        """Context manager entry"""
        if self.setup_driver():
            return self
        raise RuntimeError("Failed to setup WebDriver")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_driver()

