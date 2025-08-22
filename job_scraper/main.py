#!/usr/bin/env python3
"""
Main job scraper script for the Intelligent Job Assistant
"""

import asyncio
import logging
import sys
import os
import json
from typing import List, Optional
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from job_scraper.naukri_scraper import NaukriScraper
from job_scraper.linkedin_scraper import LinkedInScraper
from models.job import Job, JobPlatform


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JobScraperManager:
    """Manager for job scraping operations"""
    
    def __init__(self):
        pass
        
    async def initialize(self):
        """Initialize scraper manager"""
        try:
            logger.info("Job scraper manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize scraper manager: {e}")
            return False
    
    async def scrape_naukri_jobs(self, query: str, limit: int = 100) -> List[Job]:
        """Scrape jobs from Naukri"""
        try:
            logger.info(f"Starting Naukri scraping for: {query}")
            
            with NaukriScraper(headless=True, delay=2.0) as scraper:
                jobs = scraper.scrape_jobs(query, limit)
            
            logger.info(f"Naukri scraping completed: {len(jobs)} jobs found")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Naukri jobs: {e}")
            return []
    
    async def scrape_linkedin_jobs(self, query: str, limit: int = 100) -> List[Job]:
        """Scrape jobs from LinkedIn"""
        try:
            logger.info(f"Starting LinkedIn scraping for: {query}")
            
            with LinkedInScraper(headless=True, delay=2.0) as scraper:
                jobs = scraper.scrape_jobs(query, limit)
            
            logger.info(f"LinkedIn scraping completed: {len(jobs)} jobs found")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn jobs: {e}")
            return []
    
    async def save_jobs(self, jobs: List[Job]) -> int:
        """Save jobs to JSON file"""
        try:
            # Load existing jobs
            jobs_file = "jobs_data.json"
            existing_jobs = []
            
            if os.path.exists(jobs_file):
                with open(jobs_file, 'r') as f:
                    existing_jobs = json.load(f)
            
            # Add new jobs (avoid duplicates)
            saved_count = 0
            existing_titles = {job.get('title', '') + job.get('company', '') for job in existing_jobs}
            
            for job in jobs:
                job_key = job.title + job.company
                if job_key not in existing_titles:
                    existing_jobs.append(job.dict())
                    saved_count += 1
                    logger.debug(f"Saved job: {job.title} at {job.company}")
                else:
                    logger.debug(f"Job already exists: {job.title}")
            
            # Save to JSON file
            with open(jobs_file, 'w') as f:
                json.dump(existing_jobs, f, indent=2, default=str)
            
            logger.info(f"Successfully saved {saved_count}/{len(jobs)} jobs to JSON")
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving jobs: {e}")
            return 0
    
    async def scrape_and_save(self, platform: str, query: str, limit: int = 100):
        """Scrape jobs from specified platform and save to JSON"""
        try:
            # Scrape jobs
            if platform.lower() == "naukri":
                jobs = await self.scrape_naukri_jobs(query, limit)
            elif platform.lower() == "linkedin":
                jobs = await self.scrape_linkedin_jobs(query, limit)
            else:
                logger.error(f"Unsupported platform: {platform}")
                return
            
            if not jobs:
                logger.warning("No jobs found")
                return
            
            # Save to JSON file
            saved_count = await self.save_jobs(jobs)
            
            # Print summary
            print(f"\nScraping Summary for {platform.upper()}:")
            print(f"Query: {query}")
            print(f"Jobs found: {len(jobs)}")
            print(f"Jobs saved: {saved_count}")
            
            # Show sample jobs
            if jobs:
                print(f"\nSample Jobs:")
                for i, job in enumerate(jobs[:3], 1):
                    print(f"{i}. {job.title} at {job.company}")
                    print(f"   Location: {job.location}")
                    print(f"   Experience: {job.experience}")
                    print(f"   Skills: {', '.join(job.skills[:3])}")
                    print()
            
        except Exception as e:
            logger.error(f"Error in scrape_and_save: {e}")
    
    async def run_bulk_scraping(self, queries: List[str], platforms: List[str], limit: int = 100):
        """Run bulk scraping for multiple queries and platforms"""
        try:
            total_jobs = 0
            total_saved = 0
            
            print(f"\nStarting Bulk Scraping")
            print(f"Queries: {', '.join(queries)}")
            print(f"Platforms: {', '.join(platforms)}")
            print(f"Limit per query: {limit}")
            print("=" * 60)
            
            for platform in platforms:
                for query in queries:
                    print(f"\nScraping {platform.upper()} for: {query}")
                    
                    # Scrape and save
                    if platform.lower() == "naukri":
                        jobs = await self.scrape_naukri_jobs(query, limit)
                    elif platform.lower() == "linkedin":
                        jobs = await self.scrape_linkedin_jobs(query, limit)
                    else:
                        continue
                    
                    if jobs:
                        saved_count = await self.save_jobs(jobs)
                        total_jobs += len(jobs)
                        total_saved += saved_count
                        
                        print(f"{platform.upper()}: {saved_count}/{len(jobs)} jobs saved")
                    
                    # Rate limiting between requests
                    await asyncio.sleep(5)
            
            # Final summary
            print("\n" + "=" * 60)
            print(f"Bulk Scraping Completed!")
            print(f"Total jobs found: {total_jobs}")
            print(f"Total jobs saved: {total_saved}")
            print(f"Success rate: {(total_saved/total_jobs)*100:.1f}%" if total_jobs > 0 else "N/A")
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"Error in bulk scraping: {e}")
    
    async def close(self):
        """Close scraper manager"""
        pass


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Job Scraper for Intelligent Job Assistant")
    parser.add_argument("--platform", "-p", choices=["naukri", "linkedin", "both"], 
                       default="both", help="Platform to scrape")
    parser.add_argument("--query", "-q", default="software engineer", 
                       help="Job search query")
    parser.add_argument("--limit", "-l", type=int, default=100, 
                       help="Maximum number of jobs to scrape per query")
    parser.add_argument("--bulk", "-b", action="store_true", 
                       help="Run bulk scraping with predefined queries")
    parser.add_argument("--save", "-s", action="store_true", 
                       help="Save scraped jobs to JSON file")
    
    args = parser.parse_args()
    
    # Initialize scraper manager
    scraper_manager = JobScraperManager()
    
    if not await scraper_manager.initialize():
        logger.error("Failed to initialize scraper manager")
        sys.exit(1)
    
    try:
        if args.bulk:
            # Bulk scraping with predefined queries
            queries = [
                "software engineer",
                "data scientist", 
                "machine learning engineer",
                "full stack developer",
                "devops engineer",
                "product manager",
                "ui ux designer",
                "data analyst"
            ]
            
            platforms = ["naukri", "linkedin"] if args.platform == "both" else [args.platform]
            
            await scraper_manager.run_bulk_scraping(queries, platforms, args.limit)
            
        else:
            # Single platform scraping
            if args.platform == "both":
                # Scrape both platforms
                for platform in ["naukri", "linkedin"]:
                    await scraper_manager.scrape_and_save(platform, args.query, args.limit)
            else:
                # Scrape single platform
                await scraper_manager.scrape_and_save(args.platform, args.query, args.limit)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    
    finally:
        await scraper_manager.close()


if __name__ == "__main__":
    asyncio.run(main())

