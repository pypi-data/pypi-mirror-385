"""
Configuration management for Sales Agent MCP Server
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from multiple possible locations
# 1. Local .env file (for development)
# 2. Global config file (for pipx/uvx installations)
# 3. Environment variables (for Claude Desktop config)

# Try to load from current directory first (development)
load_dotenv()

# Try to load from global config directory (production)
config_dir = Path.home() / ".config" / "sales-agent-mcp"
config_file = config_dir / ".env"
if config_file.exists():
    load_dotenv(config_file)


class Config:
    """Configuration holder for Sales Agent MCP Server"""
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """OpenAI API key for agent operations"""
        return os.getenv("OPENAI_API_KEY")
    
    @property
    def sendgrid_api_key(self) -> Optional[str]:
        """SendGrid API key for email sending"""
        return os.getenv("SENDGRID_API_KEY")
    
    @property
    def sender_email(self) -> Optional[str]:
        """Verified sender email address"""
        return os.getenv("SENDER_EMAIL")
    
    @property
    def recipient_emails(self) -> list[str]:
        """List of recipient email addresses"""
        emails = os.getenv("RECIPIENT_EMAILS", "")
        return [e.strip() for e in emails.split(",") if e.strip()]
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY not configured")
        
        if not self.sendgrid_api_key:
            errors.append("SENDGRID_API_KEY not configured")
        
        if not self.sender_email:
            errors.append("SENDER_EMAIL not configured")
        
        return len(errors) == 0, errors


# Global config instance
config = Config()
