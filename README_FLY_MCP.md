# Fly.io Deployment & MCP Integration

Deploy Claude AI applications to Fly.io and integrate with Model Context Protocol (MCP) servers for enhanced capabilities.

## 📚 What's Included

### 1. **Fly.io Deployment** (`fly-examples/`)
Production-ready Flask applications for Fly.io deployment with automatic scaling and global distribution.

### 2. **MCP Integration** (`mcp-examples/`)
Claude integration with Model Context Protocol servers for filesystem, database, git, and more.

---

## 🚀 Fly.io Deployment

### What is Fly.io?

Fly.io is a platform for running full-stack apps globally with automatic scaling, edge deployment, and zero-configuration deployment.

**Key Features:**
- ✅ Global edge deployment
- ✅ Automatic HTTPS
- ✅ Zero-downtime deployments
- ✅ Auto-scaling and auto-stopping
- ✅ Built-in health checks
- ✅ Free tier available

### Quick Start

**Prerequisites:**
- Fly.io account (sign up at https://fly.io)
- flyctl CLI installed

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Authenticate
fly auth login

# Set your Fly.io token (already provided to you)
export FLY_API_TOKEN="FlyV1 fm2_lJPECAAAAAAACt3txBBzORMVURNOLhllVqnZS6rTwrVodHRwczovL2FwaS5mbHkuaW8vdjGUAJLOABRgAx8Lk7lodHRwczovL2FwaS5mbHkuaW8vYWFhL3Yx..."
```

### Deploy Thinking Agent

```bash
cd fly-examples

# Create Fly.io app
fly launch --name thinking-agent --region sjc

# Set secrets
fly secrets set ANTHROPIC_API_KEY=sk-ant-your-key

# Deploy
fly deploy

# Your app is live!
# https://thinking-agent.fly.dev
```

### Test Deployed App

```bash
# Health check
curl https://thinking-agent.fly.dev/health

# Extended thinking
curl -X POST https://thinking-agent.fly.dev/think \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Explain how machine learning works",
    "thinking_budget": 3000,
    "domain": "code"
  }'

# Quick analysis
curl -X POST https://thinking-agent.fly.dev/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What does this code do?",
    "context": "def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)"
  }'
```

### Configuration

**`fly.toml`** - Fly.io configuration:

```toml
app = "thinking-agent"
primary_region = "sjc"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  memory = "512mb"
  cpu_kind = "shared"
  cpus = 1
```

### Scaling

```bash
# Manual scaling
fly scale count 3  # Run 3 instances

# Increase memory
fly scale memory 1024  # 1GB per instance

# Add more regions
fly regions add lax iad  # Los Angeles, Virginia

# Auto-scale based on load
fly autoscale set min=1 max=10
```

### Monitoring

```bash
# View logs
fly logs

# SSH into machine
fly ssh console

# Check status
fly status

# View metrics
fly dashboard
```

---

## 🔌 MCP (Model Context Protocol) Integration

### What is MCP?

Model Context Protocol allows Claude to interact with external tools and data sources like filesystems, databases, APIs, and more.

**Available MCP Servers:**
- ✅ **Filesystem** - Read/write files
- ✅ **Git** - Repository operations
- ✅ **SQLite** - Database queries
- ✅ **PostgreSQL** - Database access
- ✅ **Puppeteer** - Web automation
- ✅ **Slack** - Slack integration

### Configuration

**`mcp_config.json`** - Configure MCP servers:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_PATHS": "/Users/me/projects"
      }
    }
  }
}
```

### Usage Examples

#### Example 1: Filesystem Analysis

```python
from claude_with_mcp import ClaudeMCPClient

# Initialize client
client = ClaudeMCPClient()

# Configure filesystem access
client.configure_mcp_server("filesystem", {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-filesystem"],
    "env": {
        "ALLOWED_PATHS": "/Users/me/projects"
    }
})

# Analyze files
result = client.analyze_files(
    query="What is the architecture of this codebase?",
    file_paths=[
        "/Users/me/projects/app/main.py",
        "/Users/me/projects/app/models.py"
    ],
    enable_thinking=True
)

print(result["text"])
```

#### Example 2: Code Search

```python
# Search for security vulnerabilities
result = client.code_search(
    query="Find potential SQL injection vulnerabilities",
    directory="/Users/me/projects/app",
    file_pattern="*.py"
)

print(result["text"])
```

#### Example 3: Database Analysis

```python
# Configure database MCP server
client.configure_mcp_server("sqlite", {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-sqlite"],
    "env": {
        "DATABASE_PATH": "/Users/me/data/app.db"
    }
})

# Query and analyze database
result = client.chat(
    message="Analyze the database schema and suggest optimizations",
    system="You have database access via MCP. Analyze and provide recommendations.",
    enable_thinking=True
)
```

#### Example 4: Git Operations

```python
# Configure git MCP server
client.configure_mcp_server("git", {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-git"],
    "env": {
        "GIT_REPOS": "/Users/me/projects"
    }
})

# Analyze git history
result = client.chat(
    message="Analyze the git history and identify the most changed files",
    system="You have git access. Analyze repository history."
)
```

### MCP Server Setup

**Install MCP servers:**

```bash
# Filesystem server
npm install -g @modelcontextprotocol/server-filesystem

# Git server
npm install -g @modelcontextprotocol/server-git

# SQLite server
npm install -g @modelcontextprotocol/server-sqlite

# PostgreSQL server
npm install -g @modelcontextprotocol/server-postgres

# Puppeteer server
npm install -g @modelcontextprotocol/server-puppeteer
```

---

