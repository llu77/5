# MCP (Model Context Protocol) Integration Examples

Use Claude with MCP servers for enhanced capabilities like filesystem access, database queries, git operations, Cloudflare analytics, and data lake queries.

## 📁 What's Here

- **`claude_with_mcp.py`** - Basic MCP integration examples
- **`advanced_mcp_examples.py`** - Cloudflare & Iceberg integration
- **`mcp_config.json`** - Complete MCP server configuration
- **`ADVANCED_MCP_SETUP.md`** - Setup guide for advanced servers
- **`requirements.txt`** - Python dependencies

## 🚀 Quick Start

```bash
# 1. Install MCP servers
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-sqlite

# 2. Set API key
export ANTHROPIC_API_KEY=sk-ant-your-key

# 3. Run examples
python claude_with_mcp.py
```

## 🔌 Available MCP Servers

### Basic Servers

**Filesystem**
Access local files and directories.

```json
{
  "filesystem": {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-filesystem"],
    "env": {
      "ALLOWED_PATHS": "/Users/me/projects"
    }
  }
}
```

### Git
Repository operations and history analysis.

```json
{
  "git": {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-git"],
    "env": {
      "GIT_REPOS": "/Users/me/projects"
    }
  }
}
```

### SQLite
Database queries and schema analysis.

```json
{
  "sqlite": {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-sqlite"],
    "env": {
      "DATABASE_PATH": "/Users/me/data/app.db"
    }
  }
}
```

### PostgreSQL
PostgreSQL database access.

```json
{
  "postgres": {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-postgres"],
    "env": {
      "DATABASE_URL": "postgresql://user:pass@localhost:5432/db"
    }
  }
}
```

### Advanced Servers

**Cloudflare Observability**
Access Cloudflare analytics and monitoring data.

```json
{
  "cloudflare-observability": {
    "command": "npx",
    "args": ["mcp-remote", "https://observability.mcp.cloudflare.com/mcp"],
    "env": {}
  }
}
```

**Cloudflare Bindings**
Interact with Cloudflare Workers bindings (KV, D1, R2).

```json
{
  "cloudflare-bindings": {
    "command": "npx",
    "args": ["mcp-remote", "https://bindings.mcp.cloudflare.com/mcp"],
    "env": {}
  }
}
```

**Apache Iceberg Data Lake**
Query Iceberg tables via Impala for data analytics.

```json
{
  "iceberg": {
    "command": "uvx",
    "args": ["git+https://github.com/cloudera/iceberg-mcp-server@main"],
    "env": {
      "IMPALA_HOST": "your-impala-host",
      "IMPALA_PORT": "21050",
      "IMPALA_USER": "username",
      "IMPALA_PASSWORD": "password",
      "IMPALA_DATABASE": "default"
    }
  }
}
```

See `ADVANCED_MCP_SETUP.md` for detailed setup instructions.

## 💻 Usage Examples

### Example 1: Analyze Files

```python
from claude_with_mcp import ClaudeMCPClient

client = ClaudeMCPClient()

# Configure filesystem access
client.configure_mcp_server("filesystem", {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-filesystem"],
    "env": {"ALLOWED_PATHS": "/Users/me/projects"}
})

# Analyze files
result = client.analyze_files(
    query="What is the architecture?",
    file_paths=["app/main.py", "app/models.py"],
    enable_thinking=True
)

print(result["text"])
```

### Example 2: Search Code

```python
# Search for security issues
result = client.code_search(
    query="Find SQL injection vulnerabilities",
    directory="/Users/me/projects/app",
    file_pattern="*.py"
)

print(result["text"])
```

### Example 3: Database Analysis

```python
# Configure database
client.configure_mcp_server("sqlite", {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-sqlite"],
    "env": {"DATABASE_PATH": "/path/to/db.sqlite"}
})

# Analyze schema
result = client.chat(
    message="Analyze database schema and suggest optimizations",
    system="You have database access. Provide recommendations.",
    enable_thinking=True
)
```

### Example 4: Git Analysis

```python
# Configure git
client.configure_mcp_server("git", {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-git"],
    "env": {"GIT_REPOS": "/Users/me/projects"}
})

# Analyze commits
result = client.chat(
    message="Show me the most frequently changed files",
    system="You have git access. Analyze repository."
)
```

## 🎯 Use Cases

### Code Analysis
- Security audits
- Architecture review
- Code quality assessment
- Refactoring suggestions

### Documentation
- Auto-generate README
- API documentation
- Architecture diagrams
- Setup instructions

### Database Operations
- Schema analysis
- Query optimization
- Data migration planning
- Performance tuning

### Git Operations
- Commit history analysis
- Code change tracking
- Contributor statistics
- Branch comparisons

## 🔧 Configuration

Edit `mcp_config.json` to configure your MCP servers:

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

**Important:** Set `ALLOWED_PATHS` to only directories you want Claude to access.

## 🐛 Troubleshooting

### MCP server not found
```bash
# Install globally
npm install -g @modelcontextprotocol/server-filesystem

# Verify
npx @modelcontextprotocol/server-filesystem --version
```

### Permission denied
```json
{
  "env": {
    "ALLOWED_PATHS": "/correct/accessible/path"
  }
}
```

### API errors
```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Set if missing
export ANTHROPIC_API_KEY=sk-ant-your-key
```

## 📚 Resources

- [Model Context Protocol Spec](https://modelcontextprotocol.io/)
- [MCP Servers](https://github.com/modelcontextprotocol/servers)
- [Anthropic MCP Docs](https://docs.anthropic.com/en/docs/build-with-claude/mcp)

See `README_FLY_MCP.md` for comprehensive documentation.
