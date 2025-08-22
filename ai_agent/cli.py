#!/usr/bin/env python3
"""
Command-line interface for the Intelligent Job Assistant
"""

import asyncio
import logging
import sys
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agent.agent import JobAssistantAgent
from ai_agent.recommendations import JobRecommender

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JobAssistantCLI:
    """Command-line interface for the job assistant"""
    
    def __init__(self):
        self.agent = None
        self.recommender = None
        self.session_id = None
        
    async def initialize(self):
        """Initialize the AI agent and recommender"""
        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                logger.error("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
                return False
            
            self.agent = JobAssistantAgent(openai_api_key)
            self.recommender = JobRecommender()
        
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            return False
    
    async def start_interactive_mode(self):
        """Start interactive chat mode"""
        if not self.agent:
            logger.error("AI Agent not initialized")
            return
        
        print("\n" + "="*60)
        print("Intelligent Job Assistant - Interactive Mode")
        print("="*60)
        print("Type 'help' for available commands, 'quit' to exit")
        print("="*60 + "\n")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if user_input.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                
                if user_input.lower() == 'resume':
                    await self.handle_resume_analysis()
                    continue
                
                if user_input.lower() == 'stats':
                    await self.show_stats()
                    continue
                
                # Process regular query
                print("AI: Processing your request...")
                response = await self.agent.query(user_input, self.session_id)
                
                print(f"AI: {response.response}")
                print(f"Confidence: {response.confidence:.2f}")
                print("-" * 40)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error processing input: {e}")
                print("AI: I encountered an error. Please try again.")
    
    def show_help(self):
        """Show available commands"""
        print("\nAvailable Commands:")
        print("  help     - Show this help message")
        print("  resume   - Analyze a resume")
        print("  stats    - Show system statistics")
        print("  clear    - Clear the screen")
        print("  quit     - Exit the application")
        print("\nExample Queries:")
        print("  - 'Show me data scientist jobs in Bangalore'")
        print("  - 'What skills do I need for a machine learning engineer?'")
        print("  - 'How to prepare for technical interviews?'")
        print("  - 'Find remote software developer positions'")
        print("  - 'What are the top companies hiring Python developers?'")
        print()
    
    async def handle_resume_analysis(self):
        """Handle resume analysis request"""
        if not self.recommender:
                            print("AI: Resume analysis service not available")
            return
        
        print("\nResume Analysis")
        print("Please paste your resume text (press Enter twice when done):")
        
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        
        resume_text = "\n".join(lines[:-1])  # Remove the last empty line
        
        if not resume_text.strip():
                            print("AI: No resume text provided")
            return
        
                        print("\nAI: Analyzing your resume...")
        
        try:
            analysis = await self.recommender.analyze_resume(resume_text)
            
                            print("\nResume Analysis Results:")
            print(f"Skills identified: {', '.join(analysis.skills[:10])}")
            
            if analysis.experience_years:
                print(f"Experience level: {analysis.experience_years} years")
            
            if analysis.preferred_locations:
                print(f"Preferred locations: {', '.join(analysis.preferred_locations)}")
            
            if analysis.job_preferences:
                print(f"Job preferences: {', '.join(analysis.job_preferences)}")
            
            if analysis.recommendations:
                print(f"\nTop Job Recommendations:")
                for i, rec in enumerate(analysis.recommendations[:5], 1):
                    print(f"{i}. {rec.job.title} at {rec.job.company}")
                    print(f"   Score: {rec.score:.2f} - {rec.rationale}")
                    print()
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {e}")
                            print("AI: I encountered an error analyzing your resume. Please try again.")
    
    async def show_stats(self):
        """Show system statistics"""
                        print("\nSystem Statistics:")
        print(f"AI Agent: {'Active' if self.agent else 'Inactive'}")
        print(f"Recommender: {'Active' if self.recommender else 'Inactive'}")
        print(f"Session ID: {self.session_id or 'None'}")
        print()
    
    async def run_single_query(self, query: str):
        """Run a single query and exit"""
        if not self.agent:
            logger.error("AI Agent not initialized")
            return
        
        try:
                            print(f"AI: Processing query: {query}")
            response = await self.agent.query(query)
            
                            print(f"\nAI: {response.response}")
            print(f"Confidence: {response.confidence:.2f}")
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
                            print("AI: I encountered an error processing your query.")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Intelligent Job Assistant CLI")
    parser.add_argument("--query", "-q", help="Single query to process")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = JobAssistantCLI()
    
    if not await cli.initialize():
        sys.exit(1)
    
    try:
        if args.query:
            # Single query mode
            await cli.run_single_query(args.query)
        else:
            # Interactive mode (default)
            await cli.start_interactive_mode()
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