## 🔄 Integration: Fly.io + MCP

Combine Fly.io deployment with MCP capabilities:

```python
# app.py - Flask app on Fly.io with MCP
from flask import Flask, request, jsonify
from claude_with_mcp import ClaudeMCPClient

app = Flask(__name__)
mcp_client = ClaudeMCPClient()

# Configure MCP on startup
mcp_client.configure_mcp_server("filesystem", {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-filesystem"],
    "env": {
        "ALLOWED_PATHS": "/app/data"
    }
})

@app.route("/analyze-code", methods=["POST"])
def analyze_code():
    data = request.json
    directory = data.get("directory", "/app/data")
    query = data.get("query", "Analyze this code")

    result = mcp_client.code_search(
        query=query,
        directory=directory,
        file_pattern="*.py"
    )

    return jsonify(result)

# Deploy to Fly.io
# fly deploy
```

---

## 📊 Comparison: Deployment Options

| Feature | Fly.io | Modal | Cloudflare |
|---------|--------|-------|------------|
| **Language** | Any (Docker) | Python | JavaScript/TS |
| **Edge Deploy** | Global regions | Global | Global edge |
| **Auto-scale** | Yes | Yes | Yes |
| **MCP Support** | Yes | Limited | Limited |
| **Free Tier** | Yes | Yes | Yes |
| **Cold Start** | ~1-2s | ~1-2s | <100ms |
| **Best For** | Full-stack apps | Python ML | Edge functions |

---

## 🎯 Use Cases

### Use Case 1: Code Analysis Service

Deploy a code analysis service that uses MCP to read repositories:

```python
# Deployed on Fly.io
@app.route("/audit", methods=["POST"])
def security_audit():
    repo_path = request.json["repository"]

    client = ClaudeMCPClient()
    client.configure_mcp_server("filesystem", {
        "command": "npx",
        "args": ["@modelcontextprotocol/server-filesystem"],
        "env": {"ALLOWED_PATHS": repo_path}
    })

    result = client.code_search(
        query="Find security vulnerabilities (SQL injection, XSS, etc.)",
        directory=repo_path,
        file_pattern="*.py"
    )

    return jsonify(result)
```

### Use Case 2: Documentation Generator

Automatically generate docs from codebases:

```python
@app.route("/generate-docs", methods=["POST"])
def generate_docs():
    project_path = request.json["project"]

    result = mcp_client.chat(
        message=f"Generate comprehensive documentation for {project_path}",
        system="Read codebase via filesystem MCP and generate docs",
        enable_thinking=True
    )

    return jsonify({"documentation": result["text"]})
```

### Use Case 3: Database Analyzer

Analyze and optimize database schemas:

```python
@app.route("/optimize-db", methods=["POST"])
def optimize_database():
    db_path = request.json["database"]

    client.configure_mcp_server("sqlite", {
        "command": "npx",
        "args": ["@modelcontextprotocol/server-sqlite"],
        "env": {"DATABASE_PATH": db_path}
    })

    result = client.chat(
        message="Analyze schema and suggest optimizations with indexes",
        enable_thinking=True
    )

    return jsonify(result)
```

---

## 🐛 Troubleshooting

### Fly.io Issues

**Issue: Deploy fails**
```bash
# Check logs
fly logs

# Validate fly.toml
fly config validate

# Force rebuild
fly deploy --force-dockerfile
```

**Issue: App not starting**
```bash
# Check health
fly checks list

# View machine status
fly machine list

# Restart
fly machine restart
```

**Issue: Secrets not set**
```bash
# List secrets
fly secrets list

# Set secret
fly secrets set ANTHROPIC_API_KEY=your-key
```

### MCP Issues

**Issue: MCP server not found**
```bash
# Install globally
npm install -g @modelcontextprotocol/server-filesystem

# Check installation
npx @modelcontextprotocol/server-filesystem --version
```

**Issue: Permission denied**
```json
{
  "env": {
    "ALLOWED_PATHS": "/correct/path/here"
  }
}
```

**Issue: MCP beta header**
```python
# Ensure beta header is set
extra_headers={"anthropic-beta": "mcp-client-2025-04-04"}
```

---

## 📚 Resources

**Fly.io:**
- [Fly.io Documentation](https://fly.io/docs/)
- [Fly.io Python Guide](https://fly.io/docs/languages-and-frameworks/python/)
- [flyctl Reference](https://fly.io/docs/flyctl/)

**MCP:**
- [Model Context Protocol Spec](https://modelcontextprotocol.io/)
- [MCP Servers](https://github.com/modelcontextprotocol/servers)
- [Anthropic MCP Docs](https://docs.anthropic.com/en/docs/build-with-claude/mcp)

**This Repository:**
- `README_MODAL.md` - Modal serverless integration
- `README_CLOUDFLARE_SANDBOX.md` - Cloudflare Sandbox integration
- `README_THINKING_TOOLS.md` - Extended thinking patterns

---

## 🎯 Next Steps

1. **Deploy to Fly.io:**
   ```bash
   cd fly-examples
   fly launch
   fly secrets set ANTHROPIC_API_KEY=your-key
   fly deploy
   ```

2. **Set up MCP:**
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   python mcp-examples/claude_with_mcp.py
   ```

3. **Combine both:**
   - Deploy MCP-enabled app to Fly.io
   - Use filesystem/database MCP servers
   - Build production services

4. **Monitor and scale:**
   - `fly logs` - View logs
   - `fly dashboard` - Web dashboard
   - `fly autoscale` - Configure scaling

---

**Deploy globally with MCP! 🌍🔌**
