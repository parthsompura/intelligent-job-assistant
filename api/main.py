from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from typing import List, Optional
from contextlib import asynccontextmanager
import json
from datetime import datetime

from models.job import Job, JobSearchQuery, JobRecommendation, ResumeAnalysis
from models.chat import ChatRequest, ChatResponse
from ai_agent.agent import JobAssistantAgent
from ai_agent.recommendations import JobRecommender
from job_scraper.naukri_scraper import NaukriScraper
from job_scraper.linkedin_scraper import LinkedInScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for services
job_agent: Optional[JobAssistantAgent] = None
job_recommender: Optional[JobRecommender] = None

# In-memory storage for jobs (JSON-based)
jobs_storage: List[Job] = []
jobs_file = "jobs_data.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up Job Assistant API...")
    
    # Load existing jobs from JSON file
    global jobs_storage
    try:
        if os.path.exists(jobs_file):
            with open(jobs_file, 'r') as f:
                jobs_data = json.load(f)
                jobs_storage = [Job(**job) for job in jobs_data]
            logger.info(f"Loaded {len(jobs_storage)} jobs from JSON file")
        else:
            logger.info("No existing jobs file found, starting with empty storage")
    except Exception as e:
        logger.warning(f"Error loading jobs from JSON: {e}")
        jobs_storage = []
    
    # Initialize AI agent
    global job_agent, job_recommender
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("OpenAI API key not found, AI features will be limited")
            job_agent = None
        else:
            # Pass jobs data to the AI agent for intelligent search
            job_agent = JobAssistantAgent(openai_api_key, jobs_storage)
        
        job_recommender = JobRecommender()
        
    except Exception as e:
        logger.error(f"Failed to initialize AI services: {e}")
        job_agent = None
        job_recommender = None
    

    yield
    
    # Shutdown - save jobs to JSON file
    try:
        jobs_data = [job.dict() for job in jobs_storage]
        with open(jobs_file, 'w') as f:
            json.dump(jobs_data, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error saving jobs to JSON: {e}")


# Create FastAPI app
app = FastAPI(
    title="Intelligent Job Assistant API",
    description="AI-powered job intelligence system with scraping, recommendations, and chat",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Intelligent Job Assistant API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "Job scraping from Naukri and LinkedIn",
            "AI-powered job recommendations",
            "Intelligent chat interface",
            "Resume analysis and matching"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-15T10:00:00Z"}


# Job Management Endpoints

@app.get("/api/jobs", response_model=List[Job])
async def get_jobs(
    limit: int = 100,
    platform: Optional[str] = None
):
    """Get all jobs with optional filtering from JSON storage"""
    try:
        if platform:
            filtered_jobs = [job for job in jobs_storage if job.platform.value.lower() == platform.lower()]
            return filtered_jobs[:limit]
        else:
            return jobs_storage[:limit]
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve jobs")


@app.get("/api/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get job by ID from JSON storage"""
    try:
        for job in jobs_storage:
            if job.job_id == job_id:
                return job
        raise HTTPException(status_code=404, detail="Job not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve job")


@app.post("/api/jobs/search")
async def search_jobs(query: JobSearchQuery):
    """Search jobs based on criteria from JSON storage"""
    try:
        results = []
        query_lower = query.query.lower() if query.query else ""
        location_lower = query.location.lower() if query.location else ""
        
        for job in jobs_storage:
            # Simple text-based search
            matches = True
            
            if query_lower and query_lower not in job.title.lower() and query_lower not in job.description.lower():
                matches = False
            
            if location_lower and location_lower not in job.location.lower():
                matches = False
            
            if query.skills:
                job_skills_lower = [skill.lower() for skill in job.skills]
                query_skills_lower = [skill.lower() for skill in query.skills]
                if not any(skill in job_skills_lower for skill in query_skills_lower):
                    matches = False
            
            if matches:
                results.append(job)
            
            if len(results) >= query.limit:
                break
        
        return {
            "jobs": results,
            "total": len(results),
            "query": query.dict()
        }
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to search jobs")


@app.get("/api/jobs/{job_id}/recommendations", response_model=List[JobRecommendation])
async def get_job_recommendations(
    job_id: str,
    limit: int = 5
):
    """Get similar job recommendations"""
    try:
        if not job_recommender:
            raise HTTPException(status_code=503, detail="Recommendation service not available")
        
        recommendations = await job_recommender.get_similar_jobs(job_id, limit)
        return recommendations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")


# AI Agent Endpoints

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest
):
    """Chat with the AI job assistant"""
    try:
        if not job_agent:
            raise HTTPException(status_code=503, detail="AI Agent not available")
        
        response = await job_agent.query(
            message=request.message,
            session_id=request.session_id,
            user_id=request.user_id
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat request")


@app.post("/api/analyze-resume", response_model=ResumeAnalysis)
async def analyze_resume(request: dict):
    """Analyze resume and get job recommendations"""
    try:
        if not job_recommender:
            raise HTTPException(status_code=503, detail="Recommendation service not available")
        
        resume_text = request.get("resume_text", "")
        if not resume_text:
            raise HTTPException(status_code=400, detail="resume_text is required")
        
        analysis = await job_recommender.analyze_resume(resume_text)
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze resume")


# Scraping Endpoints

@app.post("/api/scrape/naukri")
async def scrape_naukri_jobs(
    background_tasks: BackgroundTasks,
    query: str = "software engineer",
    limit: int = 100
):
    """Trigger Naukri job scraping (runs in background)"""
    try:
        background_tasks.add_task(scrape_naukri_background, query, limit)
        return {
            "message": "Naukri scraping started in background",
            "query": query,
            "limit": limit,
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Error starting Naukri scraping: {e}")
        raise HTTPException(status_code=500, detail="Failed to start scraping")


@app.post("/api/scrape/linkedin")
async def scrape_linkedin_jobs(
    background_tasks: BackgroundTasks,
    query: str = "software engineer",
    limit: int = 100
):
    """Trigger LinkedIn job scraping (runs in background)"""
    try:
        background_tasks.add_task(scrape_linkedin_background, query, limit)
        return {
            "message": "LinkedIn scraping started in background",
            "query": query,
            "limit": limit,
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Error starting LinkedIn scraping: {e}")
        raise HTTPException(status_code=500, detail="Failed to start scraping")


# Background scraping functions

async def scrape_naukri_background(query: str, limit: int):
    """Background task for Naukri scraping"""
    try:
        logger.info(f"Starting Naukri scraping for: {query}")
        
        scraper = NaukriScraper(headless=True, delay=2.0)
        jobs = scraper.scrape_jobs(query, limit)
        
        # Save jobs to JSON storage
        global jobs_storage
        saved_count = 0
        for job in jobs:
            # Check if job already exists
            if not any(existing_job.job_id == job.job_id for existing_job in jobs_storage):
                jobs_storage.append(job)
                saved_count += 1
        
        # Update AI agent with new jobs data
        global job_agent
        if job_agent:
            job_agent.update_jobs_data(jobs_storage)
            logger.info(f"Updated AI agent with {len(jobs_storage)} jobs")
        
        # Save to JSON file
        try:
            jobs_data = [job.dict() for job in jobs_storage]
            with open(jobs_file, 'w') as f:
                json.dump(jobs_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving jobs to JSON: {e}")
        
        logger.info(f"Naukri scraping completed: {saved_count}/{len(jobs)} jobs saved to JSON")
        
    except Exception as e:
        logger.error(f"Error in Naukri background scraping: {e}")


async def scrape_linkedin_background(query: str, limit: int):
    """Background task for LinkedIn scraping"""
    try:
        logger.info(f"Starting LinkedIn scraping for: {query}")
        
        scraper = LinkedInScraper(headless=True, delay=2.0)
        jobs = scraper.scrape_jobs(query, limit)
        
        # Save jobs to JSON storage
        global jobs_storage
        saved_count = 0
        for job in jobs:
            # Check if job already exists
            if not any(existing_job.job_id == job.job_id for existing_job in jobs_storage):
                jobs_storage.append(job)
                saved_count += 1
        
        # Update AI agent with new jobs data
        global job_agent
        if job_agent:
            job_agent.update_jobs_data(jobs_storage)
            logger.info(f"Updated AI agent with {len(jobs_storage)} jobs")
        
        # Save to JSON file
        try:
            jobs_data = [job.dict() for job in jobs_storage]
            with open(jobs_file, 'w') as f:
                json.dump(jobs_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving jobs to JSON: {e}")
        
        logger.info(f"LinkedIn scraping completed: {saved_count}/{len(jobs)} jobs saved to JSON")
        
    except Exception as e:
        logger.error(f"Error in LinkedIn background scraping: {e}")


# Statistics Endpoints

@app.get("/api/stats")
async def get_stats():
    """Get system statistics from JSON storage"""
    try:
        total_jobs = len(jobs_storage)
        
        # Count jobs by platform
        platform_counts = {}
        for job in jobs_storage:
            platform = job.platform.value
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        return {
            "total_jobs": total_jobs,
            "platforms": platform_counts,
            "ai_agent": "active" if job_agent else "inactive",
            "recommendations": "active" if job_recommender else "inactive",
            "storage": "JSON file"
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


# Error handlers

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "path": str(request.url)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "path": str(request.url)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

