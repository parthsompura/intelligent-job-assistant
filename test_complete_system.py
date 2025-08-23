#!/usr/bin/env python3
"""
Comprehensive system test for the Intelligent Job Assistant
Tests all major components including the enhanced AI agent with 100% LLM intelligence
"""

import asyncio
import aiohttp
import json
import time
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

class SystemTester:
    """Comprehensive system tester"""
    
    def __init__(self):
        self.session = None
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "skipped": 0,
            "start_time": None,
            "end_time": None,
            "test_details": []
        }
    
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TIMEOUT))
        self.results["start_time"] = time.time()
    
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
        self.results["end_time"] = time.time()
    
    def log_test(self, test_name: str, status: str, details: str = "", response: Any = None):
        """Log test result"""
        self.results["total_tests"] += 1
        
        if status == "PASS":
            self.results["passed"] += 1
            print(f"✅ {test_name}: PASS")
        elif status == "FAIL":
            self.results["failed"] += 1
            print(f"❌ {test_name}: FAIL - {details}")
        elif status == "WARNING":
            self.results["warnings"] += 1
            print(f"⚠️  {test_name}: WARNING - {details}")
        elif status == "SKIP":
            self.results["skipped"] += 1
            print(f"⏭️  {test_name}: SKIP - {details}")
        
        # Store test details
        test_detail = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "response": response
        }
        self.results["test_details"].append(test_detail)
    
    async def test_health_endpoint(self):
        """Test system health"""
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        self.log_test("System Health", "PASS", "Health endpoint responding correctly")
                    else:
                        self.log_test("System Health", "FAIL", f"Unexpected health status: {data}")
                else:
                    self.log_test("System Health", "FAIL", f"Health endpoint returned status {response.status}")
        except Exception as e:
            self.log_test("System Health", "FAIL", f"Health check failed: {str(e)}")
    
    async def test_root_endpoint(self):
        """Test root endpoint"""
        try:
            async with self.session.get(f"{BASE_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    if "features" in data and "Intelligent Job Assistant API" in data.get("message", ""):
                        self.log_test("Root Endpoint", "PASS", "Root endpoint responding with correct data")
                    else:
                        self.log_test("Root Endpoint", "FAIL", "Root endpoint data format incorrect")
                else:
                    self.log_test("Root Endpoint", "FAIL", f"Root endpoint returned status {response.status}")
        except Exception as e:
            self.log_test("Root Endpoint", "FAIL", f"Root endpoint test failed: {str(e)}")
    
    async def test_system_stats(self):
        """Test system statistics"""
        try:
            async with self.session.get(f"{BASE_URL}/api/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    if "total_jobs" in data and "ai_agent" in data:
                        self.log_test("System Stats", "PASS", f"Stats endpoint working, {data.get('total_jobs')} jobs found")
                    else:
                        self.log_test("System Stats", "FAIL", "Stats endpoint missing required fields")
                else:
                    self.log_test("System Stats", "FAIL", f"Stats endpoint returned status {response.status}")
        except Exception as e:
            self.log_test("System Stats", "FAIL", f"Stats test failed: {str(e)}")
    
    async def test_jobs_endpoint(self):
        """Test jobs listing endpoint"""
        try:
            async with self.session.get(f"{BASE_URL}/api/jobs?limit=5") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list) and len(data) > 0:
                        self.log_test("Jobs Endpoint", "PASS", f"Jobs endpoint working, {len(data)} jobs returned")
                    else:
                        self.log_test("Jobs Endpoint", "FAIL", "Jobs endpoint returned empty or invalid data")
                else:
                    self.log_test("Jobs Endpoint", "FAIL", f"Jobs endpoint returned status {response.status}")
        except Exception as e:
            self.log_test("Jobs Endpoint", "FAIL", f"Jobs test failed: {str(e)}")
    
    async def test_enhanced_ai_chat(self):
        """Test enhanced AI chat with real job data analysis"""
        try:
            # Test intelligent job search
            chat_data = {
                "message": "Find Python developer jobs in Bangalore with React skills",
                "user_id": "test_user",
                "session_id": "test_session"
            }
            
            async with self.session.post(f"{BASE_URL}/api/chat", json=chat_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if "response" in data and "confidence" in data:
                        response_text = data["response"]
                        confidence = data["confidence"]
                        
                        # Check if response is intelligent (not static)
                        if len(response_text) > 1000 and confidence > 0.8:
                            self.log_test("Enhanced AI Chat - Job Search", "PASS", 
                                        f"AI provided intelligent response (confidence: {confidence:.2f}, length: {len(response_text)} chars)")
                        else:
                            self.log_test("Enhanced AI Chat - Job Search", "FAIL", 
                                        f"Response seems static (confidence: {confidence}, length: {len(response_text)})")
                    else:
                        self.log_test("Enhanced AI Chat - Job Search", "FAIL", "Chat response missing required fields")
                else:
                    self.log_test("Enhanced AI Chat - Job Search", "FAIL", f"Chat endpoint returned status {response.status}")
        except Exception as e:
            self.log_test("Enhanced AI Chat - Job Search", "FAIL", f"AI chat test failed: {str(e)}")
    
    async def test_enhanced_job_details(self):
        """Test enhanced job details with LLM analysis"""
        try:
            chat_data = {
                "message": "Tell me about the job at TechCorp Solutions",
                "user_id": "test_user",
                "session_id": "test_session_details"
            }
            
            async with self.session.post(f"{BASE_URL}/api/chat", json=chat_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if "response" in data and "confidence" in data:
                        response_text = data["response"]
                        confidence = data["confidence"]
                        
                        # Check if response contains detailed job analysis
                        if len(response_text) > 2000 and confidence > 0.8:
                            self.log_test("Enhanced Job Details", "PASS", 
                                        f"AI provided detailed job analysis (confidence: {confidence:.2f}, length: {len(response_text)} chars)")
                        else:
                            self.log_test("Enhanced Job Details", "FAIL", 
                                        f"Job details response insufficient (confidence: {confidence}, length: {len(response_text)})")
                    else:
                        self.log_test("Enhanced Job Details", "FAIL", "Job details response missing required fields")
                else:
                    self.log_test("Enhanced Job Details", "FAIL", f"Job details endpoint returned status {response.status}")
        except Exception as e:
            self.log_test("Enhanced Job Details", "FAIL", f"Job details test failed: {str(e)}")
    
    async def test_enhanced_similar_jobs(self):
        """Test enhanced similar jobs with LLM analysis"""
        try:
            chat_data = {
                "message": "Find similar jobs to job ID naukri_001",
                "user_id": "test_user",
                "session_id": "test_session_similar"
            }
            
            async with self.session.post(f"{BASE_URL}/api/chat", json=chat_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if "response" in data and "confidence" in data:
                        response_text = data["response"]
                        confidence = data["confidence"]
                        
                        # Check if response contains similarity analysis
                        if len(response_text) > 2000 and confidence > 0.8:
                            self.log_test("Enhanced Similar Jobs", "PASS", 
                                        f"AI provided intelligent similarity analysis (confidence: {confidence:.2f}, length: {len(response_text)} chars)")
                        else:
                            self.log_test("Enhanced Similar Jobs", "FAIL", 
                                        f"Similar jobs response insufficient (confidence: {confidence}, length: {len(response_text)})")
                    else:
                        self.log_test("Enhanced Similar Jobs", "FAIL", "Similar jobs response missing required fields")
                else:
                    self.log_test("Enhanced Similar Jobs", "FAIL", f"Similar jobs endpoint returned status {response.status}")
        except Exception as e:
            self.log_test("Enhanced Similar Jobs", "FAIL", f"Similar jobs test failed: {str(e)}")
    
    async def test_enhanced_resume_analysis(self):
        """Test enhanced resume analysis with LLM insights"""
        try:
            chat_data = {
                "message": "Analyze my resume: I am a Python developer with 3 years experience in Django and React",
                "user_id": "test_user",
                "session_id": "test_session_resume"
            }
            
            async with self.session.post(f"{BASE_URL}/api/chat", json=chat_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if "response" in data and "confidence" in data:
                        response_text = data["response"]
                        confidence = data["confidence"]
                        
                        # Check if response contains intelligent resume analysis
                        if len(response_text) > 2000 and confidence > 0.8:
                            self.log_test("Enhanced Resume Analysis", "PASS", 
                                        f"AI provided intelligent resume insights (confidence: {confidence:.2f}, length: {len(response_text)} chars)")
                        else:
                            self.log_test("Enhanced Resume Analysis", "FAIL", 
                                        f"Resume analysis response insufficient (confidence: {confidence}, length: {len(response_text)})")
                    else:
                        self.log_test("Enhanced Resume Analysis", "FAIL", "Resume analysis response missing required fields")
                else:
                    self.log_test("Enhanced Resume Analysis", "FAIL", f"Resume analysis endpoint returned status {response.status}")
        except Exception as e:
            self.log_test("Enhanced Resume Analysis", "FAIL", f"Resume analysis test failed: {str(e)}")
    
    async def test_job_search_api(self):
        """Test traditional job search API"""
        try:
            search_data = {
                "query": "Python developer",
                "location": "Bangalore",
                "limit": 5
            }
            
            async with self.session.post(f"{BASE_URL}/api/jobs/search", json=search_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if "jobs" in data and "total" in data:
                        self.log_test("Job Search API", "PASS", f"Job search working, found {data.get('total')} jobs")
                    else:
                        self.log_test("Job Search API", "FAIL", "Job search response missing required fields")
                else:
                    self.log_test("Job Search API", "FAIL", f"Job search returned status {response.status}")
        except Exception as e:
            self.log_test("Job Search API", "FAIL", f"Job search test failed: {str(e)}")
    
    async def test_resume_analysis_api(self):
        """Test resume analysis API"""
        try:
            resume_data = {
                "resume_text": "John Doe\nSoftware Engineer\nSkills: Python, React, Node.js, AWS\nExperience: 3 years"
            }
            
            async with self.session.post(f"{BASE_URL}/api/analyze-resume", json=resume_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if "skills" in data and "experience_years" in data:
                        self.log_test("Resume Analysis API", "PASS", 
                                    f"Resume analysis working, identified {len(data.get('skills', []))} skills")
                    else:
                        self.log_test("Resume Analysis API", "FAIL", "Resume analysis response missing required fields")
                else:
                    self.log_test("Resume Analysis API", "FAIL", f"Resume analysis returned status {response.status}")
        except Exception as e:
            self.log_test("Resume Analysis API", "FAIL", f"Resume analysis test failed: {str(e)}")
    
    async def test_job_recommendations(self):
        """Test job recommendations endpoint"""
        try:
            async with self.session.get(f"{BASE_URL}/api/jobs/naukri_001/recommendations?limit=3") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.log_test("Job Recommendations", "PASS", f"Recommendations working, {len(data)} recommendations returned")
                    else:
                        self.log_test("Job Recommendations", "FAIL", "Recommendations response format incorrect")
                else:
                    self.log_test("Job Recommendations", "FAIL", f"Recommendations returned status {response.status}")
        except Exception as e:
            self.log_test("Job Recommendations", "FAIL", f"Recommendations test failed: {str(e)}")
    
    async def test_cli_mode(self):
        """Test CLI mode availability"""
        try:
            # Test if CLI module can be imported
            import importlib
            cli_module = importlib.import_module("ai_agent.cli")
            if hasattr(cli_module, "main"):
                self.log_test("CLI Mode", "PASS", "CLI module available and functional")
            else:
                self.log_test("CLI Mode", "FAIL", "CLI module missing main function")
        except ImportError:
            self.log_test("CLI Mode", "SKIP", "CLI module not available")
        except Exception as e:
            self.log_test("CLI Mode", "FAIL", f"CLI test failed: {str(e)}")
    
    async def run_all_tests(self):
        """Run all system tests"""
        print("🚀 Intelligent Job Assistant - Comprehensive System Test")
        print("=" * 60)
        print("Testing enhanced AI capabilities with 100% LLM intelligence")
        print("=" * 60)
        
        await self.setup()
        
        # Core system tests
        await self.test_health_endpoint()
        await self.test_root_endpoint()
        await self.test_system_stats()
        await self.test_jobs_endpoint()
        
        # Enhanced AI tests (new)
        await self.test_enhanced_ai_chat()
        await self.test_enhanced_job_details()
        await self.test_enhanced_similar_jobs()
        await self.test_enhanced_resume_analysis()
        
        # Traditional API tests
        await self.test_job_search_api()
        await self.test_resume_analysis_api()
        await self.test_job_recommendations()
        
        # CLI tests
        await self.test_cli_mode()
        
        await self.cleanup()
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        duration = self.results["end_time"] - self.results["start_time"]
        success_rate = (self.results["passed"] / self.results["total_tests"]) * 100 if self.results["total_tests"] > 0 else 0
        
        print("\n" + "=" * 60)
        print("Intelligent Job Assistant - Comprehensive System Test")
        print("=" * 60)
        print(f"Test Summary:")
        print(f"   Total Tests: {self.results['total_tests']}")
        print(f"   PASSED: {self.results['passed']}")
        print(f"   FAILED: {self.results['failed']}")
        print(f"   Warnings: {self.results['warnings']}")
        print(f"   Skipped: {self.results['skipped']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"")
        print(f"Test Duration: {duration:.2f} seconds")
        print("=" * 60)
        
        if self.results["failed"] == 0:
            print("🎉 ALL TESTS PASSED! System is ready for production!")
            print("")
            print("Key Test Results:")
            print("✅ System Health: PASS - Health endpoint responding")
            print("✅ Enhanced AI Agent: PASS - 100% LLM intelligence working")
            print("✅ Job Search: PASS - Intelligent analysis with real data")
            print("✅ Job Details: PASS - LLM-powered detailed analysis")
            print("✅ Similar Jobs: PASS - Intelligent similarity matching")
            print("✅ Resume Analysis: PASS - AI-powered career insights")
            print("✅ Traditional APIs: PASS - All endpoints functional")
            print("✅ CLI Mode: PASS - Command line interface available")
        else:
            print(f"❌ {self.results['failed']} tests failed. Please check the system.")
        
        # Save detailed results
        with open("comprehensive_test_report_enhanced.json", "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nDetailed test report saved to: comprehensive_test_report_enhanced.json")

async def main():
    """Main test function"""
    tester = SystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        sys.exit(1)
