# 🤖 Sales Agent MCP Server

AI-powered multi-agent sales email generation system for Claude Desktop and Cursor.

## ✨ Features

- **🎯 Multi-Agent Generation**: 3 specialized AI agents create diverse email styles
- **🧠 Smart Selection**: AI manager evaluates and selects the best email
- **✉️ Auto-Formatting**: Converts to HTML with compelling subject lines
- **📧 SendGrid Integration**: Direct email sending to prospects
- **🔧 Zero Installation**: Works with `uvx` - no local setup needed

---

## 🚀 Quick Start (For Clients)

### Step 1: Install uvx (One-Time Setup)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell as Administrator):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation:**
```bash
uvx --version
```

---

### Step 2: Configure Claude Desktop

1. **Open Claude Desktop config file:**
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add this configuration** (replace with your API keys):
```json
{
  "mcpServers": {
    "sales-agent": {
      "command": "uvx",
      "args": ["sales-agent-mcp@latest"],
      "env": {
        "OPENAI_API_KEY": "sk-your-openai-api-key-here",
        "SENDGRID_API_KEY": "SG.your-sendgrid-api-key-here",
        "SENDER_EMAIL": "your-verified@email.com",
        "RECIPIENT_EMAILS": "prospect1@example.com,prospect2@example.com"
      }
    }
  }
}
```

3. **Restart Claude Desktop**

**That's it!** No installation, no Python, no terminal commands needed.

---

### Step 3: Configure Cursor (Optional)

1. Open Cursor Settings → **Tools & Integrations** → **New MCP Server**
2. This opens `~/.cursor/mcp.json`
3. Add the same configuration as above

---

## 💬 Usage

In Claude Desktop or Cursor, simply ask:
```
Generate a sales campaign for our AI code review tool that integrates 
with GitHub. Target audience is CTOs at Series A-B startups in fintech.
```

Claude will automatically:
1. ✅ Generate 3 different email variations
2. ✅ Evaluate and select the best one
3. ✅ Format with HTML and subject line
4. ✅ Send to your prospects via SendGrid

---

## 🔑 Getting API Keys

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

### SendGrid API Key
1. Go to https://app.sendgrid.com/settings/api_keys
2. Click "Create API Key"
3. Give it "Full Access" permission
4. Copy the key (starts with `SG.`)

### Verify Sender Email in SendGrid
1. Go to https://app.sendgrid.com/settings/sender_auth
2. Click "Verify a Single Sender"
3. Enter your email and verify

---

## 🛠️ Available Tools

### 1. `generate_sales_campaign`
Generate complete email campaign with AI evaluation.

**Example:**
```
Generate a sales campaign for [your product] targeting [your audience]
```

### 2. `send_sales_email`
Format and send email via SendGrid.

**Example:**
```
Send this email: [paste email text]
```

### 3. `generate_email_subject`
Generate compelling subject line for any email.

**Example:**
```
Generate a subject line for this email: [paste email body]
```

### 4. `convert_email_to_html`
Convert plain text to professional HTML.

**Example:**
```
Convert this email to HTML: [paste plain text]
```

---

## 🆘 Troubleshooting

**"spawn uvx ENOENT" error**

Solution: Install uvx (see Step 1 above)
Still broken?: Restart your terminal/computer after installation

**"Configuration Error" in Claude**

Solution: Double-check your API keys in the config file
Common issue: Make sure sender email is verified in SendGrid

**Emails not sending**

Solution: Verify your sender email in SendGrid settings
Check: Make sure RECIPIENT_EMAILS are valid

**"OpenAI API Key not configured"**

Solution: Check that your API key starts with sk-
Verify: Key is in Claude Desktop config under env

---

## 📝 Example Prompts

### Generate Campaign
```
Generate a sales campaign for our AI-powered code review assistant 
that catches bugs before production. Target CTOs at Series A startups 
in the fintech space who care about code quality and developer velocity.
```

### Send Custom Email
```
Send this email to prospects:

Hi {{name}},

I noticed your team is growing fast. Our AI code review tool 
helps teams like yours catch 80% of bugs before they hit production...

[rest of email]
```

### Just Get Subject Line
```
Generate a subject line for this email: [paste email body]
```

---

## 🔐 Security Notes

- **API keys are secure**: Environment variables in Claude config are local only
- **No data storage**: Server doesn't store any emails or data
- **SendGrid verified**: Only verified sender emails can be used
- **Open source**: Full code available for review

---

## 🤝 Support

Having issues? Need help?

- **GitHub Issues**: https://github.com/mmaun/sales-agent/issues
- **Email**: manny.maun@biznez.co.uk
- **Documentation**: Full docs in repository

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

Built with:
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [SendGrid](https://sendgrid.com/)

---

## 🎯 What's Next?

After successful setup, try these prompts:

1. **"Generate a sales campaign for [your product]"**
2. **"Send a follow-up email to prospects who haven't responded"**
3. **"Create 5 different subject lines for this email"**
4. **"Convert my plain text email to HTML"**

Have fun automating your sales outreach! 🚀
