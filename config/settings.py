import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings and configuration"""
    
    # Application
    APP_NAME: str = "Intelligent Job Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    

    
    # Scraping Configuration
    HEADLESS_BROWSER: bool = os.getenv("HEADLESS_BROWSER", "True").lower() == "true"
    SCRAPING_DELAY: float = float(os.getenv("SCRAPING_DELAY", "2.0"))
    MAX_SCRAPING_PAGES: int = int(os.getenv("MAX_SCRAPING_PAGES", "10"))
    MAX_JOBS_PER_QUERY: int = int(os.getenv("MAX_JOBS_PER_QUERY", "100"))
    
    # Rate Limiting
    RATE_LIMIT_DELAY: float = float(os.getenv("RATE_LIMIT_DELAY", "1.0"))
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
    
    # AI Agent Configuration
    AGENT_SESSION_TIMEOUT: int = int(os.getenv("AGENT_SESSION_TIMEOUT", "3600"))  # 1 hour
    MAX_CONVERSATION_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "100"))
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
    
    # Job Recommendation Configuration
    MIN_RECOMMENDATION_SCORE: float = float(os.getenv("MIN_RECOMMENDATION_SCORE", "0.3"))
    MAX_RECOMMENDATIONS: int = int(os.getenv("MAX_RECOMMENDATIONS", "10"))
    SKILL_MATCH_WEIGHT: float = float(os.getenv("SKILL_MATCH_WEIGHT", "0.4"))
    EXPERIENCE_MATCH_WEIGHT: float = float(os.getenv("EXPERIENCE_MATCH_WEIGHT", "0.3"))
    LOCATION_MATCH_WEIGHT: float = float(os.getenv("LOCATION_MATCH_WEIGHT", "0.2"))
    DESCRIPTION_MATCH_WEIGHT: float = float(os.getenv("DESCRIPTION_MATCH_WEIGHT", "0.1"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # Security Configuration
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    API_KEY_HEADER: str = os.getenv("API_KEY_HEADER", "X-API-Key")
    API_KEY: Optional[str] = os.getenv("API_KEY")
    
    # Cache Configuration
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))
    
    # Monitoring Configuration
    METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "True").lower() == "true"
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))  # seconds
    
    # Job Platform Configuration
    SUPPORTED_PLATFORMS: list = ["naukri", "linkedin"]
    PLATFORM_CONFIGS: dict = {
        "naukri": {
            "base_url": "https://www.naukri.com",
            "search_url": "https://www.naukri.com/jobs-in-",
            "max_pages": 10,
            "delay": 2.0
        },
        "linkedin": {
            "base_url": "https://www.linkedin.com",
            "jobs_url": "https://www.linkedin.com/jobs",
            "max_pages": 10,
            "delay": 2.0
        }
    }
    
    # Resume Analysis Configuration
    RESUME_MAX_SIZE: int = int(os.getenv("RESUME_MAX_SIZE", "1024 * 1024"))  # 1MB
    SUPPORTED_RESUME_FORMATS: list = ["txt", "pdf", "doc", "docx"]
    SKILL_EXTRACTION_ENABLED: bool = os.getenv("SKILL_EXTRACTION_ENABLED", "True").lower() == "true"
    
    # Notification Configuration
    EMAIL_NOTIFICATIONS: bool = os.getenv("EMAIL_NOTIFICATIONS", "False").lower() == "true"
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required settings"""
        required_settings = [
            "OPENAI_API_KEY",
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not getattr(cls, setting):
                missing_settings.append(setting)
        
        if missing_settings:
            print(f"Missing required settings: {', '.join(missing_settings)}")
            return False
        
        return True
    

    
    @classmethod
    def get_platform_config(cls, platform: str) -> dict:
        """Get configuration for a specific job platform"""
        if platform.lower() not in cls.PLATFORM_CONFIGS:
            raise ValueError(f"Unsupported platform: {platform}")
        return cls.PLATFORM_CONFIGS[platform.lower()]


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance"""
    return settings


