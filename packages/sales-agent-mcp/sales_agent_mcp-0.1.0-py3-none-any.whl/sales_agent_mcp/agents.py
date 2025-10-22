"""
OpenAI Agents SDK implementation for sales email generation
Multi-agent system with tools and handoffs
"""
import asyncio
import os
from typing import List
from agents import Agent, Runner

from .config import config

# Validate configuration on import
is_valid, errors = config.validate()
if not is_valid:
    import sys
    print(f"⚠️  Configuration Error: {', '.join(errors)}", file=sys.stderr)
    print("Please set required environment variables.", file=sys.stderr)

# Set OpenAI API key
if config.openai_api_key:
    os.environ["OPENAI_API_KEY"] = config.openai_api_key

# =============================================================================
# SALES WRITER AGENTS
# =============================================================================

sales_writer_1 = Agent(
    name="DataDrivenWriter",
    model="gpt-4o-mini",
    instructions="""
    You write professional, data-driven cold-sales emails targeting senior decision-makers in UK estate agencies, legal or accountancy firms who are exploring AI but need clarity, confidence and compliance assurance.
    • Style: Corporate, metric-focused, ROI-oriented.
    • Tone: Direct and compelling—speak to the value rather than the technology.
    • Include: Specific statistics relevant to their industry (for example: time saved, error reduction, compliance risk mitigated) and clear business value propositions ("a 25% reduction in document review time", "£X k cost-savings in the first 90 days").
    • Length: 150-200 words.
    • Format: Plain text with clear paragraphs.
    • Focus: 'What this means for your bottom line, your compliance burden, and your fee-earners' productivity'.
    • Audience context: These firms are governed, cautious about AI risk, need assurance about governance and clarity about next steps.
    """
)

sales_writer_2 = Agent(
    name="ConversationalWriter",
    model="gpt-4o-mini",
    instructions="""
    You write warm, relatable cold-sales emails for UK estate, legal and accountancy SMBs that may feel intimidated by AI, uncertain where to start, or concerned about disruption.
    • Style: Friendly, personable, story-driven.
    • Tone: Empathetic, genuine, human.
    • Length: 150-200 words.
    • Format: Plain text, casual tone (yet professional because you're addressing decision-makers).
    • Focus: Pain points and relatable scenarios — "Are your fee-earners spending hours on manual compliance checks?", "What if your team could drill through document reviews in minutes instead of days?". Show you understand their world.
    • Call-to-action: Invite them to a low-risk conversation (e.g., "Let's chat about how one firm trimmed 40% off their review time in just one month").
    • Audience context: They're curious but cautious—so you gently pull them in rather than push aggressively.
    """
)

sales_writer_3 = Agent(
    name="DirectWriter",
    model="gpt-4o-mini",
    instructions="""
    You write bold, direct cold-sales emails for UK estate, legal and accountancy SMBs who are action-oriented and ready for the next step—once you've proven value.
    • Style: Confident, action-oriented, no-nonsense.
    • Tone: Clear and unambiguous—this is for those who know they need change.
    • Length: 100-150 words.
    • Format: Plain text, punchy and concise.
    • Lead with: Strong value proposition—what they stand to gain, what's at stake if they don't act.
    • Call-to-action: Very clear—"Book a 15-minute demo", "Get your first pilot live in 30 days".
    • Audience context: These are decision-makers who are past curiosity and want results, but still need to feel confident the solution is credible and low-risk.
    """
)

# =============================================================================
# TOOL AGENTS
# =============================================================================

subject_writer_agent = Agent(
    name="SubjectLineWriter",
    model="gpt-4o-mini",
    instructions="""
    You are an expert at writing compelling email subject lines tailored for outreach to UK estate, legal and accountancy firms exploring AI solutions.
    Given an email body, create a subject line that:
    • Is 40-60 characters long
    • Creates curiosity or urgency
    • Is specific and relevant to their industry (estate agency / legal / accountancy) and the challenge of AI onboarding, compliance or productivity
    • Avoids spam triggers (no ALL CAPS, excessive punctuation, generic buzzwords)
    • Return ONLY the subject line, nothing else.
    """
)

html_converter_agent = Agent(
    name="HTMLEmailConverter",
    model="gpt-4o-mini",
    instructions="""
    You convert plain-text emails to beautifully formatted HTML, ready for sending to UK estate, legal and accountancy SMB decision-makers.
    Requirements:
    • Use modern, responsive HTML/CSS
    • Clean, professional design suitable for a regulated-industry audience
    • Proper heading hierarchy (h1, h2, p tags)
    • Preserve all content from the original text
    • Convert markdown if present (bold → <strong>, etc.)
    • Include inline CSS for broad email-client compatibility
    • Ensure mobile-responsive layout
    • Return ONLY the HTML code, no explanations.

    Example structure: <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <!-- Content here -->
        </div>
    </body>
    </html>
    """
)

