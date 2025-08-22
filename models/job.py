from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class JobPlatform(str, Enum):
    """Supported job platforms"""
    NAUKRI = "naukri"
    LINKEDIN = "linkedin"


class Job(BaseModel):
    """Job posting data model"""
    job_id: str = Field(..., description="Unique identifier for the job")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    experience: str = Field(..., description="Required experience level")
    skills: List[str] = Field(default_factory=list, description="Required skills")
    description: str = Field(..., description="Job description")
    posted_date: datetime = Field(..., description="Date when job was posted")
    url: HttpUrl = Field(..., description="Job posting URL")
    platform: JobPlatform = Field(..., description="Source platform")
    salary: Optional[str] = Field(None, description="Salary information")
    job_type: Optional[str] = Field(None, description="Full-time, Part-time, Contract")
    remote_work: Optional[bool] = Field(None, description="Remote work availability")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class JobSearchQuery(BaseModel):
    """Job search query model"""
    query: str = Field(..., description="Search query")
    location: Optional[str] = Field(None, description="Location filter")
    experience: Optional[str] = Field(None, description="Experience level filter")
    skills: Optional[List[str]] = Field(None, description="Skills filter")
    platform: Optional[JobPlatform] = Field(None, description="Platform filter")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum results")


class JobRecommendation(BaseModel):
    """Job recommendation model"""
    job: Job
    score: float = Field(..., ge=0, le=1, description="Recommendation score")
    rationale: str = Field(..., description="Reason for recommendation")
    skills_match: List[str] = Field(default_factory=list, description="Matching skills")
    location_match: bool = Field(..., description="Location preference match")


class ResumeAnalysis(BaseModel):
    """Resume analysis result model"""
    skills: List[str] = Field(default_factory=list, description="Extracted skills")
    experience_years: Optional[float] = Field(None, description="Years of experience")
    preferred_locations: List[str] = Field(default_factory=list, description="Preferred locations")
    job_preferences: List[str] = Field(default_factory=list, description="Job preferences")
    recommendations: List[JobRecommendation] = Field(default_factory=list, description="Job recommendations")

