"""
Sales Agent MCP Server
Exposes multi-agent sales system as MCP tools for Claude Desktop/Cursor
"""
import asyncio
import sys
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .config import config
from .agents import (
    sales_manager,
    email_formatter_agent,
    subject_writer_agent,
    html_converter_agent,
    generate_emails_parallel,
    sales_writer_1,
    sales_writer_2,
    sales_writer_3
)
from agents import Runner

# Initialize MCP server
mcp = FastMCP("sales-agent-mcp")

# =============================================================================
# MCP TOOLS
# =============================================================================

@mcp.tool()
async def generate_sales_campaign(
    product_description: str,
    target_audience: str = "B2B SaaS companies, CTOs and Engineering Leaders",
    num_options: int = 3
) -> dict[str, Any]:
    """
    Generate a complete AI-powered sales email campaign.
    
    This tool orchestrates multiple AI agents to:
    1. Generate 3 different email variations (data-driven, conversational, direct)
    2. Evaluate all options with AI manager
    3. Select the best email with reasoning
    4. Return the winning email with metadata
    
    Args:
        product_description: Detailed description of product/service to promote
        target_audience: Description of target audience (default: B2B SaaS CTOs)
        num_options: Number of email variations to generate (default: 3)
    
    Returns:
        Dictionary containing:
        - selected_email: The best email text
        - reasoning: Why this email was selected
        - status: "success" or "error"
        - metadata: Additional info (model used, etc.)
    
    Example:
        generate_sales_campaign(
            product_description="AI code review tool that catches bugs automatically",
            target_audience="Startup CTOs in fintech"
        )
    """
    try:
        # Validate configuration
        is_valid, errors = config.validate()
        if not is_valid:
            return {
                "status": "error",
                "error": "Configuration missing",
                "details": errors,
                "message": "Please set OPENAI_API_KEY in your environment variables"
            }
        
        campaign_prompt = f"""
        Create a cold sales email campaign for the following product/service:
        
        PRODUCT/SERVICE:
        {product_description}
        
        TARGET AUDIENCE:
        {target_audience}
        
        Please:
        1. Generate {num_options} different email options using available tools
        2. Evaluate each email carefully
        3. Select the BEST email for this audience
        4. Provide clear reasoning for your choice
        
        The email should be compelling, professional, and likely to get a response.
        """
        
        # Run sales manager agent
        result = await Runner.run(sales_manager, campaign_prompt)
        
        return {
            "status": "success",
            "selected_email": result.final_output,
            "reasoning": "Email selected by AI manager after evaluating all options",
            "metadata": {
                "orchestrator_model": "gpt-4o",
                "writer_model": "gpt-4o-mini",
                "num_options_generated": num_options,
                "target_audience": target_audience
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to generate sales campaign. Check your API keys and try again."
        }


@mcp.tool()
async def send_sales_email(
    email_body: str,
    recipients: Optional[list[str]] = None
) -> dict[str, Any]:
    """
    Format and send a sales email to prospects via SendGrid.
    
    This tool:
    1. Generates a compelling subject line
    2. Converts plain text to professional HTML
    3. Sends via SendGrid to configured recipients
    
    Args:
        email_body: Plain text email content
        recipients: Optional list of recipient emails (uses RECIPIENT_EMAILS env var if not provided)
    
    Returns:
        Dictionary with send status and details
    
    Example:
        send_sales_email(
            email_body="Your plain text email here...",
            recipients=["prospect@example.com"]
        )
    """
    try:
        # Validate configuration
        if not config.sendgrid_api_key:
            return {
                "status": "error",
                "error": "SENDGRID_API_KEY not configured",
                "message": "Please set SENDGRID_API_KEY in your environment variables"
            }
        
        if not config.sender_email:
            return {
                "status": "error",
                "error": "SENDER_EMAIL not configured",
                "message": "Please set SENDER_EMAIL in your environment variables"
            }
        
        # Override recipients if provided
        if recipients:
            import os
            original_recipients = os.getenv("RECIPIENT_EMAILS")
            os.environ["RECIPIENT_EMAILS"] = ",".join(recipients)
        
        # Hand off to email formatter agent
        prompt = f"""
        Format and send this sales email:
        
        {email_body}
        
        Please:
        1. Generate a compelling subject line
        2. Convert to professional HTML format
        3. Send to all configured recipients
        """
        
        result = await Runner.run(email_formatter_agent, prompt)
        
        # Restore original recipients
        if recipients and original_recipients:
            import os
            os.environ["RECIPIENT_EMAILS"] = original_recipients
        
        return {
            "status": "success",
            "message": result.final_output,
            "recipients": recipients or config.recipient_emails
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to send email. Check your SendGrid configuration."
        }


@mcp.tool()
async def generate_email_subject(email_body: str) -> str:
    """
    Generate a compelling subject line for an email.
    
    Uses AI to create an attention-grabbing subject line that:
    - Is 40-60 characters
    - Creates curiosity or urgency
    - Avoids spam triggers
    
    Args:
        email_body: The email body text
    
    Returns:
        Generated subject line
    
    Example:
        generate_email_subject("Your email body here...")
    """
    try:
        result = await Runner.run(subject_writer_agent, email_body)
        return result.final_output.strip()
    except Exception as e:
        return f"Error generating subject: {str(e)}"


@mcp.tool()
async def convert_email_to_html(email_body: str) -> str:
    """
    Convert plain text email to professional HTML format.
    
    Creates a mobile-responsive HTML email with:
    - Professional styling
    - Inline CSS for email client compatibility
    - Proper formatting and hierarchy
    
    Args:
        email_body: Plain text email (can include markdown)
    
    Returns:
        HTML-formatted email
    
    Example:
        convert_email_to_html("Your plain text email...")
    """
    try:
        result = await Runner.run(html_converter_agent, email_body)
        return result.final_output
    except Exception as e:
        return f"<p>Error converting to HTML: {str(e)}</p>"


# =============================================================================
# MCP RESOURCES
# =============================================================================

@mcp.resource("config://status")
def get_configuration_status() -> str:
    """
    Check configuration status and API key setup.
    
    Returns:
        Status report of all required environment variables
    """
    is_valid, errors = config.validate()
    
    status_lines = [
        "🔧 Sales Agent MCP Server Configuration Status",
        "=" * 50,
        ""
    ]
    
    # Check each required variable
    status_lines.append(f"OpenAI API Key: {'✅ Configured' if config.openai_api_key else '❌ Missing'}")
    status_lines.append(f"SendGrid API Key: {'✅ Configured' if config.sendgrid_api_key else '❌ Missing'}")
    status_lines.append(f"Sender Email: {'✅ Configured' if config.sender_email else '❌ Missing'}")
    status_lines.append(f"Recipient Emails: {'✅ Configured' if config.recipient_emails else '⚠️  Optional'}")
    
    status_lines.append("")
    status_lines.append("Required Environment Variables:")
    status_lines.append("- OPENAI_API_KEY")
    status_lines.append("- SENDGRID_API_KEY")
    status_lines.append("- SENDER_EMAIL")
    status_lines.append("- RECIPIENT_EMAILS (optional)")
    
    if not is_valid:
        status_lines.append("")
        status_lines.append("⚠️  Configuration Issues:")
        for error in errors:
            status_lines.append(f"   - {error}")
    
    return "\n".join(status_lines)


# =============================================================================
# SERVER ENTRY POINT
# =============================================================================

def main():
    """
    Main entry point for the MCP server.
    This function is called when running: uvx sales-agent-mcp
    """
    # Check configuration on startup
    is_valid, errors = config.validate()
    
    if not is_valid:
        print("⚠️  Configuration Warning:", file=sys.stderr)
        for error in errors:
            print(f"   - {error}", file=sys.stderr)
        print("\nServer will start, but tools may not work without proper configuration.", file=sys.stderr)
        print("Please set required environment variables in your Claude Desktop config.\n", file=sys.stderr)
    
    # Run MCP server using stdio transport
    mcp.run(transport="stdio")


def main_sync():
    """Synchronous wrapper for the main function"""
    main()

if __name__ == "__main__":
    main_sync()
