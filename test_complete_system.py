#!/usr/bin/env python3
"""
Comprehensive End-to-End Test for Intelligent Job Assistant System
Tests all components with real data: API, CLI, AI Agent, Job Recommendations, Resume Analysis
"""

import asyncio
import requests
import json
import time
import subprocess
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SystemTester:
    """Comprehensive system tester"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        # Print result
        emoji = "PASS" if status == "PASS" else "FAIL"
        print(f"{emoji} {test_name}: {status}")
        if details:
            print(f"   {details}")
        print()
    
    def test_system_health(self):
        """Test system health and basic connectivity"""
        print("Testing System Health...")
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("System Health", "PASS", "Health endpoint responding")
            else:
                self.log_test("System Health", "FAIL", f"Health endpoint returned {response.status_code}")
                return False
                
            # Test stats endpoint
            response = requests.get(f"{self.base_url}/api/stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                self.log_test("System Stats", "PASS", f"AI Agent: {stats.get('ai_agent', 'unknown')}, Storage: {stats.get('storage', 'unknown')}")
            else:
                self.log_test("System Stats", "FAIL", f"Stats endpoint returned {response.status_code}")
                
            return True
            
        except requests.exceptions.ConnectionError:
            self.log_test("System Health", "FAIL", "Cannot connect to server. Is it running?")
            return False
        except Exception as e:
            self.log_test("System Health", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_ai_chat_api(self):
        """Test AI chat functionality via API"""
        print("Testing AI Chat API...")
        
        test_queries = [
            {
                "name": "Job Search Query",
                "message": "I'm a Python developer with 4 years of experience looking for remote opportunities in Bangalore",
                "expected_intent": "job_search"
            },
            {
                "name": "Career Advice Query", 
                "message": "What are the top skills for data scientists in 2024?",
                "expected_intent": "career_advice"
            },
            {
                "name": "Resume Analysis Query",
                "message": "Can you analyze my resume and suggest jobs?",
                "expected_intent": "resume_analysis"
            }
        ]
        
        for query in test_queries:
            try:
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "message": query["message"],
                        "user_id": f"test_user_{query['name'].lower().replace(' ', '_')}"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    confidence = result.get('confidence', 0)
                    
                    if confidence > 0.7:
                        self.log_test(
                            f"AI Chat - {query['name']}", 
                            "PASS", 
                            f"Confidence: {confidence:.2f}, Response length: {len(result.get('response', ''))} chars"
                        )
                    else:
                        self.log_test(
                            f"AI Chat - {query['name']}", 
                            "WARN", 
                            f"Low confidence: {confidence:.2f}"
                        )
                else:
                    self.log_test(f"AI Chat - {query['name']}", "FAIL", f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"AI Chat - {query['name']}", "FAIL", f"Error: {str(e)}")
    
    def test_resume_analysis_api(self):
        """Test resume analysis via API"""
        print("Testing Resume Analysis API...")
        
        real_resume = """
        JOHN DOE
        Senior Software Engineer
        Email: john.doe@email.com | Phone: +91-98765-43210
        Location: Bangalore, Karnataka
        
        SUMMARY
        Experienced software engineer with 5 years of expertise in full-stack development, 
        specializing in Python, React, and cloud technologies. Proven track record of 
        delivering scalable applications and leading development teams.
        
        SKILLS
        Programming Languages: Python, JavaScript, TypeScript, Java, SQL
        Frontend Technologies: React, Angular, Vue.js, HTML5, CSS3, Bootstrap
        Backend Technologies: Node.js, Django, Flask, Express.js, Spring Boot
        Databases: PostgreSQL, MongoDB, MySQL, Redis, Elasticsearch
        Cloud & DevOps: AWS, Azure, Docker, Kubernetes, Jenkins, Git, CI/CD
        Tools & Others: JIRA, Postman, VS Code, PyCharm, Linux, Agile/Scrum
        
        EXPERIENCE
        
        Senior Software Engineer
        TechCorp Solutions | Bangalore | 2021-Present
        • Led development of microservices architecture serving 100K+ users
        • Implemented CI/CD pipelines reducing deployment time by 70%
        • Mentored 5 junior developers and conducted technical interviews
        • Technologies: Python, React, AWS, Docker, PostgreSQL, Redis
        
        Software Developer
        StartupXYZ | Remote | 2019-2021
        • Developed full-stack web applications using MERN stack
        • Collaborated with cross-functional teams in agile environment
        • Built real-time features using WebSocket and Socket.io
        • Technologies: Node.js, React, MongoDB, Express.js, Socket.io
        
        EDUCATION
        Bachelor of Technology in Computer Science
        Bangalore University | 2015-2019
        
        CERTIFICATIONS
        • AWS Certified Solutions Architect - Associate
        • MongoDB Certified Developer
        • Google Cloud Professional Developer
        
        LANGUAGES
        English (Fluent), Hindi (Native), Kannada (Conversational)
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/api/analyze-resume",
                json={"resume_text": real_resume},
                timeout=30
            )
            
            if response.status_code == 200:
                analysis = response.json()
                skills_count = len(analysis.get('skills', []))
                experience = analysis.get('experience_years', 0)
                recommendations = len(analysis.get('recommendations', []))
                
                self.log_test(
                    "Resume Analysis API", 
                    "PASS", 
                    f"Skills: {skills_count}, Experience: {experience} years, Recommendations: {recommendations}"
                )
                
                # Test specific skills extraction
                if skills_count > 10:
                    self.log_test("Skills Extraction", "PASS", f"Extracted {skills_count} skills")
                else:
                    self.log_test("Skills Extraction", "WARN", f"Only {skills_count} skills extracted")
                    
            else:
                self.log_test("Resume Analysis API", "FAIL", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Resume Analysis API", "FAIL", f"Error: {str(e)}")
    
    def test_job_search_api(self):
        """Test job search functionality via API"""
        print("Testing Job Search API...")
        
        search_scenarios = [
            {
                "name": "Python Developer Search",
                "query": {
                    "query": "Python developer",
                    "location": "Bangalore",
                    "experience": "3-5 years",
                    "skills": ["Python", "React"],
                    "limit": 5
                }
            },
            {
                "name": "Remote Jobs Search",
                "query": {
                    "query": "remote software engineer",
                    "location": "Remote",
                    "limit": 3
                }
            },
            {
                "name": "Data Scientist Search",
                "query": {
                    "query": "data scientist",
                    "skills": ["Python", "Machine Learning"],
                    "limit": 3
                }
            }
        ]
        
        for scenario in search_scenarios:
            try:
                response = requests.post(
                    f"{self.base_url}/api/jobs/search",
                    json=scenario["query"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    jobs_found = result.get('total', 0)
                    
                    self.log_test(
                        f"Job Search - {scenario['name']}", 
                        "PASS", 
                        f"Found {jobs_found} jobs"
                    )
                else:
                    self.log_test(f"Job Search - {scenario['name']}", "FAIL", f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Job Search - {scenario['name']}", "FAIL", f"Error: {str(e)}")
    
    def test_cli_mode(self):
        """Test CLI mode functionality"""
        print("Testing CLI Mode...")
        
        # Test CLI initialization
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ai_agent.cli", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.log_test("CLI Help", "PASS", "CLI help command working")
            else:
                self.log_test("CLI Help", "FAIL", f"CLI help failed: {result.stderr}")
                return
                
        except Exception as e:
            self.log_test("CLI Help", "FAIL", f"Error: {str(e)}")
            return
        
        # Test single query via CLI
        test_query = "I'm a Python developer looking for remote opportunities"
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ai_agent.cli", "--query", test_query],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and "AI:" in result.stdout:
                self.log_test("CLI Single Query", "PASS", "CLI query processing working")
            else:
                self.log_test("CLI Single Query", "FAIL", f"CLI query failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.log_test("CLI Single Query", "FAIL", "CLI query timed out")
        except Exception as e:
            self.log_test("CLI Single Query", "FAIL", f"Error: {str(e)}")
    
    def test_data_models(self):
        """Test data model imports and functionality"""
        print("Testing Data Models...")
        
        try:
            # Test model imports
            from models import Job, ChatResponse, ResumeAnalysis, JobSearchQuery
            self.log_test("Model Imports", "PASS", "All models imported successfully")
            
            # Test Job model creation
            job_data = {
                "job_id": "test_001",
                "title": "Senior Python Developer",
                "company": "TestCorp",
                "location": "Bangalore",
                "experience": "4-7 years",
                "skills": ["Python", "React", "AWS"],
                "description": "Test job description",
                "posted_date": datetime.now(),
                "url": "https://example.com/job",
                "platform": "naukri"
            }
            
            job = Job(**job_data)
            self.log_test("Job Model", "PASS", f"Created job: {job.title} at {job.company}")
            
            # Test ChatResponse model
            chat_response = ChatResponse(
                response="Test response",
                session_id="test_session",
                confidence=0.95
            )
            self.log_test("ChatResponse Model", "PASS", f"Created response with confidence: {chat_response.confidence}")
            
            # Test JobSearchQuery model
            search_query = JobSearchQuery(
                query="Python developer",
                location="Bangalore",
                limit=10
            )
            self.log_test("JobSearchQuery Model", "PASS", f"Created search query: {search_query.query}")
            
        except ImportError as e:
            self.log_test("Model Imports", "FAIL", f"Import error: {str(e)}")
        except Exception as e:
            self.log_test("Data Models", "FAIL", f"Error: {str(e)}")
    
    def test_ai_agent_components(self):
        """Test AI agent components directly"""
        print("Testing AI Agent Components...")
        
        try:
            # Test agent initialization
            from ai_agent.agent import JobAssistantAgent
            from ai_agent.recommendations import JobRecommender
            
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key or openai_key == "your_openai_api_key_here":
                self.log_test("AI Agent Init", "SKIP", "OpenAI API key not configured")
                return
            
            agent = JobAssistantAgent(openai_key)
            self.log_test("AI Agent Init", "PASS", "Agent initialized successfully")
            
            # Test intent classifier
            from ai_agent.intent_classifier import IntentClassifier
            classifier = IntentClassifier(agent.llm)
            self.log_test("Intent Classifier", "PASS", "Intent classifier initialized")
            
            # Test job recommender
            recommender = JobRecommender()
            self.log_test("Job Recommender", "PASS", "Job recommender initialized")
            
        except Exception as e:
            self.log_test("AI Agent Components", "FAIL", f"Error: {str(e)}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARN"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        print(f"Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   PASSED: {passed_tests}")
        print(f"   FAILED: {failed_tests}")
        print(f"   Warnings: {warning_tests}")
        print(f"   Skipped: {skipped_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\nTest Duration: {time.time() - self.start_time:.2f} seconds")
        
        # Show failed tests
        if failed_tests > 0:
            print(f"\nFAILED Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   - {result['test']}: {result['details']}")
        
        # Show warnings
        if warning_tests > 0:
            print(f"\nWarnings:")
            for result in self.test_results:
                if result["status"] == "WARN":
                    print(f"   - {result['test']}: {result['details']}")
        
        # Overall status
        if failed_tests == 0:
            print(f"\nALL TESTS PASSED! System is ready for production!")
        elif failed_tests < total_tests * 0.2:  # Less than 20% failed
            print(f"\nMOST TESTS PASSED! System is mostly functional.")
        else:
            print(f"\nMANY TESTS FAILED! System needs attention.")
        
        # Save detailed report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "warnings": warning_tests,
                    "skipped": skipped_tests,
                    "success_rate": (passed_tests/total_tests*100) if total_tests > 0 else 0,
                    "duration": time.time() - self.start_time
                },
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_file}")
        
        return failed_tests == 0

def main():
    """Main test runner"""
    print("Intelligent Job Assistant - Comprehensive System Test")
    print("="*60)
    print("Testing: API, CLI, AI Agent, Job Recommendations, Resume Analysis")
    print("="*60)
    
    tester = SystemTester()
    
    # Run all tests
    tests = [
        ("System Health", tester.test_system_health),
        ("Data Models", tester.test_data_models),
        ("AI Agent Components", tester.test_ai_agent_components),
        ("AI Chat API", tester.test_ai_chat_api),
        ("Resume Analysis API", tester.test_resume_analysis_api),
        ("Job Search API", tester.test_job_search_api),
        ("CLI Mode", tester.test_cli_mode),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            tester.log_test(test_name, "FAIL", f"Test crashed: {str(e)}")
    
    # Generate report
    success = tester.generate_report()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
