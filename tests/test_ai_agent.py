import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import os

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agent.agent import JobAssistantAgent
from ai_agent.intent_classifier import IntentClassifier
from ai_agent.recommendations import JobRecommender
from models.chat import ChatRequest, ChatResponse, QueryIntent
from models.job import Job, JobRecommendation, ResumeAnalysis


class TestJobAssistantAgent:
    """Test cases for the main AI agent"""
    
    @pytest.fixture
    def mock_openai_key(self):
        """Mock OpenAI API key"""
        return "test_openai_key_12345"
    
    @pytest.fixture
    def mock_agent(self, mock_openai_key):
        """Mock AI agent"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': mock_openai_key}):
            agent = JobAssistantAgent(mock_openai_key)
            return agent
    
    @patch('ai_agent.agent.ChatOpenAI')
    def test_agent_initialization(self, mock_chat_openai, mock_openai_key):
        """Test AI agent initialization"""
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        agent = JobAssistantAgent(mock_openai_key)
        
        assert agent.openai_api_key == mock_openai_key
        assert agent.llm is not None
        assert agent.intent_classifier is not None
        assert agent.job_recommender is not None
    
    def test_agent_initialization_no_key(self):
        """Test agent initialization without API key"""
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            JobAssistantAgent(None)
    
    @patch('ai_agent.agent.ChatOpenAI')
    @patch('ai_agent.intent_classifier.IntentClassifier')
    @patch('ai_agent.recommendations.JobRecommender')
    async def test_query_processing(self, mock_recommender, mock_classifier, mock_chat_openai, mock_agent):
        """Test query processing"""
        # Mock intent classification
        mock_intent = QueryIntent(
            intent="job_search",
            confidence=0.9,
            entities=[],
            parameters={"query": "data scientist", "location": "bangalore"}
        )
        mock_agent.intent_classifier.classify_intent.return_value = mock_intent
        
        # Mock response generation
        mock_agent.handle_job_search = Mock()
        mock_agent.handle_job_search.return_value = "I found 15 data scientist jobs in Bangalore"
        
        # Test query
        response = await mock_agent.query("Show me data scientist jobs in Bangalore")
        
        assert response is not None
        assert response.response == "I found 15 data scientist jobs in Bangalore"
        assert response.confidence == 0.9
        assert response.session_id is not None
    
    async def test_session_management(self, mock_agent):
        """Test chat session management"""
        # Test session creation
        response1 = await mock_agent.query("Hello")
        session_id = response1.session_id
        
        # Test session persistence
        response2 = await mock_agent.query("How are you?", session_id=session_id)
        
        assert response2.session_id == session_id
        assert len(mock_agent.sessions[session_id].messages) == 4  # 2 user + 2 assistant
    
    async def test_error_handling(self, mock_agent):
        """Test error handling in query processing"""
        # Mock intent classification to raise exception
        mock_agent.intent_classifier.classify_intent.side_effect = Exception("Test error")
        
        response = await mock_agent.query("Test query")
        
        assert "error" in response.response.lower()
        assert response.confidence == 0.0


class TestIntentClassifier:
    """Test cases for intent classification"""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM"""
        mock_llm = Mock()
        mock_llm.generate.return_value.generations = [[Mock(text='{"intent": "job_search", "confidence": 0.9}')]]
        return mock_llm
    
    @pytest.fixture
    def classifier(self, mock_llm):
        """Intent classifier instance"""
        return IntentClassifier(mock_llm)
    
    def test_intent_classification_success(self, classifier, mock_llm):
        """Test successful intent classification"""
        intent = classifier.classify_intent("Show me data scientist jobs")
        
        assert intent.intent == "job_search"
        assert intent.confidence == 0.9
    
    def test_intent_classification_fallback(self, classifier):
        """Test fallback to pattern-based classification"""
        # Mock LLM to return invalid JSON
        classifier.llm.generate.return_value.generations = [[Mock(text='invalid json')]]
        
        intent = classifier.classify_intent("Show me data scientist jobs")
        
        assert intent.intent == "job_search"  # Should fallback to pattern-based
        assert intent.confidence == 0.7
    
    def test_pattern_based_classification(self, classifier):
        """Test pattern-based intent classification"""
        # Test job search intent
        intent = classifier.pattern_based_classification("I need a job")
        assert intent.intent == "job_search"
        
        # Test resume analysis intent
        intent = classifier.pattern_based_classification("Analyze my resume")
        assert intent.intent == "resume_analysis"
        
        # Test career advice intent
        intent = classifier.pattern_based_classification("Give me career tips")
        assert intent.intent == "career_advice"
    
    def test_parameter_extraction(self, classifier):
        """Test parameter extraction from queries"""
        intent = classifier.pattern_based_classification("Show me Python jobs in Bangalore with 3 years experience")
        
        assert intent.parameters.get("query") is not None
        assert "bangalore" in intent.parameters.get("location", "").lower()
        assert "3" in intent.parameters.get("experience", "")
        assert "python" in intent.parameters.get("skills", [])
    
    def test_skill_extraction(self, classifier):
        """Test technical skill extraction"""
        intent = classifier.pattern_based_classification("I know Python, React, and AWS")
        
        skills = intent.parameters.get("skills", [])
        assert "Python" in skills
        assert "React" in skills
        assert "AWS" in skills


