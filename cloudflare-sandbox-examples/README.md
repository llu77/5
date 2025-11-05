# Cloudflare Sandbox Examples

Integration examples combining Cloudflare Sandbox SDK with Claude AI patterns.

## 📁 What's Here

- **`thinking-agent-sandbox.ts`** - Extended thinking with sandbox code execution
- **`orchestrator-workers-sandbox.ts`** - Distributed workers in isolated sandboxes
- **`claude-code-automation.ts`** - Automated repository editing with Claude Code
- **`package.json`** - Dependencies and scripts
- **`wrangler.toml.example`** - Configuration template
- **`tsconfig.json`** - TypeScript configuration

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Configure
cp wrangler.toml.example wrangler.toml

# Choose which example to run (edit wrangler.toml)
# Set: main = "thinking-agent-sandbox.ts"

# Start local dev server
npm run dev

# Deploy to Cloudflare
npm run deploy
```

## 📖 Documentation

See the main repository's `README_CLOUDFLARE_SANDBOX.md` for:
- Detailed usage examples
- API documentation
- Integration patterns
- Best practices
- Troubleshooting guide

## 🎯 Example Usage

### Thinking Agent

```bash
curl -X POST http://localhost:8787 \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Calculate factorial of 20 and explain the result",
    "thinkingBudget": 2000,
    "requiresCodeExecution": true
  }'
```

### Orchestrator-Workers

```bash
curl -X POST http://localhost:8787 \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Analyze security best practices for a REST API",
    "maxWorkers": 3
  }'
```

### Claude Code Automation

```bash
curl -X POST http://localhost:8787 \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "https://github.com/user/project",
    "task": "Add input validation to login form"
  }'
```

## 🔧 Configuration

Edit `wrangler.toml` to:
- Choose which example to deploy (`main` field)
- Set environment variables
- Configure Durable Objects binding

## 📚 Learn More

- [Cloudflare Sandbox SDK](https://github.com/cloudflare/sandbox-sdk)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
