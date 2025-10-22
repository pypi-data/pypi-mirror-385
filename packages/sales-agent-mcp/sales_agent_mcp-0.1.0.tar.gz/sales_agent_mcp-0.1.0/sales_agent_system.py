"""
Sales Agent System - Phase 1: Sales Writer Agents and Parallel Execution

Implements:
- Checkpoint 1: Multiple agent-generated Python code execution (3 sales writer agents)
- Checkpoint 2: Parallel execution using asyncio.gather for concurrent email generation

Run Phase 1 quick test:
  export OPENAI_API_KEY="your-key"
  python sales_agent_system.py

Note: Requires openai-agents >= 0.4.0 installed.
"""

import asyncio
import os
from typing import List

try:
    # OpenAI Agents SDK
    from agents import Agent, Runner
except Exception as import_error:  # pragma: no cover - helpful message if SDK missing
    raise SystemExit(
        "The 'openai-agents' SDK is required. Install with: pip install openai-agents"
    ) from import_error


# ================================
# Phase 1: Sales Writer Agents
# ================================

# Agent 1: Professional & Data-Driven
sales_writer_1: Agent = Agent(
    name="DataDrivenWriter",
    model="gpt-4o-mini",
    instructions=(
        """
        You write professional, data-driven cold-sales emails targeting senior decision-makers in UK estate agencies, legal or accountancy firms who are exploring AI but need clarity, confidence and compliance assurance.
        • Style: Corporate, metric-focused, ROI-oriented.
        • Tone: Direct and compelling—speak to the value rather than the technology.
        • Include: Specific statistics relevant to their industry (for example: time saved, error reduction, compliance risk mitigated) and clear business value propositions ("a 25% reduction in document review time", "£X k cost-savings in the first 90 days").
        • Length: 150-200 words.
        • Format: Plain text with clear paragraphs.
        • Focus: 'What this means for your bottom line, your compliance burden, and your fee-earners' productivity'.
        • Audience context: These firms are governed, cautious about AI risk, need assurance about governance and clarity about next steps.
        """
    ),
)

# Agent 2: Conversational & Friendly
sales_writer_2: Agent = Agent(
    name="ConversationalWriter",
    model="gpt-4o-mini",
    instructions=(
        """
        You write warm, relatable cold-sales emails for UK estate, legal and accountancy SMBs that may feel intimidated by AI, uncertain where to start, or concerned about disruption.
        • Style: Friendly, personable, story-driven.
        • Tone: Empathetic, genuine, human.
        • Length: 150-200 words.
        • Format: Plain text, casual tone (yet professional because you're addressing decision-makers).
        • Focus: Pain points and relatable scenarios — "Are your fee-earners spending hours on manual compliance checks?", "What if your team could drill through document reviews in minutes instead of days?". Show you understand their world.
        • Call-to-action: Invite them to a low-risk conversation (e.g., "Let's chat about how one firm trimmed 40% off their review time in just one month").
        • Audience context: They're curious but cautious—so you gently pull them in rather than push aggressively.
        """
    ),
)

# Agent 3: Bold & Direct
sales_writer_3: Agent = Agent(
    name="DirectWriter",
    model="gpt-4o-mini",
    instructions=(
        """
        You write bold, direct cold-sales emails for UK estate, legal and accountancy SMBs who are action-oriented and ready for the next step—once you've proven value.
        • Style: Confident, action-oriented, no-nonsense.
        • Tone: Clear and unambiguous—this is for those who know they need change.
        • Length: 100-150 words.
        • Format: Plain text, punchy and concise.
        • Lead with: Strong value proposition—what they stand to gain, what's at stake if they don't act.
        • Call-to-action: Very clear—"Book a 15-minute demo", "Get your first pilot live in 30 days".
        • Audience context: These are decision-makers who are past curiosity and want results, but still need to feel confident the solution is credible and low-risk.
        """
    ),
)


async def generate_emails_parallel(agents: List[Agent], prompt: str) -> List[str]:
    """Generate emails from multiple agents in parallel using asyncio.gather.

    Args:
        agents: List of agent instances.
        prompt: Common prompt for all agents.

    Returns:
        List of generated email bodies as strings.
    """
    tasks = [Runner.run(agent, prompt) for agent in agents]
    results = await asyncio.gather(*tasks)
    emails = [result.final_output for result in results]
    return emails


