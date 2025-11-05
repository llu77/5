# Fly.io Deployment Examples

Flask applications ready to deploy on Fly.io with Claude AI integration.

## 📁 What's Here

- **`thinking_agent_fly.py`** - Extended thinking Flask app
- **`fly.toml`** - Fly.io configuration
- **`Dockerfile`** - Container configuration
- **`requirements.txt`** - Python dependencies

## ⚡ Quick Deploy

```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Login
fly auth login

# 3. Launch app
fly launch --name thinking-agent

# 4. Set secrets
fly secrets set ANTHROPIC_API_KEY=sk-ant-your-key

# 5. Deploy
fly deploy

# Your app is live!
# https://thinking-agent.fly.dev
```

## 🔐 Your Fly.io Token

```
FlyV1 fm2_lJPECAAAAAAACt3txBBzORMVURNOLhllVqnZS6rTwrVodHRwczovL2FwaS5mbHkuaW8vdjGUAJLOABRgAx8Lk7lodHRwczovL2FwaS5mbHkuaW8vYWFhL3Yx...
```

Set with:
```bash
export FLY_API_TOKEN="your-token-here"
```

## 📖 API Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "thinking-agent"
}
```

### POST /think
Extended thinking analysis.

**Request:**
```json
{
  "task": "Your problem or question",
  "thinking_budget": 3000,
  "domain": "general"
}
```

**Response:**
```json
{
  "thinking": "...",
  "answer": "...",
  "usage": {
    "input_tokens": 245,
    "output_tokens": 892
  }
}
```

### POST /analyze
Quick analysis without extended thinking.

**Request:**
```json
{
  "query": "What does this code do?",
  "context": "code here"
}
```

## 🧪 Test Deployed App

```bash
# Health check
curl https://thinking-agent.fly.dev/health

# Thinking
curl -X POST https://thinking-agent.fly.dev/think \
  -H "Content-Type: application/json" \
  -d '{"task": "Explain quantum computing", "thinking_budget": 3000}'

# Analysis
curl -X POST https://thinking-agent.fly.dev/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze this", "context": "code"}'
```

## 📊 Monitoring

```bash
# View logs
fly logs

# Live tail
fly logs --follow

# Check status
fly status

# Dashboard
fly dashboard
```

## 🔧 Management

```bash
# Scale
fly scale count 3
fly scale memory 1024

# Restart
fly machine restart

# SSH into machine
fly ssh console

# View secrets
fly secrets list
```

## 📚 More Info

See `README_FLY_MCP.md` in the main repository for:
- Detailed deployment guide
- MCP integration
- Use cases
- Troubleshooting
