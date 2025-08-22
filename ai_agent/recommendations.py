import logging
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import numpy as np
from models.job import Job, JobRecommendation, ResumeAnalysis
import re

logger = logging.getLogger(__name__)


class JobRecommender:
    """Job recommendation system using ML and similarity matching"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.job_vectors = None
        self.jobs = []
        
    async def analyze_resume(self, resume_text: str) -> ResumeAnalysis:
        """Analyze resume and extract key information"""
        try:
            # Extract skills from resume
            skills = self.extract_skills_from_text(resume_text)
            
            # Extract experience years
            experience_years = self.extract_experience_years(resume_text)
            
            # Extract preferred locations
            preferred_locations = self.extract_preferred_locations(resume_text)
            
            # Extract job preferences
            job_preferences = self.extract_job_preferences(resume_text)
            
            # Get job recommendations based on resume
            recommendations = await self.get_recommendations_for_resume(
                resume_text, skills, experience_years, preferred_locations
            )
            
            # Create resume analysis result
            analysis = ResumeAnalysis(
                skills=skills,
                experience_years=experience_years,
                preferred_locations=preferred_locations,
                job_preferences=job_preferences,
                recommendations=recommendations
            )
            
            logger.info(f"Resume analysis completed: {len(skills)} skills, {experience_years} years experience")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {e}")
            return ResumeAnalysis()
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract technical skills from text"""
        # Common technical skills
        technical_skills = [
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
        
        for skill in technical_skills:
            if skill in text_lower:
                # Clean up skill name
                clean_skill = skill.replace("/", " ").title()
                if clean_skill not in extracted_skills:
                    extracted_skills.append(clean_skill)
        
        # Also look for skills mentioned with variations
        skill_patterns = [
            r"(\w+)\s+programming",
            r"(\w+)\s+development",
            r"(\w+)\s+framework",
            r"(\w+)\s+library",
            r"(\w+)\s+tool",
            r"(\w+)\s+technology"
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if match not in [skill.lower() for skill in extracted_skills]:
                    extracted_skills.append(match.title())
        
        return extracted_skills[:20]  # Limit to top 20 skills
    
    def extract_experience_years(self, text: str) -> Optional[float]:
        """Extract years of experience from text"""
        # Common experience patterns
        experience_patterns = [
            r"(\d+)\s+years?\s+of?\s+experience",
            r"(\d+)\s+years?\s+in\s+\w+",
            r"experience:\s*(\d+)\s+years?",
            r"(\d+)\+?\s+years?\s+experience",
            r"senior\s+level\s+\((\d+)\s+years?\)"
        ]
        
        text_lower = text.lower()
        
        for pattern in experience_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    years = float(match.group(1))
                    return years
                except ValueError:
                    continue
        
        # Look for experience level indicators
        if "entry level" in text_lower or "junior" in text_lower:
            return 1.0
        elif "mid level" in text_lower or "intermediate" in text_lower:
            return 3.0
        elif "senior" in text_lower:
            return 7.0
        elif "lead" in text_lower or "principal" in text_lower:
            return 10.0
        elif "architect" in text_lower or "director" in text_lower:
            return 15.0
        
        return None
    
    def extract_preferred_locations(self, text: str) -> List[str]:
        """Extract preferred locations from text"""
        # Common location patterns
        location_patterns = [
            r"location:\s*([A-Za-z\s,]+)",
            r"based\s+in\s+([A-Za-z\s,]+)",
            r"from\s+([A-Za-z\s,]+)",
            r"willing\s+to\s+relocate\s+to\s+([A-Za-z\s,]+)",
            r"preferred\s+location:\s*([A-Za-z\s,]+)"
        ]
        
        locations = []
        text_lower = text.lower()
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                location = match.strip()
                if location and location not in locations:
                    locations.append(location.title())
        
        # Look for common city names
        common_cities = [
            "bangalore", "mumbai", "delhi", "pune", "hyderabad", "chennai",
            "kolkata", "noida", "gurgaon", "remote", "hybrid"
        ]
        
        for city in common_cities:
            if city in text_lower and city.title() not in locations:
                locations.append(city.title())
        
        return locations[:5]  # Limit to top 5 locations
    
    def extract_job_preferences(self, text: str) -> List[str]:
        """Extract job preferences from text"""
        preferences = []
        text_lower = text.lower()
        
        # Job type preferences
        if "full time" in text_lower or "full-time" in text_lower:
            preferences.append("Full-time")
        if "part time" in text_lower or "part-time" in text_lower:
            preferences.append("Part-time")
        if "contract" in text_lower:
            preferences.append("Contract")
        if "remote" in text_lower:
            preferences.append("Remote")
        if "hybrid" in text_lower:
            preferences.append("Hybrid")
        
        # Industry preferences
        if "startup" in text_lower:
            preferences.append("Startup")
        if "enterprise" in text_lower or "corporate" in text_lower:
            preferences.append("Enterprise")
        if "fintech" in text_lower or "finance" in text_lower:
            preferences.append("Fintech")
        if "healthcare" in text_lower or "medical" in text_lower:
            preferences.append("Healthcare")
        if "ecommerce" in text_lower or "retail" in text_lower:
            preferences.append("E-commerce")
        
        return preferences
    
    async def get_recommendations_for_resume(
        self, 
        resume_text: str, 
        skills: List[str], 
        experience_years: Optional[float],
        preferred_locations: List[str]
    ) -> List[JobRecommendation]:
        """Get job recommendations based on resume analysis"""
        try:
            # This would typically fetch from database
            # For now, return mock recommendations
            mock_jobs = self.get_mock_jobs()
            
            recommendations = []
            for job in mock_jobs:
                score = self.calculate_job_match_score(job, skills, experience_years, preferred_locations)
                if score > 0.3:  # Only recommend jobs with reasonable match
                    rationale = self.generate_match_rationale(job, skills, experience_years, preferred_locations)
                    skills_match = [skill for skill in skills if skill.lower() in job.description.lower()]
                    location_match = any(loc.lower() in job.location.lower() for loc in preferred_locations)
                    
                    recommendation = JobRecommendation(
                        job=job,
                        score=score,
                        rationale=rationale,
                        skills_match=skills_match,
                        location_match=location_match
                    )
                    recommendations.append(recommendation)
            
            # Sort by score (highest first)
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
            return recommendations[:10]  # Return top 10 recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    def calculate_job_match_score(
        self, 
        job: Job, 
        skills: List[str], 
        experience_years: Optional[float],
        preferred_locations: List[str]
    ) -> float:
        """Calculate how well a job matches the resume"""
        score = 0.0
        
        # Skills match (40% weight)
        if skills and job.skills:
            skill_matches = sum(1 for skill in skills if skill.lower() in [s.lower() for s in job.skills])
            skill_score = skill_matches / len(skills) if skills else 0
            score += skill_score * 0.4
        
        # Experience match (30% weight)
        if experience_years and job.experience:
            exp_score = self.calculate_experience_match(experience_years, job.experience)
            score += exp_score * 0.3
        
        # Location match (20% weight)
        if preferred_locations:
            location_score = self.calculate_location_match(job.location, preferred_locations)
            score += location_score * 0.2
        
        # Description match (10% weight)
        if skills and job.description:
            desc_matches = sum(1 for skill in skills if skill.lower() in job.description.lower())
            desc_score = desc_matches / len(skills) if skills else 0
            score += desc_score * 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def calculate_experience_match(self, resume_years: float, job_experience: str) -> float:
        """Calculate experience level match"""
        try:
            # Parse job experience requirements
            if "entry" in job_experience.lower() or "junior" in job_experience.lower():
                job_years = 1.0
            elif "mid" in job_experience.lower() or "intermediate" in job_experience.lower():
                job_years = 3.0
            elif "senior" in job_experience.lower():
                job_years = 7.0
            elif "lead" in job_experience.lower() or "principal" in job_experience.lower():
                job_years = 10.0
            else:
                # Try to extract years from text
                years_match = re.search(r"(\d+)[-+](\d+)?", job_experience)
                if years_match:
                    min_years = float(years_match.group(1))
                    max_years = float(years_match.group(2)) if years_match.group(2) else min_years + 2
                    job_years = (min_years + max_years) / 2
                else:
                    job_years = 5.0  # Default
            
            # Calculate match score
            if resume_years >= job_years:
                return 1.0  # Overqualified is fine
            else:
                # Underqualified - calculate how close
                return max(0.0, 1.0 - (job_years - resume_years) / job_years)
                
        except Exception:
            return 0.5  # Default score if parsing fails
    
    def calculate_location_match(self, job_location: str, preferred_locations: List[str]) -> float:
        """Calculate location match score"""
        job_location_lower = job_location.lower()
        
        # Check for exact matches
        for pref_loc in preferred_locations:
            if pref_loc.lower() in job_location_lower:
                return 1.0
        
        # Check for partial matches
        for pref_loc in preferred_locations:
            if any(word in job_location_lower for word in pref_loc.lower().split()):
                return 0.7
        
        # Check for remote/hybrid preferences
        if "remote" in preferred_locations and "remote" in job_location_lower:
            return 1.0
        if "hybrid" in preferred_locations and "hybrid" in job_location_lower:
            return 0.8
        
        return 0.0
    
    def generate_match_rationale(
        self, 
        job: Job, 
        skills: List[str], 
        experience_years: Optional[float],
        preferred_locations: List[str]
    ) -> str:
        """Generate explanation for why a job matches"""
        reasons = []
        
        # Skills match
        if skills and job.skills:
            matching_skills = [skill for skill in skills if skill.lower() in [s.lower() for s in job.skills]]
            if matching_skills:
                reasons.append(f"Skills match: {', '.join(matching_skills[:3])}")
        
        # Experience match
        if experience_years and job.experience:
            if "senior" in job.experience.lower() and experience_years >= 5:
                reasons.append("Experience level matches senior position")
            elif "entry" in job.experience.lower() and experience_years <= 2:
                reasons.append("Experience level matches entry position")
        
        # Location match
        if preferred_locations:
            for pref_loc in preferred_locations:
                if pref_loc.lower() in job.location.lower():
                    reasons.append(f"Location preference: {pref_loc}")
                    break
        
        # Company size/type
        if "startup" in job.company.lower() and "startup" in [p.lower() for p in preferred_locations]:
            reasons.append("Company type preference: Startup")
        
        if not reasons:
            reasons.append("General fit based on job requirements")
        
        return "; ".join(reasons)
    
    def get_mock_jobs(self) -> List[Job]:
        """Get mock jobs for testing (replace with database query)"""
        from datetime import datetime
        from models.job import JobPlatform
        
        return [
            Job(
                job_id="mock_1",
                title="Senior Software Engineer",
                company="TechCorp Solutions",
                location="Bangalore, Karnataka",
                experience="5-8 years",
                skills=["Python", "React", "AWS", "SQL"],
                description="We are looking for a talented software engineer with Python and React experience",
                posted_date=datetime.utcnow(),
                url="https://example.com/job1",
                platform=JobPlatform.NAUKRI
            ),
            Job(
                job_id="mock_2",
                title="Data Scientist",
                company="DataTech Inc",
                location="Mumbai, Maharashtra",
                experience="3-6 years",
                skills=["Python", "Machine Learning", "SQL", "Statistics"],
                description="Join our data science team to build ML models and analyze data",
                posted_date=datetime.utcnow(),
                url="https://example.com/job2",
                platform=JobPlatform.LINKEDIN
            ),
            Job(
                job_id="mock_3",
                title="Full Stack Developer",
                company="StartupXYZ",
                location="Remote",
                experience="2-5 years",
                skills=["JavaScript", "Node.js", "React", "MongoDB"],
                description="Build scalable web applications using modern technologies",
                posted_date=datetime.utcnow(),
                url="https://example.com/job3",
                platform=JobPlatform.NAUKRI
            )
        ]
    
    async def get_similar_jobs(self, job_id: str, limit: int = 5) -> List[JobRecommendation]:
        """Get similar jobs based on a reference job"""
        try:
            # This would fetch the reference job from database
            # For now, use mock data
            reference_job = self.get_mock_jobs()[0]  # Use first mock job as reference
            
            # Get all jobs and calculate similarity
            all_jobs = self.get_mock_jobs()
            recommendations = []
            
            for job in all_jobs:
                if job.job_id != job_id:
                    similarity_score = self.calculate_job_similarity(reference_job, job)
                    if similarity_score > 0.3:
                        rationale = f"Similar to {reference_job.title} position"
                        recommendation = JobRecommendation(
                            job=job,
                            score=similarity_score,
                            rationale=rationale,
                            skills_match=[],
                            location_match=False
                        )
                        recommendations.append(recommendation)
            
            # Sort by similarity score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting similar jobs: {e}")
            return []
    
    def calculate_job_similarity(self, job1: Job, job2: Job) -> float:
        """Calculate similarity between two jobs"""
        score = 0.0
        
        # Title similarity
        if job1.title.lower() == job2.title.lower():
            score += 0.3
        elif any(word in job2.title.lower() for word in job1.title.lower().split()):
            score += 0.2
        
        # Skills similarity
        if job1.skills and job2.skills:
            common_skills = set(s.lower() for s in job1.skills) & set(s.lower() for s in job2.skills)
            if common_skills:
                score += 0.3 * (len(common_skills) / max(len(job1.skills), len(job2.skills)))
        
        # Experience similarity
        if job1.experience and job2.experience:
            if job1.experience.lower() == job2.experience.lower():
                score += 0.2
            elif any(level in job1.experience.lower() for level in ["senior", "lead"]) and \
                 any(level in job2.experience.lower() for level in ["senior", "lead"]):
                score += 0.15
        
        # Location similarity
        if job1.location.lower() == job2.location.lower():
            score += 0.2
        
        return min(score, 1.0)

