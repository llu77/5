# Advanced MCP Server Setup Guide

Setup guide for Cloudflare and Iceberg MCP servers.

## 🌐 Cloudflare MCP Servers

### Cloudflare Observability

Access Cloudflare analytics, metrics, and observability data.

**Configuration:**
```json
{
  "cloudflare-observability": {
    "command": "npx",
    "args": ["mcp-remote", "https://observability.mcp.cloudflare.com/mcp"],
    "env": {}
  }
}
```

**Prerequisites:**
- Cloudflare account
- Cloudflare API token with Analytics Read permissions

**Capabilities:**
- Query traffic analytics
- Access cache metrics
- Review error rates
- Analyze performance data
- Geographic distribution insights

**Example Usage:**
```python
from advanced_mcp_examples import AdvancedMCPClient

client = AdvancedMCPClient()
client.configure_cloudflare_observability()

result = client.chat(
    message="Show top 10 countries by traffic and cache hit rates",
    system="You have Cloudflare observability access."
)
```

---

### Cloudflare Bindings

Interact with Cloudflare Workers bindings (KV, D1, R2, Durable Objects).

**Configuration:**
```json
{
  "cloudflare-bindings": {
    "command": "npx",
    "args": ["mcp-remote", "https://bindings.mcp.cloudflare.com/mcp"],
    "env": {}
  }
}
```

**Prerequisites:**
- Cloudflare Workers account
- Configured bindings (KV namespaces, D1 databases, R2 buckets)

**Capabilities:**
- Access KV storage
- Query D1 databases
- Manage R2 buckets
- Interact with Durable Objects
- View binding configurations

**Example Usage:**
```python
client.configure_cloudflare_bindings()

result = client.chat(
    message="List all KV namespaces and show storage usage",
    system="You have access to Cloudflare Workers bindings."
)
```

---

## 🏔️ Iceberg MCP Server

Query Apache Iceberg tables via Impala for data lake analytics.

### Installation

**Option 1: Direct from GitHub (Recommended)**
```bash
# Using uvx (uv package executor)
pip install uv
uvx git+https://github.com/cloudera/iceberg-mcp-server@main
```

**Option 2: Clone and Install**
```bash
git clone https://github.com/cloudera/iceberg-mcp-server.git
cd iceberg-mcp-server
pip install -e .
```

### Configuration

```json
{
  "iceberg": {
    "command": "uvx",
    "args": ["git+https://github.com/cloudera/iceberg-mcp-server@main"],
    "env": {
      "IMPALA_HOST": "your-impala-host.com",
      "IMPALA_PORT": "21050",
      "IMPALA_USER": "your-username",
      "IMPALA_PASSWORD": "your-password",
      "IMPALA_DATABASE": "default",
      "MCP_TRANSPORT": "stdio"
    }
  }
}
```

### Environment Variables

**Required:**
- `IMPALA_HOST` - Impala server hostname
- `IMPALA_PORT` - Connection port (default: 21050)
- `IMPALA_USER` - Authentication username
- `IMPALA_PASSWORD` - Authentication password
- `IMPALA_DATABASE` - Target database name

**Optional:**
- `MCP_TRANSPORT` - Communication protocol
  - `stdio` (default) - Standard I/O for local use
  - `http` - HTTP for microservices
  - `sse` - Server-Sent Events for web

### Capabilities

**execute_query(sql_query: str)**
- Execute SQL queries against Impala
- Returns results as JSON
- Read-only access for safety

**get_schema()**
- List available tables
- Show table schemas
- Database metadata

### Security

**Read-Only Access:**
- Iceberg MCP server provides read-only access
- No INSERT, UPDATE, or DELETE operations
- Safe for production analytics

**Credentials Management:**
```bash
# Set environment variables
export IMPALA_HOST="data-warehouse.company.com"
export IMPALA_PORT="21050"
export IMPALA_USER="analytics_user"
export IMPALA_PASSWORD="secure_password"
export IMPALA_DATABASE="production_analytics"
```

### Example Queries

**List Tables:**
```python
client.configure_iceberg(
    impala_host="warehouse.company.com",
    impala_user="user",
    impala_password="pass",
    impala_database="analytics"
)

result = client.chat(
    message="Show all tables in the database with row counts",
    system="You have Iceberg access via Impala."
)
```

**Sales Analysis:**
```python
result = client.chat(
    message="""Query the sales table:
    - Total revenue last quarter
    - Top 10 products by revenue
    - Revenue by region""",
    system="Query Iceberg tables and provide analysis."
)
```

**Schema Optimization:**
```python
result = client.chat(
    message="""Analyze table schemas and suggest:
    - Optimal partitioning strategies
    - Index recommendations
    - Query performance improvements""",
    enable_thinking=True
)
```

---

## 🔄 Combined Usage

Use multiple MCP servers together for comprehensive analysis.

### Example: Infrastructure & Data Analysis

