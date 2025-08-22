import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path for imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from job_scraper.naukri_scraper import NaukriScraper
from job_scraper.linkedin_scraper import LinkedInScraper
from models.job import Job, JobPlatform


class TestNaukriScraper:
    """Test cases for Naukri scraper"""
    
    @pytest.fixture
    def mock_driver(self):
        """Mock WebDriver"""
        driver = Mock()
        driver.execute_script = Mock()
        driver.quit = Mock()
        return driver
    
    @pytest.fixture
    def mock_element(self):
        """Mock web element"""
        element = Mock()
        element.text = "Test Job Title"
        element.get_attribute.return_value = "https://example.com/job"
        return element
    
    @patch('job_scraper.naukri_scraper.ChromeDriverManager')
    @patch('job_scraper.naukri_scraper.webdriver.Chrome')
    def test_setup_driver(self, mock_chrome, mock_driver_manager, mock_driver):
        """Test WebDriver setup"""
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
        mock_chrome.return_value = mock_driver
        
        scraper = NaukriScraper()
        result = scraper.setup_driver()
        
        assert result is True
        assert scraper.driver is not None
        assert scraper.wait is not None
    
    def test_parse_job_listing(self, mock_element):
        """Test job listing parsing"""
        scraper = NaukriScraper()
        
        # Mock the find_element calls
        mock_element.find_element.side_effect = [
            Mock(text="Software Engineer", get_attribute=lambda x: "https://example.com/job"),
            Mock(text="TechCorp"),
            Mock(text="Bangalore"),
            Mock(text="3-5 years"),
            Mock(text="Python, React"),
            Mock(text="Job description here"),
            Mock(text="₹15-25 LPA")
        ]
        
        # Mock find_elements for skills
        mock_element.find_elements.return_value = [
            Mock(text="Python"),
            Mock(text="React")
        ]
        
        job = scraper.parse_job_listing(mock_element)
        
        assert job is not None
        assert job.title == "Software Engineer"
        assert job.company == "TechCorp"
        assert job.location == "Bangalore"
        assert job.experience == "3-5 years"
        assert "Python" in job.skills
        assert "React" in job.skills
        assert job.platform == JobPlatform.NAUKRI


class TestLinkedInScraper:
    """Test cases for LinkedIn scraper"""
    
    @pytest.fixture
    def mock_driver(self):
        """Mock WebDriver"""
        driver = Mock()
        driver.execute_script = Mock()
        driver.quit = Mock()
        return driver
    
    @pytest.fixture
    def mock_element(self):
        """Mock web element"""
        element = Mock()
        element.text = "Test Job Title"
        element.get_attribute.return_value = "https://example.com/job"
        return element
    
    @patch('job_scraper.linkedin_scraper.ChromeDriverManager')
    @patch('job_scraper.linkedin_scraper.webdriver.Chrome')
    def test_setup_driver(self, mock_chrome, mock_driver_manager, mock_driver):
        """Test WebDriver setup"""
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
        mock_chrome.return_value = mock_driver
        
        scraper = LinkedInScraper()
        result = scraper.setup_driver()
        
        assert result is True
        assert scraper.driver is not None
        assert scraper.wait is not None
    
    def test_parse_job_listing(self, mock_element):
        """Test job listing parsing"""
        scraper = LinkedInScraper()
        
        # Mock the find_element calls
        mock_element.find_element.side_effect = [
            Mock(text="Data Scientist"),
            Mock(text="DataCorp"),
            Mock(text="Mumbai"),
            Mock(text="https://example.com/job"),
            Mock(get_attribute=lambda x: "2024-01-15T10:00:00Z"),
            Mock(text="Full-time")
        ]
        
        job = scraper.parse_job_listing(mock_element)
        
        assert job is not None
        assert job.title == "Data Scientist"
        assert job.company == "DataCorp"
        assert job.location == "Mumbai"
        assert job.platform == JobPlatform.LINKEDIN
    
    def test_extract_skills_from_description(self):
        """Test skills extraction from job description"""
        scraper = LinkedInScraper()
        
        description = """
        We are looking for a Python developer with experience in:
        - Machine Learning and AI
        - SQL databases
        - AWS cloud services
        - Docker containers
        """
        
        skills = scraper.extract_skills_from_description(description)
        
        expected_skills = ["Python", "Machine Learning", "AI", "SQL", "AWS", "Docker"]
        for skill in expected_skills:
            assert skill in skills


class TestBaseScraper:
    """Test cases for base scraper functionality"""
    
    def test_safe_find_element(self):
        """Test safe element finding"""
        scraper = NaukriScraper()
        scraper.driver = Mock()
        scraper.wait = Mock()
        
        # Mock successful element finding
        mock_element = Mock()
        scraper.wait.until.return_value = mock_element
        
        result = scraper.safe_find_element("id", "test-id")
        assert result == mock_element
    
    def test_safe_get_text(self):
        """Test safe text extraction"""
        scraper = NaukriScraper()
        
        # Test with valid element
        mock_element = Mock()
        mock_element.text = "Test Text"
        result = scraper.safe_get_text(mock_element)
        assert result == "Test Text"
        
        # Test with None element
        result = scraper.safe_get_text(None)
        assert result == ""
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        scraper = NaukriScraper(delay=0.1)
        
        start_time = datetime.now()
        scraper.rate_limit()
        end_time = datetime.now()
        
        # Should have some delay
        assert (end_time - start_time).total_seconds() >= 0.1


# Integration tests
@pytest.mark.integration
class TestScraperIntegration:
    """Integration tests for scrapers (require actual web access)"""
    
    @pytest.mark.skip(reason="Requires actual web access")
    def test_naukri_scraping_integration(self):
        """Test actual Naukri scraping (integration test)"""
        scraper = NaukriScraper(headless=True, delay=1.0)
        
        with scraper:
            jobs = scraper.scrape_jobs("python developer", limit=5)
            
            assert len(jobs) > 0
            assert all(isinstance(job, Job) for job in jobs)
            assert all(job.platform == JobPlatform.NAUKRI for job in jobs)
    
    @pytest.mark.skip(reason="Requires actual web access")
    def test_linkedin_scraping_integration(self):
        """Test actual LinkedIn scraping (integration test)"""
        scraper = LinkedInScraper(headless=True, delay=1.0)
        
        with scraper:
            jobs = scraper.scrape_jobs("data scientist", limit=5)
            
            assert len(jobs) > 0
            assert all(isinstance(job, Job) for job in jobs)
            assert all(job.platform == JobPlatform.LINKEDIN for job in jobs)


if __name__ == "__main__":
    pytest.main([__file__])

