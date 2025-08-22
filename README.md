# 🚀 Intelligent Job Assistant & Recommendation System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.0.350-orange.svg)](https://langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5--turbo-purple.svg)](https://openai.com/)

An AI-powered job intelligence system that provides intelligent job recommendations, resume analysis, and natural language job search capabilities.

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ System Architecture](#️-system-architecture)
- [🚀 Quick Start](#-quick-start)
- [🌟 Real-World Usage Examples](#-real-world-usage-examples)
- [🔧 API Endpoints](#-api-endpoints)
- [📊 Sample Data](#-sample-data)
- [🧪 Testing](#-testing)
- [🔒 Security & Privacy](#-security--privacy)
- [🚀 Deployment](#-deployment)
- [📋 Requirements](#-requirements)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [🆘 Support](#-support)

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

## 🌟 Real-World Usage Examples

### 🎯 Scenario 1: Job Seeker Looking for Remote Opportunities

**User Query**: "I'm a Python developer with 3 years of experience. I want remote jobs in Bangalore with salary above 15 LPA."

**AI Response**:
```
I found 8 remote Python developer positions in Bangalore matching your criteria:

1. Senior Python Developer at TechCorp (Remote)
   - Experience: 3-5 years ✅
   - Skills: Python, Django, React, AWS
   - Salary: ₹18-25 LPA ✅
   - Location: Bangalore (Remote) ✅

2. Full Stack Developer at StartupXYZ (Remote)
   - Experience: 2-4 years ✅
   - Skills: Python, FastAPI, Vue.js, PostgreSQL
   - Salary: ₹16-22 LPA ✅
   - Location: Bangalore (Remote) ✅

Would you like me to analyze your resume to find the best matches?
```

### 🎯 Scenario 2: Career Change Advice

**User Query**: "I'm a mechanical engineer with 5 years of experience. I want to switch to data science. What skills should I learn?"

**AI Response**:
```
Great career transition! Here's a structured learning path for your mechanical engineering background:

**Phase 1: Foundation (2-3 months)**
- Python Programming (pandas, numpy)
- Statistics & Mathematics
- SQL & Database fundamentals

**Phase 2: Core ML (3-4 months)**
- Machine Learning algorithms
- Scikit-learn, TensorFlow
- Data visualization (matplotlib, seaborn)

**Phase 3: Specialization (2-3 months)**
- Deep Learning (if interested in AI)
- Big Data tools (Spark, Hadoop)
- Cloud platforms (AWS, GCP)

**Recommended Learning Resources:**
- Coursera: Machine Learning by Andrew Ng
- Kaggle: Practice with real datasets
- Books: "Hands-On Machine Learning"

**Expected Timeline**: 7-10 months to become job-ready
**Salary Range**: ₹8-15 LPA for entry-level data scientist roles
```

### 🎯 Scenario 3: Resume Analysis & Job Matching

**Resume Input**:
```
John Doe
Software Engineer
Skills: Python, React, Node.js, AWS, Docker
Experience: 4 years
Projects: E-commerce platform, ML recommendation system
```

**AI Analysis Results**:
```
📊 Resume Analysis Complete!

**Skills Identified**: 15 skills found
- Programming: Python, JavaScript, TypeScript
- Frontend: React, HTML, CSS, Bootstrap
- Backend: Node.js, Express, FastAPI
- DevOps: AWS, Docker, Git, CI/CD
- Database: MongoDB, PostgreSQL, Redis

**Experience Level**: Mid-level (4 years)
**Recommended Roles**: 
- Full Stack Developer
- Backend Engineer
- DevOps Engineer
- Software Engineer

**Top 5 Job Matches**:
1. Senior Full Stack Developer at TechCorp (95% match)
2. Backend Engineer at StartupXYZ (92% match)
3. DevOps Engineer at CloudTech (89% match)
4. Software Engineer at FinTech (87% match)
5. Full Stack Developer at E-commerce (85% match)

**Skills Gap Analysis**:
- Strong: Python, React, AWS
- Improve: Kubernetes, Microservices, System Design
- Learn: GraphQL, Elasticsearch, Redis
```

### 🎯 Scenario 4: Company Research & Interview Prep

**User Query**: "I have an interview at Google for a software engineer role. What should I prepare?"

**AI Response**:
```
Congratulations on the Google interview! Here's your comprehensive preparation guide:

**Technical Preparation (Priority 1)**
- Data Structures & Algorithms (LeetCode Medium/Hard)
- System Design concepts
- Coding in Google Docs (no IDE)
- Time complexity analysis

**Specific Topics to Master**:
- Arrays, Strings, Linked Lists, Trees, Graphs
- Dynamic Programming, Greedy algorithms
- Hash tables, Heaps, Stacks, Queues
- Recursion, Backtracking, Divide & Conquer

**System Design Questions**:
- Design URL shortener
- Design chat application
- Design recommendation system
- Design distributed cache

**Behavioral Questions**:
- Leadership challenges
- Conflict resolution
- Technical decisions
- Project failures & learnings

**Interview Format**:
- 2-3 coding rounds (45 mins each)
- 1 system design round (45 mins)
- 1 behavioral round (45 mins)
- 1 hiring committee review

**Resources**:
- LeetCode: 200+ medium/hard problems
- System Design Primer (GitHub)
- Cracking the Coding Interview book
- Google's coding style guide

**Success Rate**: 15-20% of candidates get offers
**Preparation Time**: 3-6 months recommended
```

### 🎯 Scenario 5: Salary Negotiation

**User Query**: "I got an offer for ₹25 LPA but I want ₹35 LPA. How do I negotiate?"

**AI Response**:
```
Smart negotiation strategy! Here's how to approach this:

**Market Research**:
- Your experience level: 5 years
- Market rate for your role: ₹28-40 LPA
- Your target: ₹35 LPA (within market range) ✅

**Negotiation Strategy**:

**Phase 1: Research & Preparation**
- Research company's salary bands
- Prepare your achievements & impact
- Have competing offers if possible
- Know your BATNA (Best Alternative)

**Phase 2: The Conversation**
- "I'm excited about the role, but I was expecting ₹35 LPA based on my experience and market rates"
- Highlight specific achievements: "I led a team of 5 developers and delivered 3 major projects"
- Show market data: "Similar roles in Bangalore are offering ₹30-40 LPA"

**Phase 3: Compromise Options**
- Base salary: ₹32 LPA
- Performance bonus: ₹3 LPA
- Stock options: Additional ₹2-3 LPA
- Signing bonus: ₹1-2 LPA

**Key Phrases to Use**:
- "I'm confident I can deliver exceptional value"
- "This role aligns with my career goals"
- "I'm excited about the company's mission"
- "I believe my experience justifies this compensation"

**Timing**: Negotiate after offer, before acceptance
**Confidence Level**: High (your target is reasonable)
**Expected Outcome**: ₹30-35 LPA final offer
```

## 📖 Technical Usage Examples

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**MIT License Benefits:**
- ✅ **Open Source**: Free to use, modify, and distribute
- ✅ **Commercial Use**: Can be used in commercial projects
- ✅ **Attribution**: Requires only copyright notice
- ✅ **No Warranty**: Clear liability protection
- ✅ **Industry Standard**: Widely adopted by major projects

**Copyright © 2025 Parth Pathak**

## 🆘 Support

- 📚 [API Documentation](http://localhost:8000/docs)
- 🐛 [Issue Tracker](https://github.com/your-repo/issues)
- 📧 [Email Support](mailto:support@example.com)

---

**🎉 Ready for production use!**

