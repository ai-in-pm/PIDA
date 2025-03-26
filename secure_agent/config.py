"""Configuration module for the secure AI agent."""

import os
import dotenv
from pathlib import Path

# Load environment variables from .env file
dotenv.load_dotenv(Path(__file__).parent.parent / '.env')

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Database settings
DATABASE_PATH = Path(__file__).parent.parent / 'data' / 'secure_agent.db'

# Security settings
TRUSTED_EMAIL_DOMAINS = ['company.com', 'trusted-partner.com']
MAX_QUERY_LENGTH = 1000

# Logging settings
LOG_LEVEL = 'INFO'
LOG_FILE = Path(__file__).parent.parent / 'logs' / 'secure_agent.log'

# Ensure directories exist
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