class TestJobRecommender:
    """Test cases for job recommendations"""
    
    @pytest.fixture
    def recommender(self):
        """Job recommender instance"""
        return JobRecommender()
    
    async def test_resume_analysis(self, recommender):
        """Test resume analysis functionality"""
        resume_text = """
        Software Engineer with 5 years of experience
        Skills: Python, React, AWS, SQL
        Location: Bangalore, willing to relocate to Mumbai
        Prefers: Full-time, Remote work
        """
        
        analysis = await recommender.analyze_resume(resume_text)
        
        assert analysis.skills is not None
        assert len(analysis.skills) > 0
        assert "Python" in analysis.skills
        assert "React" in analysis.skills
        assert analysis.experience_years == 5.0
        assert "Bangalore" in analysis.preferred_locations
        assert "Remote" in analysis.job_preferences
    
    def test_skill_extraction(self, recommender):
        """Test skill extraction from text"""
        text = "I have experience with Python programming, React development, and AWS cloud services"
        
        skills = recommender.extract_skills_from_text(text)
        
        assert "Python" in skills
        assert "React" in skills
        assert "AWS" in skills
    
    def test_experience_extraction(self, recommender):
        """Test experience year extraction"""
        # Test explicit years
        text1 = "I have 7 years of experience in software development"
        years1 = recommender.extract_experience_years(text1)
        assert years1 == 7.0
        
        # Test level indicators
        text2 = "Senior software engineer with lead responsibilities"
        years2 = recommender.extract_experience_years(text2)
        assert years2 == 10.0
    
    def test_location_extraction(self, recommender):
        """Test location preference extraction"""
        text = "Based in Delhi, willing to relocate to Bangalore or Mumbai"
        
        locations = recommender.extract_preferred_locations(text)
        
        assert "Delhi" in locations
        assert "Bangalore" in locations
        assert "Mumbai" in locations
    
    def test_job_preference_extraction(self, recommender):
        """Test job preference extraction"""
        text = "Looking for full-time remote positions in startup companies"
        
        preferences = recommender.extract_job_preferences(text)
        
        assert "Full-time" in preferences
        assert "Remote" in preferences
        assert "Startup" in preferences
    
    async def test_job_recommendations(self, recommender):
        """Test job recommendation generation"""
        resume_text = "Python developer with 3 years experience, based in Bangalore"
        
        analysis = await recommender.analyze_resume(resume_text)
        
        assert analysis.recommendations is not None
        assert len(analysis.recommendations) > 0
        
        # Check recommendation structure
        for rec in analysis.recommendations:
            assert hasattr(rec, 'job')
            assert hasattr(rec, 'score')
            assert hasattr(rec, 'rationale')
            assert 0 <= rec.score <= 1
    
    def test_job_similarity_calculation(self, recommender):
        """Test job similarity calculation"""
        from models.job import Job, JobPlatform
        from datetime import datetime
        
        job1 = Job(
            job_id="test1",
            title="Senior Software Engineer",
            company="TechCorp",
            location="Bangalore",
            experience="5-8 years",
            skills=["Python", "React", "AWS"],
            description="Python developer with React experience",
            posted_date=datetime.utcnow(),
            url="https://example.com/job1",
            platform=JobPlatform.NAUKRI
        )
        
        job2 = Job(
            job_id="test2",
            title="Software Engineer",
            company="DataCorp",
            location="Mumbai",
            experience="3-5 years",
            skills=["Python", "JavaScript", "SQL"],
            description="Python developer with JavaScript experience",
            posted_date=datetime.utcnow(),
            url="https://example.com/job2",
            platform=JobPlatform.LINKEDIN
        )
        
        similarity = recommender.calculate_job_similarity(job1, job2)
        
        assert 0 <= similarity <= 1
        assert similarity > 0  # Should have some similarity due to Python


# Integration tests
@pytest.mark.integration
class TestAIAgentIntegration:
    """Integration tests for AI agent (require OpenAI API)"""
    
    @pytest.mark.skip(reason="Requires OpenAI API key")
    async def test_live_agent_query(self):
        """Test live agent with OpenAI API"""
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            pytest.skip("OpenAI API key not available")
        
        agent = JobAssistantAgent(openai_key)
        response = await agent.query("What is a data scientist?")
        
        assert response is not None
        assert len(response.response) > 0
        assert response.confidence > 0


if __name__ == "__main__":
    pytest.main([__file__])