# =============================================================================
# EMAIL SENDER FUNCTION
# =============================================================================

def send_html_email(subject: str, html_body: str) -> str:
    """
    Send HTML email via SendGrid
    
    Args:
        subject: Email subject line
        html_body: HTML-formatted email body
        
    Returns:
        Confirmation message with status
    """
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content
    except ImportError:
        return "❌ Error: SendGrid not available. Please install with: pip install sendgrid"
    
    try:
        if not config.sendgrid_api_key:
            return "❌ Error: SENDGRID_API_KEY not configured"
        
        if not config.sender_email:
            return "❌ Error: SENDER_EMAIL not configured"
        
        recipients = config.recipient_emails
        if not recipients:
            return "❌ Error: RECIPIENT_EMAILS not configured"
        
        sg = SendGridAPIClient(config.sendgrid_api_key)
        
        results = []
        for recipient in recipients:
            message = Mail(
                from_email=Email(config.sender_email),
                to_emails=To(recipient),
                subject=subject,
                html_content=Content("text/html", html_body)
            )
            
            response = sg.send(message)
            results.append(f"✅ Sent to {recipient} (Status: {response.status_code})")
        
        return "📧 Email sent successfully!\n" + "\n".join(results)
        
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"

# =============================================================================
# TOOL WRAPPERS
# =============================================================================

subject_writer_tool = subject_writer_agent.as_tool(
    tool_name="write_subject_line",
    tool_description="Generates a compelling subject line for a given email body"
)

html_converter_tool = html_converter_agent.as_tool(
    tool_name="convert_to_html",
    tool_description="Converts plain text email to formatted HTML with professional styling"
)

# Create tool wrapper for send_html_email function
from agents import function_tool

@function_tool
def send_html_email_tool(subject: str, html_body: str) -> str:
    """Sends HTML email via SendGrid to configured recipients"""
    return send_html_email(subject, html_body)

# =============================================================================
# EMAIL FORMATTER AGENT (Handoff Target)
# =============================================================================

email_formatter_agent = Agent(
    name="EmailFormatterAndSender",
    model="gpt-4o-mini",
    instructions="""
    You are an email formatting and sending specialist targeting UK estate, legal and accountancy SMBs.
    Workflow:
    1. Receive a plain-text email body
    2. Use the SubjectLineWriter tool to generate a subject line
    3. Use the HTMLEmailConverter tool to format the email into HTML
    4. Use send_html_email tool to deliver the email (to be executed in the system environment)
    5. Confirm completion at each step
    6. After sending, report the final status (e.g., "Email sent to X at Y – delivered").
    """,
    tools=[
        subject_writer_tool,
        html_converter_tool,
        send_html_email_tool
    ],
    handoff_description="Formats email to HTML and sends it to prospects"
)

# =============================================================================
# SALES MANAGER AGENT (Orchestrator)
# =============================================================================

sales_writer_1_tool = sales_writer_1.as_tool(
    tool_name="data_driven_writer",
    tool_description="Generates professional, data-driven sales emails with metrics and ROI focus"
)

sales_writer_2_tool = sales_writer_2.as_tool(
    tool_name="conversational_writer",
    tool_description="Generates warm, friendly sales emails with relatable scenarios"
)

sales_writer_3_tool = sales_writer_3.as_tool(
    tool_name="direct_writer",
    tool_description="Generates bold, action-oriented sales emails with strong CTAs"
)

sales_manager = Agent(
    name="SalesManager",
    model="gpt-4o",
    instructions="""
    You are a Sales Manager overseeing email campaign creation for UK estate, legal and accountancy SMBs exploring AI onboarding.
    Workflow:
    1. Use all three writer tools to generate email options:
    • data_driven_writer
    • conversational_writer
    • direct_writer
    2. Evaluate all three emails based on:
    • Clarity and persuasiveness
    • Tone appropriateness for cold outreach (in regulated/skeptical industries)
    • Likelihood to get a response
    • Professionalism
    3. Select the BEST email and include a brief explanation of your reasoning.
    4. Hand off the winning email to EmailFormatterAndSender agent for formatting and delivery.
    """,
    tools=[
        sales_writer_1_tool,
        sales_writer_2_tool,
        sales_writer_3_tool
    ],
    handoffs=[
        email_formatter_agent
    ]
)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def generate_emails_parallel(
    agents: List[Agent],
    prompt: str
) -> List[str]:
    """
    Generate emails from multiple agents in parallel
    
    Args:
        agents: List of agent instances
        prompt: Common prompt for all agents
    
    Returns:
        List of generated email bodies
    """
    tasks = [Runner.run(agent, prompt) for agent in agents]
    results = await asyncio.gather(*tasks)
    return [result.final_output for result in results]