```python
from advanced_mcp_examples import AdvancedMCPClient

client = AdvancedMCPClient()

# Configure all servers
client.configure_cloudflare_observability()
client.configure_cloudflare_bindings()
client.configure_iceberg(
    impala_host="warehouse.company.com",
    impala_user="analytics",
    impala_password="secret",
    impala_database="production"
)

# Comprehensive analysis
result = client.chat(
    message="""Cross-platform performance analysis:

1. Cloudflare Traffic:
   - Show peak hours and traffic patterns
   - Identify high-latency endpoints

2. Storage Analysis:
   - KV cache effectiveness
   - D1 query performance

3. Data Warehouse:
   - User behavior from Iceberg tables
   - Correlate with traffic patterns

Provide optimization recommendations.""",
    enable_thinking=True,
    thinking_budget=5000
)
```

---

## 🚀 Quick Start Examples

### 1. Cloudflare Performance Dashboard

```bash
python advanced_mcp_examples.py
```

This runs all examples including:
- Traffic analytics from Observability
- Storage metrics from Bindings
- Data lake queries from Iceberg

### 2. Custom Analytics Script

```python
#!/usr/bin/env python3
from advanced_mcp_examples import AdvancedMCPClient
import os

client = AdvancedMCPClient()
client.configure_cloudflare_observability()

# Daily analytics report
result = client.chat(
    message="Generate daily analytics report with traffic, errors, and cache stats",
    system="Provide comprehensive daily metrics.",
    enable_thinking=False
)

print(result["text"])

# Save to file
with open("daily_report.md", "w") as f:
    f.write(result["text"])
```

### 3. Automated Data Lake Queries

```python
#!/usr/bin/env python3
import os
from advanced_mcp_examples import AdvancedMCPClient

client = AdvancedMCPClient()
client.configure_iceberg(
    impala_host=os.getenv("IMPALA_HOST"),
    impala_user=os.getenv("IMPALA_USER"),
    impala_password=os.getenv("IMPALA_PASSWORD"),
    impala_database="analytics"
)

# Weekly sales report
result = client.chat(
    message="""Generate weekly sales report:
    - Total revenue
    - Top products
    - Regional breakdown
    - YoY comparison""",
    enable_thinking=True
)

print(result["text"])
```

---

## 🐛 Troubleshooting

### Cloudflare MCP Servers

**Issue: Connection failed**
- Verify internet connectivity
- Check Cloudflare API token permissions
- Ensure `mcp-remote` is available: `npm install -g mcp-remote`

**Issue: No data returned**
- Verify you have Cloudflare zones configured
- Check API token has Analytics:Read permission
- Review Cloudflare dashboard to confirm data exists

### Iceberg MCP Server

**Issue: "IMPALA_HOST not set"**
```bash
export IMPALA_HOST="your-impala-server.com"
export IMPALA_USER="username"
export IMPALA_PASSWORD="password"
```

**Issue: Connection timeout**
- Verify Impala server is accessible
- Check firewall rules for port 21050
- Confirm VPN/network access if required

**Issue: "uvx command not found"**
```bash
pip install uv
# Or use python -m uv
python -m uv tool run git+https://github.com/cloudera/iceberg-mcp-server@main
```

**Issue: Authentication failed**
- Verify credentials are correct
- Check user has database access permissions
- Confirm database name exists

---

## 📊 Performance Tips

### Cloudflare
- Use specific time ranges for analytics queries
- Cache frequently accessed metrics
- Batch requests when possible

### Iceberg
- Partition large tables for better query performance
- Use WHERE clauses to limit data scanned
- Enable query result caching in Impala
- Consider materialized views for complex queries

---

## 🔒 Security Best Practices

**Credentials:**
- ✅ Use environment variables, not hardcoded values
- ✅ Rotate credentials regularly
- ✅ Use read-only accounts for analytics
- ✅ Enable audit logging

**Access Control:**
- ✅ Limit ALLOWED_PATHS for filesystem servers
- ✅ Use least-privilege API tokens
- ✅ Monitor MCP server access logs
- ✅ Implement rate limiting

**Secrets Management:**
```bash
# Use a .env file (never commit!)
cat > .env <<EOF
ANTHROPIC_API_KEY=sk-ant-your-key
IMPALA_HOST=warehouse.company.com
IMPALA_USER=analytics
IMPALA_PASSWORD=secure_password
IMPALA_DATABASE=production
EOF

# Load in your scripts
source .env
```

---

## 📚 Resources

**Cloudflare:**
- [Cloudflare MCP Documentation](https://observability.mcp.cloudflare.com/)
- [Cloudflare API Docs](https://developers.cloudflare.com/api/)
- [Workers Bindings](https://developers.cloudflare.com/workers/configuration/bindings/)

**Iceberg:**
- [Iceberg MCP Server GitHub](https://github.com/cloudera/iceberg-mcp-server)
- [Apache Iceberg Docs](https://iceberg.apache.org/)
- [Impala Documentation](https://impala.apache.org/docs/)

**MCP:**
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Servers](https://github.com/modelcontextprotocol/servers)

---

**Ready to query across platforms! 🌐🏔️**
