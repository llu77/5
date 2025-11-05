# Modal + Claude Integration Examples

Serverless Python functions combining Modal's compute platform with Claude AI patterns.

## 📁 What's Here

### Examples
- **`thinking_agent_modal.py`** - Extended thinking with Modal serverless functions
- **`orchestrator_workers_modal.py`** - Distributed workers with automatic scaling
- **`code_analyzer_modal.py`** - Code analysis and security auditing
- **`resilient_batch_processor.py`** - Fault-tolerant batch processing

### Documentation & Tools
- **`QUICKSTART_SUMMARY.md`** - ⚡ **START HERE!** Your credentials and 3-command setup
- **`SETUP.md`** - Detailed setup guide with troubleshooting
- **`quickstart.sh`** - Automated setup script
- **`test_webhook.py`** - Webhook testing tool
- **`requirements.txt`** - Python dependencies

## ⚡ Ultra-Quick Start (Automated)

```bash
# One-command setup (includes deployment)
./quickstart.sh

# Or just 3 commands:
pip install modal
modal token set --token-id ak-CNC6lcJihRz4vhP3WnR2YE --token-secret as-BRa4kKXSby7B8NhgFBFfak
modal deploy thinking_agent_modal.py
```

**Read `QUICKSTART_SUMMARY.md` for your credentials and detailed instructions.**

## 🚀 Manual Setup

```bash
# 1. Install Modal CLI
pip install modal

# 2. Authenticate (use your credentials from QUICKSTART_SUMMARY.md)
modal token set --token-id ak-CNC6lcJihRz4vhP3WnR2YE --token-secret as-BRa4kKXSby7B8NhgFBFfak

# 3. Create Anthropic secret
modal secret create anthropic-secret ANTHROPIC_API_KEY=sk-ant-...

# 4. Test locally
modal run thinking_agent_modal.py

# 5. Deploy to cloud
modal deploy thinking_agent_modal.py
```

## 📖 Documentation

See the main repository's `README_MODAL.md` for:
- Detailed usage examples
- API documentation
- Integration patterns
- Best practices
- Comparison with Cloudflare Sandboxes

## 🎯 Example Usage

### Thinking Agent

```bash
# Basic
modal run thinking_agent_modal.py \
  --task "Calculate factorial of 20"

# With domain
modal run thinking_agent_modal.py \
  --task "Prove the Pythagorean theorem" \
  --domain math \
  --thinking-budget 5000

# Iterative solving
modal run thinking_agent_modal.py \
  --task "Solve traveling salesman for 5 cities" \
  --iterative True
```

### Orchestrator-Workers

```bash
modal run orchestrator_workers_modal.py \
  --task "Analyze security best practices for REST APIs" \
  --max-workers 5
```

### Code Analyzer

```bash
# Analyze file
modal run code_analyzer_modal.py --file "script.py"

# Analyze directory
modal run code_analyzer_modal.py \
  --directory "src/" \
  --query "Find potential bugs"

# Analyze repository
modal run code_analyzer_modal.py \
  --repo "https://github.com/user/repo" \
  --query "Summarize architecture"
```

### Batch Processor

```bash
# Sequential with checkpoints
modal run resilient_batch_processor.py \
  --input-file data.json \
  --output-file results.json

# Parallel processing
modal run resilient_batch_processor.py \
  --input-file data.json \
  --parallel True
```

## 🌐 Web Deployments

Each example includes web endpoints:

```bash
# Deploy
modal deploy thinking_agent_modal.py

# Use API
curl -X POST https://your-modal-url.modal.run \
  -H "Content-Type: application/json" \
  -d '{"task": "Your question here", "thinking_budget": 3000}'
```

## 📚 Learn More

- [Modal Documentation](https://modal.com/docs)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [Modal Examples](https://modal.com/docs/examples)