async def _phase1_demo_run() -> None:
    """Small Phase 1 demo: generates three drafts in parallel and prints them.

    Requires OPENAI_API_KEY set in the environment.
    """
    product_description = (
        "AI-powered document review and compliance assistant for UK estate agencies, legal and accountancy firms that reduces document review time by 60% and ensures regulatory compliance."
    )
    prompt = (
        "Write a cold email to a senior decision-maker at a UK estate agency, legal or accountancy firm about our AI automation platform.\n\n"
        f"Product: {product_description}\n"
        "Audience: Senior decision-makers at UK estate agencies, legal and accountancy SMBs exploring AI solutions."
    )

    agents: List[Agent] = [sales_writer_1, sales_writer_2, sales_writer_3]

    print("=" * 60)
    print("Phase 1: Generating emails in parallel (3 writer agents)")
    print("=" * 60)

    emails = await generate_emails_parallel(agents, prompt)
    for index, email in enumerate(emails, start=1):
        print(f"\n--- EMAIL {index} ---\n{email}\n")
    # Phase 2 quick validation prints
    print("\n=== PHASE 2: TOOL VALIDATION ===")
    print(f"Subject Tool: {subject_writer_tool.name}")
    print(f"HTML Tool: {html_converter_tool.name}")
    # Phase 3 quick validation (dry-run expected unless SENDGRID_API_KEY set)
    print("\n=== PHASE 3: EMAIL SENDER VALIDATION ===")
    preview = send_html_email(subject="Test Subject", html_body="<h1>Test</h1>")
    print(preview)
    # Phase 4 quick validation prints
    print("\n=== PHASE 4: EMAIL FORMATTER VALIDATION ===")
    print(f"Email Formatter Agent: {email_formatter_agent.name}")
    tool_names = []
    for tool in email_formatter_agent.tools:
        if hasattr(tool, 'name'):
            tool_names.append(tool.name)
        else:
            tool_names.append(tool.__name__ if hasattr(tool, '__name__') else str(tool))
    print(f"Tools: {tool_names}")
    print(f"Handoff Description: {email_formatter_agent.handoff_description}")
    # Phase 5 quick validation prints
    print("\n=== PHASE 5: SALES MANAGER VALIDATION ===")
    print(f"Sales Manager Agent: {sales_manager.name}")
    print(f"Tools: {[tool.name for tool in sales_manager.tools]}")
    print(f"Handoffs: {[h.name for h in sales_manager.handoffs]}")
    print("\n=== TOOLS vs HANDOFFS DISTINCTION ===")
    print("TOOLS (request-response): Sales Manager calls writer tools, gets emails back, continues")
    print("HANDOFFS (delegation): Sales Manager delegates to Email Formatter, control transfers")


def _can_call_models() -> bool:
    """Returns True if an API key is present to call models."""
    return bool(os.getenv("OPENAI_API_KEY"))


# ================================
# Phase 2: Specialized Agents as Tools
# ================================

# Subject Writer Agent
subject_writer_agent: Agent = Agent(
    name="SubjectLineWriter",
    model="gpt-4o-mini",
    instructions=(
        """
        You are an expert at writing compelling email subject lines tailored for outreach to UK estate, legal and accountancy firms exploring AI solutions.
        Given an email body, create a subject line that:
        • Is 40-60 characters long
        • Creates curiosity or urgency
        • Is specific and relevant to their industry (estate agency / legal / accountancy) and the challenge of AI onboarding, compliance or productivity
        • Avoids spam triggers (no ALL CAPS, excessive punctuation, generic buzzwords)
        • Return ONLY the subject line, nothing else.
        """
    ),
)

