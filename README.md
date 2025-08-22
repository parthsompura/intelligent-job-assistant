# 🚀 Intelligent Job Assistant & Recommendation System

An AI-powered job intelligence system that provides intelligent job recommendations, resume analysis, and natural language job search capabilities.

## ✨ Features

- **🤖 AI-Powered Chat Interface**: Natural language job queries and career advice
- **📊 Resume Analysis**: Skills extraction and personalized job matching
- **🔍 Smart Job Search**: Advanced filtering and recommendation algorithms
- **📱 Multiple Interfaces**: REST API, CLI, and web interfaces
- **💾 JSON Storage**: Lightweight, database-free data persistence
- **🔧 Scalable Architecture**: Modular design for easy extension

## 🏗️ System Architecture

```
├── ai_agent/          # LangChain-based AI agent
├── api/              # FastAPI REST endpoints
├── job_scraper/      # Job scraping modules
├── models/           # Pydantic data models
├── utils/            # Utility functions
└── tests/            # Test suite
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd joblo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory:

```bash
# OpenAI API Key (required for AI features)
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the System

#### Web Interface (Recommended)
```bash
python main.py
```
- 🌐 Web server: http://localhost:8000
- 📚 API docs: http://localhost:8000/docs

#### CLI Interface
```bash
python -m ai_agent.cli --interactive
```

#### Single Query
```bash
python -m ai_agent.cli --query "Find remote Python developer jobs"
```

## 📖 Usage Examples

### AI Chat Interface

```python
from ai_agent.agent import JobAssistantAgent

# Initialize agent
agent = JobAssistantAgent()

# Natural language queries
response = await agent.query("Show me remote data scientist jobs in Bangalore")
response = await agent.query("What are the top skills for machine learning engineers?")
response = await agent.query("Find jobs matching my resume")
```

### Resume Analysis

```python
from ai_agent.recommendations import JobRecommender

# Initialize recommender
recommender = JobRecommender()

# Analyze resume
resume_text = """
John Doe
Software Engineer
Skills: Python, React, AWS
Experience: 5 years
"""

analysis = await recommender.analyze_resume(resume_text)
print(f"Skills: {analysis.skills}")
print(f"Experience: {analysis.experience_years} years")
print(f"Recommendations: {len(analysis.recommendations)} jobs")
```

### Job Search API

```bash
# Search jobs
curl -X POST "http://localhost:8000/api/jobs/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python developer",
    "location": "Bangalore",
    "experience": "3-5 years",
    "skills": ["Python", "React"]
  }'

# Chat with AI
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find remote software engineering jobs",
    "user_id": "user123"
  }'

# Analyze resume
curl -X POST "http://localhost:8000/api/analyze-resume" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Your resume text here..."
  }'
```

## 🔧 API Endpoints

### Core Endpoints
- `GET /health` - System health check
- `GET /api/stats` - System statistics
- `GET /api/docs` - Interactive API documentation

### Job Management
- `GET /api/jobs` - List all jobs
- `GET /api/jobs/{job_id}` - Get job details
- `POST /api/jobs/search` - Search jobs with filters

### AI Features
- `POST /api/chat` - Chat with AI agent
- `POST /api/analyze-resume` - Analyze resume and get recommendations

### Scraping (Background Tasks)
- `POST /api/scrape/naukri` - Trigger Naukri job scraping
- `POST /api/scrape/linkedin` - Trigger LinkedIn job scraping

## 📊 Sample Data

### Job Object
```json
{
  "job_id": "naukri_12345",
  "title": "Senior Data Scientist",
  "company": "TechCorp",
  "location": "Bangalore, Karnataka",
  "experience": "5-8 years",
  "skills": ["Python", "Machine Learning", "SQL"],
  "description": "We are looking for a Senior Data Scientist...",
  "posted_date": "2024-01-15T10:00:00Z",
  "url": "https://naukri.com/job/12345",
  "platform": "naukri"
}
```

### AI Response
```
User: "Show me remote data scientist jobs in Bangalore"

AI: I found 15 remote data scientist positions in Bangalore that match your criteria:

1. Senior Data Scientist at TechCorp (Remote)
   - Skills: Python, ML, SQL
   - Experience: 5-8 years
   - Salary: ₹25-35 LPA

2. Lead Data Scientist at DataTech (Hybrid)
   - Skills: Python, Deep Learning, AWS
   - Experience: 8-12 years
   - Salary: ₹35-50 LPA

Would you like me to show more details about any specific position?
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_ai_agent.py
pytest tests/test_recommendations.py
pytest tests/test_api.py
```

## 🔒 Security & Privacy

- **No Sensitive Data**: API keys are stored in environment variables
- **Input Validation**: All inputs are validated using Pydantic models
- **Error Handling**: Graceful error handling without exposing internals
- **Rate Limiting**: Built-in rate limiting for API endpoints

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production Deployment
```bash
# Using Gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Using Docker
docker build -t job-assistant .
docker run -p 8000:8000 job-assistant
```

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

## 📋 Requirements

### System Requirements
- Python 3.8+
- 4GB RAM minimum
- Internet connection for AI features

### Dependencies
- FastAPI - Web framework
- LangChain - AI/LLM framework
- OpenAI - AI model provider
- Selenium - Web scraping
- Pydantic - Data validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🆘 Support

- 📚 [API Documentation](http://localhost:8000/docs)
- 🐛 [Issue Tracker](https://github.com/your-repo/issues)
- 📧 [Email Support](mailto:support@example.com)

---

**🎉 Ready for production use!**

