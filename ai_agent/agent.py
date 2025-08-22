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
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
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
        """Handle job search queries"""
        try:
            # Extract search parameters
            query = parameters.get("query", "")
            location = parameters.get("location", "")
            experience = parameters.get("experience", "")
            skills = parameters.get("skills", [])
            
            # Create search query
            search_query = JobSearchQuery(
                query=query,
                location=location,
                experience=experience,
                skills=skills,
                limit=10
            )
            
            # Search for jobs (this would require database connection)
            # For now, return a template response
            response = f"I'll help you find jobs for '{query}'"
            if location:
                response += f" in {location}"
            if experience:
                response += f" with {experience} experience"
            if skills:
                response += f" requiring skills like {', '.join(skills)}"
            
            response += ".\n\n"
            response += "Here are some matching job opportunities:\n"
            response += "1. Senior Software Engineer at TechCorp (Bangalore)\n"
            response += "2. Full Stack Developer at StartupXYZ (Remote)\n"
            response += "3. Data Scientist at BigTech Inc (Mumbai)\n\n"
            response += "Would you like me to show more details about any specific position or refine your search?"
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling job search: {e}")
            return "I encountered an error while searching for jobs. Please try again."
    
    async def handle_resume_analysis(self, message: str, parameters: Dict[str, Any]) -> str:
        """Handle resume analysis requests"""
        try:
            resume_text = parameters.get("resume_text", "")
            
            if not resume_text:
                return "I'd be happy to analyze your resume! Please share your resume text or upload it, and I'll help you find matching job opportunities."
            
            # Analyze resume and get recommendations
            analysis = await self.job_recommender.analyze_resume(resume_text)
            
            response = "Based on your resume analysis, here are my findings:\n\n"
            response += f"**Skills identified:** {', '.join(analysis.skills[:5])}\n"
            if analysis.experience_years:
                response += f"**Experience level:** {analysis.experience_years} years\n"
            if analysis.preferred_locations:
                response += f"**Preferred locations:** {', '.join(analysis.preferred_locations)}\n\n"
            
            response += "**Top Job Recommendations:**\n"
            for i, rec in enumerate(analysis.recommendations[:3], 1):
                response += f"{i}. {rec.job.title} at {rec.job.company}\n"
                response += f"   Score: {rec.score:.2f} - {rec.rationale}\n\n"
            
            response += "Would you like me to show more recommendations or help you refine your job search?"
            
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
        """Handle job details requests"""
        try:
            job_id = parameters.get("job_id", "")
            company = parameters.get("company", "")
            
            if not job_id and not company:
                return "I'd be happy to provide job details! Please specify which job or company you'd like to know more about."
            
            # This would typically fetch from database
            response = "Here are the details for the job you requested:\n\n"
            response += "**Job Title:** Senior Software Engineer\n"
            response += "**Company:** TechCorp Solutions\n"
            response += "**Location:** Bangalore, Karnataka\n"
            response += "**Experience:** 5-8 years\n"
            response += "**Skills Required:** Python, React, AWS, SQL\n"
            response += "**Job Type:** Full-time\n"
            response += "**Remote Work:** Hybrid\n\n"
            response += "**Description:** We are looking for a talented software engineer...\n\n"
            response += "Would you like me to show similar jobs or help you apply?"
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling job details: {e}")
            return "I encountered an error while fetching job details. Please try again."
    
    async def handle_similar_jobs(self, message: str, parameters: Dict[str, Any]) -> str:
        """Handle similar jobs requests"""
        try:
            job_id = parameters.get("job_id", "")
            
            if not job_id:
                return "I'd be happy to find similar jobs! Please specify which job you'd like me to find matches for."
            
            # This would typically fetch from database
            response = "Here are some similar jobs that might interest you:\n\n"
            response += "1. **Senior Full Stack Developer** at DataTech Inc\n"
            response += "   - Similar skills: Python, React, AWS\n"
            response += "   - Location: Mumbai\n\n"
            response += "2. **Software Engineer** at CloudCorp\n"
            response += "   - Similar skills: Python, JavaScript, Cloud\n"
            response += "   - Location: Delhi\n\n"
            response += "3. **Backend Developer** at StartupXYZ\n"
            response += "   - Similar skills: Python, SQL, APIs\n"
            response += "   - Location: Remote\n\n"
            
            response += "These jobs have similar skill requirements and experience levels. Would you like more details about any of them?"
            
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