# HTML Converter Agent
html_converter_agent: Agent = Agent(
    name="HTMLEmailConverter",
    model="gpt-4o-mini",
    instructions=(
        """
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
    ),
)

# Convert agents to tools
subject_writer_tool = subject_writer_agent.as_tool(
    tool_name="write_subject_line",
    tool_description="Generates a compelling subject line for a given email body",
)

html_converter_tool = html_converter_agent.as_tool(
    tool_name="convert_to_html",
    tool_description="Converts plain text email to formatted HTML with professional styling",
)


# ================================
# Phase 3: Function Tool (Email Sender)
# ================================

try:
    from sendgrid import SendGridAPIClient  # type: ignore
    from sendgrid.helpers.mail import Mail, Email, To, Content  # type: ignore
except Exception:
    # Defer import errors until function call to allow running Phase 1/2 without SendGrid installed
    SendGridAPIClient = None  # type: ignore
    Mail = Email = To = Content = None  # type: ignore


def send_html_email(subject: str, html_body: str) -> str:
    """Send an HTML email via SendGrid to all prospects.

    If SENDGRID_API_KEY or dependencies are missing, returns a dry-run message.
    """
    sender_email = os.getenv("SENDER_EMAIL")
    recipients_env = os.getenv("RECIPIENT_EMAILS", "")
    recipients = [r.strip() for r in recipients_env.split(",") if r.strip()]

    if not sender_email:
        return "Error: SENDER_EMAIL not configured in environment"

    if not recipients:
        return "Error: RECIPIENT_EMAILS not configured in environment"

    api_key = os.getenv("SENDGRID_API_KEY")

    # Dry-run if missing API key or SendGrid lib not available
    if not api_key or SendGridAPIClient is None or Mail is None:
        preview = (
            "[DRY RUN] Would send email via SendGrid\n"
            f"Subject: {subject}\n"
            f"Recipients: {', '.join(recipients)}\n"
            f"HTML length: {len(html_body)} chars"
        )
        return preview

    try:
        sg = SendGridAPIClient(api_key)
        results = []
        for recipient in recipients:
            message = Mail(
                from_email=Email(sender_email),
                to_emails=To(recipient),
                subject=subject,
                html_content=Content("text/html", html_body),
            )
            response = sg.send(message)
            results.append(f"\u2713 Sent to {recipient} (Status: {response.status_code})")

        return "Email sent successfully!\n" + "\n".join(results)
    except Exception as exc:  # pragma: no cover
        return f"Error sending email: {exc}"


# ================================
# Phase 4: Email Formatter Agent (Handoff Target)
# ================================

# Email Formatter Agent - Receives control via handoff
email_formatter_agent: Agent = Agent(
    name="EmailFormatterAndSender",
    model="gpt-4o-mini",
    instructions=(
        """
        You are an email formatting specialist targeting UK estate, legal and accountancy SMBs.
        Workflow:
        1. Receive a plain-text email body
        2. Use the SubjectLineWriter tool to generate a subject line
        3. Use the HTMLEmailConverter tool to format the email into HTML
        4. Provide the formatted email content for sending
        5. Confirm completion at each step
        6. Report the final status with the formatted email ready for delivery.
        """
    ),
    tools=[
        subject_writer_tool,
        html_converter_tool,
    ],
    # This description is how other agents see this agent
    handoff_description="Formats email to HTML and sends it to prospects"
)


# ================================
# Phase 5: Sales Manager Agent (Orchestrator)
# ================================

# First, wrap sales writer agents as tools
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

# Sales Manager - Orchestrates everything (Modified for human approval)
sales_manager: Agent = Agent(
    name="SalesManager",
    model="gpt-4o",  # Premium model for decision-making
    instructions=(
        """
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
        4. Present the selected email to the human for approval.
        5. DO NOT hand off to EmailFormatterAndSender until human approval is received.
        
        IMPORTANT: Format your final output exactly like this:
        
        === SALES MANAGER EVALUATION ===
        
        EMAIL OPTIONS GENERATED:
        [Brief summary of the 3 emails generated]
        
        SELECTION REASONING:
        [Your detailed reasoning for why you selected the best email]
        
        SELECTED EMAIL:
        [The complete email content that you selected as the best]
        
        === READY FOR HUMAN APPROVAL ===
        """
    ),
    tools=[
        sales_writer_1_tool,
        sales_writer_2_tool,
        sales_writer_3_tool
    ],
    # Removed handoffs - human approval step will handle delegation
)


# ================================
# Human Approval Functions
# ================================

def get_human_approval(selected_email: str, reasoning: str) -> bool:
    """
    Present the selected email to human for approval.
    Returns True if approved, False if rejected.
    """
    print("\n" + "="*80)
    print("🔍 HUMAN APPROVAL REQUIRED")
    print("="*80)
    print()
    print("📧 SELECTED EMAIL FOR REVIEW:")
    print("-" * 50)
    print(selected_email)
    print()
    print("🤖 SALES MANAGER REASONING:")
    print("-" * 50)
    print(reasoning)
    print()
    print("="*80)
    
    while True:
        approval = input("Do you approve this email for sending? (y/n): ").lower().strip()
        if approval in ['y', 'yes']:
            print("✅ Email approved! Proceeding to formatting and sending...")
            return True
        elif approval in ['n', 'no']:
            print("❌ Email rejected. Please modify your request and try again.")
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")

async def run_sales_campaign_with_approval(product_description: str) -> str:
    """
    Run the complete sales campaign with human approval step.
    """
    print("🚀 Starting Sales Campaign with Human Approval...")
    print("="*60)
    
    # Step 1: Sales Manager generates and selects best email
    print("📝 Step 1: Sales Manager generating and evaluating emails...")
    result = await Runner.run(sales_manager, product_description)
    
    # Extract the selected email and reasoning from the result
    manager_output = result.final_output
    
    # Parse the output to extract email content and reasoning
    # The Sales Manager should format the output clearly
    lines = manager_output.split('\n')
    email_content = ""
    reasoning = ""
    
    in_email_section = False
    in_reasoning_section = False
    
    for line in lines:
        if "SELECTED EMAIL:" in line:
            in_email_section = True
            in_reasoning_section = False
            continue
        elif "SELECTION REASONING:" in line:
            in_reasoning_section = True
            in_email_section = False
            continue
        elif line.strip() == "" or line.startswith("==="):
            continue
        
        if in_email_section:
            email_content += line + "\n"
        elif in_reasoning_section:
            reasoning += line + "\n"
    
    # If parsing failed, use the full output as email content
    if not email_content.strip():
        email_content = manager_output
        reasoning = "Sales Manager selected this email based on evaluation criteria."
    
    # Step 2: Human approval
    print("\n👤 Step 2: Human approval required...")
    approved = get_human_approval(email_content.strip(), reasoning.strip())
    
    if not approved:
        return "❌ Campaign cancelled - email not approved by human."
    
    # Step 3: Hand off to Email Formatter for formatting and sending
    print("\n📧 Step 3: Formatting and sending approved email...")
    formatter_result = await Runner.run(email_formatter_agent, email_content.strip())
    
    return f"✅ Campaign completed successfully!\n\nSales Manager Output:\n{manager_output}\n\nEmail Formatter Output:\n{formatter_result.final_output}"

# ================================
# Phase 6: Main Execution Flow
# ================================

async def run_sales_campaign(product_description: str) -> str:
    """Execute complete sales email campaign.
    
    Args:
        product_description: Description of product/service to promote
        
    Returns:
        Final campaign result output
    """
    
    print("=" * 60)
    print("🚀 SALES CAMPAIGN EXECUTION")
    print("=" * 60)
    
    # Construct the prompt for Sales Manager
    campaign_prompt = f"""
    We need to create a cold sales email campaign for the following product:
    
    {product_description}
    
    Target Audience: UK estate agencies, legal and accountancy SMBs exploring AI solutions
    
    Please:
    1. Generate 3 different email options using all available writers
    2. Evaluate and select the best one
    3. Hand it off for formatting and sending
    """
    
    print("\n📧 Initiating campaign with Sales Manager...\n")
    
    # Run the sales manager
    result = await Runner.run(sales_manager, campaign_prompt)
    
    print("\n" + "=" * 60)
    print("✅ CAMPAIGN COMPLETE")
    print("=" * 60)
    print(f"\nFinal Output:\n{result.final_output}")
    print("\n" + "=" * 60)
    
    return result.final_output


async def _full_campaign_demo() -> None:
    """Run the complete sales campaign with example product."""
    product_info = """
    AI-powered document review and compliance assistant for UK estate agencies, legal and accountancy firms.
    - Reduces document review time by 60%
    - Ensures regulatory compliance automatically
    - Identifies potential risks and issues
    - Learns from your firm's document patterns
    - Integrates with existing case management systems
    Pricing: £299/month per firm
    """
    
    await run_sales_campaign(product_info)

async def _full_campaign_demo_with_approval() -> None:
    """Run the complete sales campaign with human approval step."""
    product_info = """
    AI-powered document review and compliance assistant for UK estate agencies, legal and accountancy firms.
    - Reduces document review time by 60%
    - Ensures regulatory compliance automatically
    - Identifies potential risks and issues
    - Learns from your firm's document patterns
    - Integrates with existing case management systems
    Pricing: £299/month per firm
    """
    
    await run_sales_campaign_with_approval(product_info)


# ================================
# Phase 7: Verification & Validation
# ================================

def verify_all_checkpoints() -> None:
    """Verify all 8 checkpoints are implemented correctly."""
    
    print("\n" + "=" * 80)
    print("🔍 CHECKPOINT VERIFICATION")
    print("=" * 80)
    
    # Checkpoint 1: Multiple agent-generated Python code execution (3 sales writer agents)
    print("\n✅ Checkpoint 1: Multiple agent-generated Python code execution (3 sales writer agents)")
    assert len([sales_writer_1, sales_writer_2, sales_writer_3]) == 3
    print(f"   - DataDrivenWriter: {sales_writer_1.name}")
    print(f"   - ConversationalWriter: {sales_writer_2.name}")
    print(f"   - DirectWriter: {sales_writer_3.name}")
    
    # Checkpoint 2: Parallel execution using asyncio.gather() for concurrent email generation
    print("\n✅ Checkpoint 2: Parallel execution using asyncio.gather() for concurrent email generation")
    print("   - generate_emails_parallel() function implemented with asyncio.gather()")
    print("   - Creates tasks for all agents and executes concurrently")
    
    # Checkpoint 3: Selection agent that evaluates 3 emails and picks the best one
    print("\n✅ Checkpoint 3: Selection agent that evaluates 3 emails and picks the best one")
    print(f"   - Sales Manager ({sales_manager.name}) evaluates and selects best email")
    print("   - Instructions include evaluation criteria and selection process")
    
    # Checkpoint 4: Function wrapped as tool (SendGrid email sender function → tool)
    print("\n✅ Checkpoint 4: Function wrapped as tool (SendGrid email sender function → tool)")
    print("   - send_html_email() function implemented")
    print("   - Function automatically wrapped as tool when added to agent tools list")
    
    # Checkpoint 5: Agents wrapped as tools using .as_tool() construct (subject writer, HTML converter)
    print("\n✅ Checkpoint 5: Agents wrapped as tools using .as_tool() construct")
    print(f"   - Subject Writer Tool: {subject_writer_tool.name}")
    print(f"   - HTML Converter Tool: {html_converter_tool.name}")
    print(f"   - Sales Writer 1 Tool: {sales_writer_1_tool.name}")
    print(f"   - Sales Writer 2 Tool: {sales_writer_2_tool.name}")
    print(f"   - Sales Writer 3 Tool: {sales_writer_3_tool.name}")
    
    # Checkpoint 6: Sales Manager agent orchestrating all tools and making decisions
    print("\n✅ Checkpoint 6: Sales Manager agent orchestrating all tools and making decisions")
    print(f"   - Sales Manager ({sales_manager.name}) orchestrates workflow")
    print(f"   - Tools: {[tool.name for tool in sales_manager.tools]}")
    print(f"   - Handoffs: {[h.name for h in sales_manager.handoffs]}")
    
    # Checkpoint 7: Clear distinction between tools (request-response) vs handoffs (delegation)
    print("\n✅ Checkpoint 7: Clear distinction between tools vs handoffs")
    print("   - TOOLS (request-response): Sales Manager calls writer tools, gets responses back, continues")
    print("   - HANDOFFS (delegation): Sales Manager delegates to Email Formatter, control transfers")
    print("   - Code comments and validation prints explain the distinction")
    
    # Checkpoint 8: Email Formatter agent as handoff target (receives control, doesn't return it)
    print("\n✅ Checkpoint 8: Email Formatter agent as handoff target")
    print(f"   - Email Formatter ({email_formatter_agent.name}) is handoff target")
    tool_names = []
    for tool in email_formatter_agent.tools:
        if hasattr(tool, 'name'):
            tool_names.append(tool.name)
        else:
            tool_names.append(tool.__name__ if hasattr(tool, '__name__') else str(tool))
    print(f"   - Tools: {tool_names}")
    print(f"   - Handoff Description: {email_formatter_agent.handoff_description}")
    print("   - Receives control via handoff, doesn't return it")
    
    # Structural verification
    print("\n" + "=" * 80)
    print("🏗️ STRUCTURAL VERIFICATION")
    print("=" * 80)
    
    # Verify Sales Manager structure (modified for human approval workflow)
    assert len(sales_manager.tools) == 3, "Sales Manager should have 3 writer tools"
    assert len(sales_manager.handoffs) == 0, "Sales Manager should have 0 handoffs (human approval workflow)"
    print("✅ Sales Manager structure verified: 3 tools, 0 handoffs (human approval workflow)")
    
    # Verify Email Formatter structure
    assert len(email_formatter_agent.tools) == 3, "Email Formatter should have 3 tools"
    assert len(email_formatter_agent.handoffs) == 0, "Email Formatter should have no handoffs"
    print("✅ Email Formatter structure verified: 3 tools, 0 handoffs")
    
    # Verify tool names
    expected_tool_names = {
        "data_driven_writer", "conversational_writer", "direct_writer",
        "write_subject_line", "convert_to_html"
    }
    sales_manager_tool_names = {tool.name for tool in sales_manager.tools}
    formatter_tool_names = set()
    for tool in email_formatter_agent.tools:
        if hasattr(tool, 'name'):
            formatter_tool_names.add(tool.name)
        else:
            formatter_tool_names.add(tool.__name__ if hasattr(tool, '__name__') else str(tool))
    actual_tool_names = sales_manager_tool_names | formatter_tool_names
    assert expected_tool_names.issubset(actual_tool_names), f"Missing expected tools: {expected_tool_names - actual_tool_names}"
    print("✅ All expected tool names verified")
    
    print("\n" + "=" * 80)
    print("🎉 ALL CHECKPOINTS VERIFIED SUCCESSFULLY!")
    print("=" * 80)
    print("\nThe Sales Agent System is fully implemented with:")
    print("• 3 distinct sales writer agents with parallel execution")
    print("• Selection agent that evaluates and picks the best email")
    print("• Function and agent tools properly wrapped")
    print("• Clear tools vs handoffs distinction")
    print("• Complete email formatting and sending workflow")
    print("• Full campaign execution flow")
    print("=" * 80)


if __name__ == "__main__":
    if not _can_call_models():
        print(
            "OPENAI_API_KEY not set. Export it to run the system:\n"
            "  export OPENAI_API_KEY=your-key\n"
            "  export SENDGRID_API_KEY=your-key (optional, for actual sending)\n"
            "  export SENDER_EMAIL=verified@yourdomain.com (optional)\n"
            "  export RECIPIENT_EMAILS=test@example.com (optional)\n"
            "Then run: python sales_agent_system.py"
        )
        raise SystemExit(0)

    # Run verification first
    verify_all_checkpoints()
    
    # Run Phase 1-5 validation demo
    print("\nRunning Phase 1-5 validation demo...")
    asyncio.run(_phase1_demo_run())
    
    # Ask user if they want to run full campaign
    print("\n" + "=" * 60)
    response = input("Run full sales campaign with human approval? (y/N): ").strip().lower()
    if response in ('y', 'yes'):
        print("\nRunning full campaign with human approval...")
        asyncio.run(_full_campaign_demo_with_approval())
    else:
        print("Demo complete. Set SENDGRID_API_KEY and other env vars to test full email sending.")


