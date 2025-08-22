import logging
from typing import Dict, Any, List
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from models.chat import QueryIntent

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classify user intent from natural language queries"""
    
    def __init__(self, llm):
        self.llm = llm
        
        # Intent classification prompt
        self.intent_prompt = PromptTemplate(
            input_variables=["user_message"],
            template="""Analyze the following user message and classify the intent. 
            Choose from these categories:
            
            1. job_search - User wants to find jobs (e.g., "show me data scientist jobs", "find remote jobs")
            2. resume_analysis - User wants resume analysis (e.g., "analyze my resume", "match my skills to jobs")
            3. career_advice - User wants career guidance (e.g., "how to prepare for interviews", "career tips")
            4. job_details - User wants specific job information (e.g., "tell me about this job", "company details")
            5. similar_jobs - User wants similar job recommendations (e.g., "show similar jobs", "jobs like this")
            6. general_question - General job-related questions (e.g., "what is a data scientist", "job market trends")
            
            User message: {user_message}
            
            Respond in this exact JSON format:
            {{
                "intent": "intent_category",
                "confidence": 0.95,
                "entities": [
                    {{"type": "entity_type", "value": "entity_value"}}
                ],
                "parameters": {{
                    "query": "extracted_query",
                    "location": "extracted_location",
                    "experience": "extracted_experience",
                    "skills": ["skill1", "skill2"],
                    "job_id": "extracted_job_id",
                    "company": "extracted_company",
                    "topic": "extracted_topic",
                    "resume_text": "extracted_resume_text"
                }}
            }}
            
            Extract relevant information and set confidence based on how clear the intent is.
            """
        )
        
        # Entity extraction patterns
        self.entity_patterns = {
            "location": [
                r"in\s+([A-Za-z\s,]+)",
                r"at\s+([A-Za-z\s,]+)",
                r"([A-Za-z\s,]+)\s+area",
                r"remote",
                r"hybrid"
            ],
            "experience": [
                r"(\d+[-+]\d+)\s+years?",
                r"(\d+)\s+years?",
                r"entry\s+level",
                r"senior",
                r"junior",
                r"lead"
            ],
            "skills": [
                r"python",
                r"java",
                r"javascript",
                r"react",
                r"angular",
                r"vue",
                r"node\.js",
                r"sql",
                r"mongodb",
                r"aws",
                r"azure",
                r"docker",
                r"kubernetes",
                r"git",
                r"machine\s+learning",
                r"ai",
                r"data\s+science",
                r"devops",
                r"agile"
            ]
        }
    
    def classify_intent(self, message: str) -> QueryIntent:
        """Classify the intent of a user message"""
        try:
            # Use LangChain to classify intent
            messages = [
                SystemMessage(content="You are an intent classification expert. Respond only with valid JSON."),
                HumanMessage(content=self.intent_prompt.format(user_message=message))
            ]
            
            response = self.llm.generate([messages])
            response_text = response.generations[0][0].text
            
            # Parse JSON response
            import json
            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback to pattern-based classification
                logger.warning("Failed to parse LLM response, using pattern-based classification")
                return self.pattern_based_classification(message)
            
            # Extract intent information
            intent = parsed_response.get("intent", "general_question")
            confidence = parsed_response.get("confidence", 0.8)
            entities = parsed_response.get("entities", [])
            parameters = parsed_response.get("parameters", {})
            
            # Validate and clean parameters
            parameters = self.clean_parameters(parameters)
            
            # Create QueryIntent object
            query_intent = QueryIntent(
                intent=intent,
                confidence=confidence,
                entities=entities,
                parameters=parameters
            )
            
            logger.debug(f"Classified intent: {intent} with confidence: {confidence}")
            return query_intent
            
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            # Fallback to pattern-based classification
            return self.pattern_based_classification(message)
    
    def pattern_based_classification(self, message: str) -> QueryIntent:
        """Fallback pattern-based intent classification"""
        message_lower = message.lower()
        
        # Simple keyword-based classification
        if any(word in message_lower for word in ["job", "position", "opening", "vacancy", "hire", "recruit"]):
            intent = "job_search"
            confidence = 0.7
        elif any(word in message_lower for word in ["resume", "cv", "profile", "skills", "experience"]):
            intent = "resume_analysis"
            confidence = 0.7
        elif any(word in message_lower for word in ["advice", "tip", "help", "guide", "how to"]):
            intent = "career_advice"
            confidence = 0.7
        elif any(word in message_lower for word in ["detail", "information", "about", "company"]):
            intent = "job_details"
            confidence = 0.6
        elif any(word in message_lower for word in ["similar", "like", "same", "related"]):
            intent = "similar_jobs"
            confidence = 0.6
        else:
            intent = "general_question"
            confidence = 0.5
        
        # Extract basic parameters
        parameters = self.extract_basic_parameters(message)
        
        return QueryIntent(
            intent=intent,
            confidence=confidence,
            entities=[],
            parameters=parameters
        )
    
    def extract_basic_parameters(self, message: str) -> Dict[str, Any]:
        """Extract basic parameters using regex patterns"""
        import re
        
        parameters = {}
        message_lower = message.lower()
        
        # Extract location
        for pattern in self.entity_patterns["location"]:
            match = re.search(pattern, message_lower)
            if match:
                parameters["location"] = match.group(1).strip() if match.groups() else "remote"
                break
        
        # Extract experience
        for pattern in self.entity_patterns["experience"]:
            match = re.search(pattern, message_lower)
            if match:
                parameters["experience"] = match.group(1).strip() if match.groups() else match.group(0)
                break
        
        # Extract skills
        skills = []
        for skill in self.entity_patterns["skills"]:
            if skill in message_lower:
                skills.append(skill.replace("\\s+", " ").title())
        if skills:
            parameters["skills"] = skills
        
        # Extract general query
        # Remove common words and extract the main query
        common_words = ["show", "find", "get", "me", "jobs", "for", "in", "at", "with", "experience"]
        words = message.split()
        query_words = [word for word in words if word.lower() not in common_words]
        if query_words:
            parameters["query"] = " ".join(query_words[:5])  # Limit to first 5 words
        
        return parameters
    
    def clean_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate extracted parameters"""
        cleaned = {}
        
        # Clean query
        if "query" in parameters and parameters["query"]:
            cleaned["query"] = str(parameters["query"]).strip()
        
        # Clean location
        if "location" in parameters and parameters["location"]:
            cleaned["location"] = str(parameters["location"]).strip()
        
        # Clean experience
        if "experience" in parameters and parameters["experience"]:
            cleaned["experience"] = str(parameters["experience"]).strip()
        
        # Clean skills
        if "skills" in parameters and parameters["skills"]:
            if isinstance(parameters["skills"], list):
                cleaned["skills"] = [str(skill).strip() for skill in parameters["skills"] if skill]
            else:
                cleaned["skills"] = [str(parameters["skills"]).strip()]
        
        # Clean job_id
        if "job_id" in parameters and parameters["job_id"]:
            cleaned["job_id"] = str(parameters["job_id"]).strip()
        
        # Clean company
        if "company" in parameters and parameters["company"]:
            cleaned["company"] = str(parameters["company"]).strip()
        
        # Clean topic
        if "topic" in parameters and parameters["topic"]:
            cleaned["topic"] = str(parameters["topic"]).strip()
        
        # Clean resume_text
        if "resume_text" in parameters and parameters["resume_text"]:
            cleaned["resume_text"] = str(parameters["resume_text"]).strip()
        
        return cleaned
    
    def get_intent_examples(self) -> Dict[str, List[str]]:
        """Get example queries for each intent"""
        return {
            "job_search": [
                "Show me data scientist jobs",
                "Find remote software engineer positions",
                "I'm looking for Python developer jobs in Bangalore",
                "Get me entry level jobs"
            ],
            "resume_analysis": [
                "Analyze my resume",
                "Match my skills to available jobs",
                "What jobs fit my profile?",
                "Review my CV and suggest jobs"
            ],
            "career_advice": [
                "How to prepare for technical interviews?",
                "Career tips for software engineers",
                "Advice on switching careers to tech",
                "How to negotiate salary?"
            ],
            "job_details": [
                "Tell me about this job posting",
                "What does this company do?",
                "Job requirements for this position",
                "Company culture and benefits"
            ],
            "similar_jobs": [
                "Show me similar jobs",
                "Find jobs like this one",
                "Related positions",
                "Other opportunities like this"
            ],
            "general_question": [
                "What is a data scientist?",
                "Job market trends in tech",
                "Difference between frontend and backend",
                "How to start a career in AI?"
            ]
        }

