#!/usr/bin/env python3
"""
Main entry point for the Intelligent Job Assistant System
"""

import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function"""
    print("Starting Intelligent Job Assistant System...")
    
    try:
        # Check OpenAI API key
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("Warning: OpenAI API key not found. AI features will be limited.")
        else:
            print("OpenAI API key found")
        
        # Check storage configuration
        print("Using JSON file storage (no database required)")
        
        print("\n" + "="*60)
        print("Intelligent Job Assistant System")
        print("="*60)
        print("Available components:")
        print("1. Job Scraper (Naukri & LinkedIn)")
        print("2. AI Agent (Intelligent Chat Interface)")
        print("3. Job Recommendations")
        print("4. Resume Analysis")
        print("5. FastAPI REST API")
        print("="*60)
        
        print("\nStarting services...")
        
        # Import and start FastAPI server
        try:
            from api.main import app
            import uvicorn
            
            print("FastAPI application loaded successfully")
            print("Starting web server on http://localhost:8000")
            print("API documentation available at http://localhost:8000/docs")
            
            # Start the server
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8000,
                log_level="info"
            )
            
        except ImportError as e:
            print(f"Error importing FastAPI application: {e}")
            print("   Please ensure all dependencies are installed")
            return 1
        except Exception as e:
            print(f"Error starting server: {e}")
            return 1
            
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Fatal error: {e}")
        return 1


async def run_cli():
    """Run CLI interface"""
    print("Starting CLI interface...")
    
    try:
        from ai_agent.cli import main as cli_main
        await cli_main()
    except ImportError as e:
        print(f"Error importing CLI: {e}")
        print("   Please ensure all dependencies are installed")
        return 1
    except Exception as e:
        print(f"Error running CLI: {e}")
        return 1


async def run_scraper():
    """Run job scraper"""
    print("Starting job scraper...")
    
    try:
        from job_scraper.main import main as scraper_main
        await scraper_main()
    except ImportError as e:
        print(f"Error importing scraper: {e}")
        print("   Please ensure all dependencies are installed")
        return 1
    except Exception as e:
        print(f"Error running scraper: {e}")
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Intelligent Job Assistant System")
    parser.add_argument("--mode", "-m", 
                       choices=["web", "cli", "scraper"], 
                       default="web",
                       help="Run mode: web (FastAPI), cli (interactive), scraper (job scraping)")
    
    args = parser.parse_args()
    
    if args.mode == "web":
        sys.exit(main())
    elif args.mode == "cli":
        sys.exit(asyncio.run(run_cli()))
    elif args.mode == "scraper":
        sys.exit(asyncio.run(run_scraper()))
    else:
        print(f"Unknown mode: {args.mode}")
        sys.exit(1)

