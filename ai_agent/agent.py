import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from models.job import Job, JobSearchQuery, JobRecommendation
from models.chat import ChatMessage, ChatSession, ChatResponse, QueryIntent, MessageRole

from ai_agent.intent_classifier import IntentClassifier
from ai_agent.recommendations import JobRecommender

logger = logging.getLogger(__name__)


class JobAssistantAgent:
    """Intelligent job assistant agent using LangChain"""
    
    def __init__(self, openai_api_key: str = None, jobs_data: List[Job] = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        # Store jobs data for intelligent search
        self.jobs_data = jobs_data or []
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            temperature=0.7,
            openai_api_key=self.openai_api_key,
            model_name="gpt-4o-mini"  # Using GPT-4o-mini for better performance
        )
        
        # Initialize components
        self.intent_classifier = IntentClassifier(self.llm)
        self.job_recommender = JobRecommender()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # System prompt for the agent
        self.system_prompt = """You are an intelligent job assistant that helps users find jobs, 
        answer job-related questions, and provides personalized recommendations. 
        
        Your capabilities include:
        1. Searching and filtering jobs based on user criteria
        2. Analyzing resumes and matching them to suitable jobs
        3. Providing career advice and job search tips
        4. Explaining job requirements and company information
        5. Recommending similar jobs and career paths
        
        Always be helpful, professional, and provide actionable advice. 
        When recommending jobs, explain why they match the user's criteria.
        """
        
        # Initialize conversation memory
        self.sessions: Dict[str, ChatSession] = {}
        
    def update_jobs_data(self, jobs_data: List[Job]):
        """Update the jobs data that the agent can search through"""
        self.jobs_data = jobs_data
        logger.info(f"Updated agent with {len(jobs_data)} jobs")
        
    async def query(self, message: str, session_id: str = None, user_id: str = None) -> ChatResponse:
        """Process user query and return response"""
        try:
            # Create or get session
            if not session_id:
                session_id = str(uuid.uuid4())
            
            if session_id not in self.sessions:
                self.sessions[session_id] = ChatSession(
                    session_id=session_id,
                    user_id=user_id
                )
            
            session = self.sessions[session_id]
            
            # Add user message to session
            user_message = ChatMessage(
                role=MessageRole.USER,
                content=message
            )
            session.messages.append(user_message)
            
            # Classify intent
            intent = self.intent_classifier.classify_intent(message)
            
            # Generate response based on intent
            response_content = await self.generate_response(message, intent, session)
            
            # Add assistant message to session
            assistant_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=response_content
            )
            session.messages.append(assistant_message)
            session.updated_at = datetime.utcnow()
            
            # Create response
            chat_response = ChatResponse(
                response=response_content,
                session_id=session_id,
                confidence=intent.confidence
            )
            
            return chat_response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return ChatResponse(
                response="I apologize, but I encountered an error processing your request. Please try again.",
                session_id=session_id or "error",
                confidence=0.0
            )
    
    async def generate_response(self, message: str, intent: QueryIntent, session: ChatSession) -> str:
        """Generate response based on detected intent"""
        try:
            if intent.intent == "job_search":
                return await self.handle_job_search(message, intent.parameters)
            
            elif intent.intent == "resume_analysis":
                return await self.handle_resume_analysis(message, intent.parameters)
            
            elif intent.intent == "career_advice":
                return await self.handle_career_advice(message, intent.parameters)
            
            elif intent.intent == "job_details":
                return await self.handle_job_details(message, intent.parameters)
            
            elif intent.intent == "similar_jobs":
                return await self.handle_similar_jobs(message, intent.parameters)
            
            elif intent.intent == "general_question":
                return await self.handle_general_question(message, intent.parameters)
            
            else:
                return await self.handle_general_question(message, intent.parameters)
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error. Please try rephrasing your question."
    
    async def handle_job_search(self, message: str, parameters: Dict[str, Any]) -> str:
        """Handle job search queries using LLM to analyze available jobs"""
        try:
            # Extract search parameters
            query = parameters.get("query", "")
            location = parameters.get("location", "")
            experience = parameters.get("experience", "")
            skills = parameters.get("skills", [])
            
            if not self.jobs_data:
                return "I apologize, but I don't have access to job data at the moment. Please try again later."
            
            # Create a comprehensive prompt for the LLM to analyze jobs
            job_search_prompt = PromptTemplate(
                input_variables=["user_query", "search_params", "available_jobs"],
                template="""You are an expert job search assistant. Analyze the available jobs and provide intelligent recommendations based on the user's query.

User Query: {user_query}
Search Parameters: {search_params}

Available Jobs:
{available_jobs}

Based on the user's query and the available jobs, please:

1. **Find the most relevant jobs** (up to 5 best matches) that align with the user's criteria
2. **Explain why each job is a good match** - mention specific skills, location, experience, or other factors
3. **Provide a summary** of what you found and how many jobs match their criteria
4. **Suggest refinements** if the search could be improved (e.g., different skills, locations, or experience levels)

Format your response in a clear, helpful manner:
- Use bullet points for job listings
- Include job title, company, location, and key matching criteria
- Explain the match reasoning clearly
- Be encouraging and actionable

Response:"""
            )
            
            # Prepare search parameters for display
            search_params = []
            if query:
                search_params.append(f"Query: {query}")
            if location:
                search_params.append(f"Location: {location}")
            if experience:
                search_params.append(f"Experience: {experience}")
            if skills:
                search_params.append(f"Skills: {', '.join(skills)}")
            
            search_params_str = "\n".join(search_params) if search_params else "No specific filters"
            
            # Format available jobs for the prompt
            formatted_jobs = []
            for i, job in enumerate(self.jobs_data[:50], 1):  # Limit to first 50 for prompt efficiency
                job_info = f"{i}. {job.title} at {job.company}"
                job_info += f"\n   Location: {job.location}"
                if job.experience:
                    job_info += f"\n   Experience: {job.experience}"
                if job.skills:
                    job_info += f"\n   Skills: {', '.join(job.skills[:5])}"
                if job.salary:
                    job_info += f"\n   Salary: {job.salary}"
                if job.remote_work:
                    job_info += f"\n   Remote: {'Yes' if job.remote_work else 'No'}"
                formatted_jobs.append(job_info)
            
            available_jobs_str = "\n\n".join(formatted_jobs)
            
            # Use LLM to generate intelligent response
            chain = LLMChain(llm=self.llm, prompt=job_search_prompt)
            response = await chain.arun(
                user_query=message,
                search_params=search_params_str,
                available_jobs=available_jobs_str
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling job search: {e}")
            return "I encountered an error while searching for jobs. Please try again."
    
    async def handle_resume_analysis(self, message: str, parameters: Dict[str, Any]) -> str:
        """Handle resume analysis requests using LLM for intelligent insights"""
        try:
            resume_text = parameters.get("resume_text", "")
            
            if not resume_text:
                return "I'd be happy to analyze your resume! Please share your resume text or upload it, and I'll help you find matching job opportunities."
            
            # Analyze resume and get recommendations
            analysis = await self.job_recommender.analyze_resume(resume_text)
            
            # Use LLM to generate intelligent resume analysis response
            resume_analysis_prompt = PromptTemplate(
                input_variables=["resume_text", "analysis_results", "user_query"],
                template="""You are an expert career consultant and resume analyst. Provide intelligent insights and recommendations based on the resume analysis.

User Query: {user_query}

Resume Text: {resume_text}

Analysis Results:
- Skills Identified: {skills}
- Experience Level: {experience} years
- Preferred Locations: {locations}
- Job Recommendations: {recommendations}

Please provide:
1. **Resume Analysis Summary** - Key strengths and areas for improvement
2. **Skills Assessment** - How the identified skills align with market demands
3. **Career Insights** - What the experience level suggests about career stage
4. **Job Recommendations** - Analysis of the top job matches with reasoning
5. **Actionable Advice** - Specific steps to improve employability and job search
6. **Next Steps** - How to proceed with applications and career development

Format your response professionally with clear sections and actionable insights.

Response:"""
            )
            
            # Format analysis results for the prompt
            skills_str = ", ".join(analysis.skills[:10]) if analysis.skills else "None identified"
            experience_str = f"{analysis.experience_years}" if analysis.experience_years else "Not specified"
            locations_str = ", ".join(analysis.preferred_locations) if analysis.preferred_locations else "Not specified"
            
            # Format recommendations
            recs_str = ""
            if analysis.recommendations:
                for i, rec in enumerate(analysis.recommendations[:3], 1):
                    recs_str += f"{i}. {rec.job.title} at {rec.job.company} (Score: {rec.score:.2f})\n"
            else:
                recs_str = "No specific recommendations available"
            
            # Use LLM to generate intelligent response
            chain = LLMChain(llm=self.llm, prompt=resume_analysis_prompt)
            response = await chain.arun(
                resume_text=resume_text[:500],  # Limit resume text for prompt efficiency
                skills=skills_str,
                experience=experience_str,
                locations=locations_str,
                recommendations=recs_str,
                user_query=message
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling resume analysis: {e}")
            return "I encountered an error while analyzing your resume. Please try again."
    
    async def handle_career_advice(self, message: str, parameters: Dict[str, Any]) -> str:
        """Handle career advice requests"""
        try:
            topic = parameters.get("topic", "general")
            
            advice_prompt = PromptTemplate(
                input_variables=["topic", "question"],
                template="Provide helpful career advice about {topic}. Answer this question: {question}"
            )
            
            chain = LLMChain(llm=self.llm, prompt=advice_prompt)
            response = await chain.arun(topic=topic, question=message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling career advice: {e}")
            return "I'd be happy to provide career advice! Please let me know what specific career guidance you're looking for."
    
    async def handle_job_details(self, message: str, parameters: Dict[str, Any]) -> str:
        """Handle job details requests using LLM and real job data"""
        try:
            job_id = parameters.get("job_id", "")
            company = parameters.get("company", "")
            
            if not job_id and not company:
                return "I'd be happy to provide job details! Please specify which job or company you'd like to know more about."
            
            # Search for jobs matching the criteria
            matching_jobs = []
            if company:
                # Search by company name
                for job in self.jobs_data:
                    if company.lower() in job.company.lower():
                        matching_jobs.append(job)
            elif job_id:
                # Search by job ID
                for job in self.jobs_data:
                    if job_id.lower() in job.job_id.lower():
                        matching_jobs.append(job)
            
            if not matching_jobs:
                return f"I couldn't find any jobs matching '{company or job_id}'. Please check the company name or job ID and try again."
            
            # Use LLM to generate detailed response about the job(s)
            job_details_prompt = PromptTemplate(
                input_variables=["user_query", "matching_jobs"],
                template="""You are an expert job consultant. Provide detailed information about the requested job(s) based on the user's query.

User Query: {user_query}

Matching Jobs:
{matching_jobs}

Please provide:
1. **Detailed job information** for each matching job
2. **Key requirements** and qualifications
3. **Company insights** and what makes this opportunity special
4. **Next steps** for the user (how to apply, what to prepare, etc.)

Format your response professionally with clear sections and actionable advice.

Response:"""
            )
            
            # Format jobs for the prompt
            formatted_jobs = []
            for i, job in enumerate(matching_jobs, 1):
                job_info = f"{i}. {job.title} at {job.company}\n"
                job_info += f"   Location: {job.location}\n"
                if job.experience:
                    job_info += f"   Experience: {job.experience}\n"
                if job.skills:
                    job_info += f"   Skills: {', '.join(job.skills[:5])}\n"
                if job.salary:
                    job_info += f"   Salary: {job.salary}\n"
                if job.remote_work:
                    job_info += f"   Remote: {'Yes' if job.remote_work else 'No'}\n"
                if job.description:
                    job_info += f"   Description: {job.description[:200]}...\n"
                formatted_jobs.append(job_info)
            
            available_jobs_str = "\n\n".join(formatted_jobs)
            
            # Use LLM to generate intelligent response
            chain = LLMChain(llm=self.llm, prompt=job_details_prompt)
            response = await chain.arun(
                user_query=message,
                matching_jobs=available_jobs_str
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling job details: {e}")
            return "I encountered an error while fetching job details. Please try again."
    
    async def handle_similar_jobs(self, message: str, parameters: Dict[str, Any]) -> str:
        """Handle similar jobs requests using LLM and real job data"""
        try:
            job_id = parameters.get("job_id", "")
            
            if not job_id:
                return "I'd be happy to find similar jobs! Please specify which job you'd like me to find matches for."
            
            # Find the reference job
            reference_job = None
            for job in self.jobs_data:
                if job_id.lower() in job.job_id.lower():
                    reference_job = job
                    break
            
            if not reference_job:
                return f"I couldn't find a job with ID '{job_id}'. Please check the job ID and try again."
            
            # Find similar jobs based on skills, location, experience
            similar_jobs = []
            reference_skills = set(skill.lower() for skill in reference_job.skills)
            
            for job in self.jobs_data:
                if job.job_id == reference_job.job_id:
                    continue  # Skip the same job
                
                # Calculate similarity score
                job_skills = set(skill.lower() for skill in job.skills)
                skill_overlap = len(reference_skills.intersection(job_skills))
                location_match = reference_job.location.lower() in job.location.lower() or job.location.lower() in reference_job.location.lower()
                
                # Add jobs with some similarity
                if skill_overlap > 0 or location_match:
                    similar_jobs.append((job, skill_overlap, location_match))
            
            # Sort by similarity (skills overlap first, then location)
            similar_jobs.sort(key=lambda x: (x[1], x[2]), reverse=True)
            similar_jobs = similar_jobs[:5]  # Top 5 similar jobs
            
            if not similar_jobs:
                return f"I couldn't find any similar jobs to '{reference_job.title}'. This might be a unique position or we may need to expand our search criteria."
            
            # Use LLM to generate intelligent response about similar jobs
            similar_jobs_prompt = PromptTemplate(
                input_variables=["reference_job", "similar_jobs", "user_query"],
                template="""You are an expert job consultant. Analyze the reference job and find similar opportunities, then provide intelligent recommendations.

User Query: {user_query}

Reference Job:
{reference_job}

Similar Jobs Found:
{similar_jobs}

Please provide:
1. **Analysis of the reference job** - what makes it unique
2. **Similar job opportunities** with clear reasoning for each match
3. **Comparison insights** - how similar jobs differ from the reference
4. **Strategic advice** - which similar jobs might be better fits and why
5. **Next steps** for the user

Format your response professionally with clear sections and actionable insights.

Response:"""
            )
            
            # Format reference job
            ref_job_info = f"Title: {reference_job.title}\n"
            ref_job_info += f"Company: {reference_job.company}\n"
            ref_job_info += f"Location: {reference_job.location}\n"
            if reference_job.experience:
                ref_job_info += f"Experience: {reference_job.experience}\n"
            if reference_job.skills:
                ref_job_info += f"Skills: {', '.join(reference_job.skills)}\n"
            if reference_job.salary:
                ref_job_info += f"Salary: {reference_job.salary}\n"
            
            # Format similar jobs
            similar_jobs_info = []
            for job, skill_overlap, location_match in similar_jobs:
                job_info = f"- {job.title} at {job.company}\n"
                job_info += f"  Location: {job.location}\n"
                if job.skills:
                    job_info += f"  Skills: {', '.join(job.skills[:5])}\n"
                if job.salary:
                    job_info += f"  Salary: {job.salary}\n"
                job_info += f"  Similarity: {skill_overlap} matching skills, Location match: {'Yes' if location_match else 'No'}\n"
                similar_jobs_info.append(job_info)
            
            similar_jobs_str = "\n".join(similar_jobs_info)
            
            # Use LLM to generate intelligent response
            chain = LLMChain(llm=self.llm, prompt=similar_jobs_prompt)
            response = await chain.arun(
                reference_job=ref_job_info,
                similar_jobs=similar_jobs_str,
                user_query=message
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling similar jobs: {e}")
            return "I encountered an error while finding similar jobs. Please try again."
    
    async def handle_general_question(self, message: str, parameters: Dict[str, Any]) -> str:
        """Handle general questions"""
        try:
            # Use LangChain to generate response
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=message)
            ]
            
            response = await self.llm.agenerate([messages])
            return response.generations[0][0].text
            
        except Exception as e:
            logger.error(f"Error handling general question: {e}")
            return "I'd be happy to help! Please let me know what job-related questions you have."
    
    def get_session_history(self, session_id: str) -> List[ChatMessage]:
        """Get chat history for a session"""
        if session_id in self.sessions:
            return self.sessions[session_id].messages
        return []
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a chat session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

