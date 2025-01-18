import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LinkedIn credentials
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# LLM Configuration
TEMPERATURE = 0.7
MAX_TOKENS = 32768
MODEL_NAME = "mixtral-8x7b-32768"

# Research Configuration
RESEARCH_KEYWORDS = [
    "current",
    "latest",
    "recent",
    "news",
    "trend",
    "update",
    "development"
]
