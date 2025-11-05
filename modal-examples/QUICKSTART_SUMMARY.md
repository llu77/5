# Modal Quickstart Summary

**Your Modal environment is ready! Here's everything you need to get started.**

## 🔐 Your Credentials

### Modal Authentication Token
```
Token ID:     ak-CNC6lcJihRz4vhP3WnR2YE
Token Secret: as-BRa4kKXSby7B8NhgFBFfak
```

### Webhook Authentication
```
Modal-Key:    wk-MqtJuh2UbPbBHNuKTf8BOm
Modal-Secret: ws-erJAdpAlGXBKXJFXzhlWR3
```

### Account ID
```
Account ID: ac-qp2iIJLVPa4JpwLDc95lW3
```

---

## ⚡ Quick Start (3 commands)

```bash
# 1. Run the automated setup script
./quickstart.sh

# 2. Test a webhook (after deploying)
python test_webhook.py

# 3. Check your deployments
modal app list
```

---

## 📋 Manual Setup (if you prefer)

### Step 1: Install & Authenticate

```bash
# Install Modal
pip install modal

# Set your token
modal token set \
  --token-id ak-CNC6lcJihRz4vhP3WnR2YE \
  --token-secret as-BRa4kKXSby7B8NhgFBFfak
```

### Step 2: Add Anthropic API Key

```bash
# Create secret
modal secret create anthropic-secret

# You'll be prompted for:
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 3: Test Locally

```bash
# Test thinking agent
modal run thinking_agent_modal.py \
  --task "What is 15 factorial?" \
  --domain math
```

### Step 4: Deploy to Cloud

```bash
# Deploy thinking agent
modal deploy thinking_agent_modal.py

# You'll get a URL like:
# https://your-username--thinking-agent-modal-api.modal.run
```

### Step 5: Test Deployed Endpoint

```bash
# Use the test script
python test_webhook.py \
  --url https://your-endpoint.modal.run \
  --test thinking

# Or use curl
curl -X POST https://your-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -H "Modal-Key: wk-MqtJuh2UbPbBHNuKTf8BOm" \
  -H "Modal-Secret: ws-erJAdpAlGXBKXJFXzhlWR3" \
  -d '{"task": "Explain quantum computing", "thinking_budget": 2000}'
```

---

## 🎯 What You Can Deploy

### 1. Thinking Agent (`thinking_agent_modal.py`)

**Features:**
- Extended thinking with Claude Sonnet 4.5
- Domain-specific prompts (math, code, strategy, data, research)
- Iterative problem solving
- Web API endpoint

**Example Usage:**
```bash
# Local test
modal run thinking_agent_modal.py \
  --task "Optimize this database query: SELECT * FROM orders WHERE customer_id IN (SELECT id FROM customers)" \
  --domain code

# Deploy
modal deploy thinking_agent_modal.py

# Test API
curl -X POST https://your-url/api \
  -H "Content-Type: application/json" \
  -d '{"task": "Your question", "thinking_budget": 3000}'
```

### 2. Orchestrator-Workers (`orchestrator_workers_modal.py`)

**Features:**
- Automatic task decomposition
- Parallel worker execution
- Multiple specialized perspectives
- Result synthesis

**Example Usage:**
```bash
# Local test
modal run orchestrator_workers_modal.py \
  --task "Analyze the security of our API authentication system" \
  --max-workers 5

# Deploy
modal deploy orchestrator_workers_modal.py

# Test API
curl -X POST https://your-url/api \
  -H "Content-Type: application/json" \
  -d '{"task": "Evaluate microservices vs monolith", "max_workers": 4}'
```

### 3. Code Analyzer (`code_analyzer_modal.py`)

**Features:**
- Repository analysis
- Security auditing (OWASP Top 10)
- Code comparison
- Refactoring suggestions

**Example Usage:**
```bash
# Analyze repository
modal run code_analyzer_modal.py \
  --repo "https://github.com/user/project" \
  --query "Find security vulnerabilities"

# Deploy
modal deploy code_analyzer_modal.py

# Security audit via API
curl -X POST https://your-url/api_security_audit \
  -H "Content-Type: application/json" \
  -d '{
    "code": "query = \"SELECT * FROM users WHERE id = \" + user_id",
    "language": "python"
  }'
```

### 4. Batch Processor (`resilient_batch_processor.py`)

**Features:**
- Fault-tolerant processing
- Automatic checkpointing
- Resume capability
- Parallel execution

**Example Usage:**
```bash
# Create test data
echo '[
  {"id": 1, "content": "What is AI?"},
  {"id": 2, "content": "Explain Python"}
]' > data.json

# Process
modal run resilient_batch_processor.py \
  --input-file data.json \
  --output-file results.json \
  --parallel True
```

---

## 🔧 Helper Scripts

### Quickstart Script (`quickstart.sh`)

Automated setup and deployment:

```bash
./quickstart.sh

# This will:
# 1. Install Modal
# 2. Authenticate
# 3. Create Anthropic secret
# 4. Test examples
# 5. Deploy to cloud
# 6. Show your endpoint URLs
```

### Webhook Tester (`test_webhook.py`)

Test deployed endpoints:

```bash
# Interactive mode
python test_webhook.py

# Command line
python test_webhook.py \
  --url https://your-endpoint.modal.run \
  --test thinking

# Custom payload
python test_webhook.py \
  --url https://your-endpoint.modal.run \
  --payload '{"task": "Test question"}'
```

---

## 📊 Monitoring & Management

### View Deployments

```bash
# List all apps
modal app list

# Show app details
modal app show thinking-agent-modal

# View logs
modal app logs thinking-agent-modal
```

### Dashboard

Visit: https://modal.com/dashboard

You'll see:
- Active deployments
- Function calls
- Resource usage
- Costs
- Logs

### Usage Statistics

```bash
# List volumes
modal volume list

# List secrets
modal secret list

# List objects
modal object list
```

---

## 💡 Common Tasks

### Update a Deployment

```bash
# Make changes to your code
# Then redeploy
modal deploy thinking_agent_modal.py --force
```

### Check Logs

```bash
# Stream live logs
modal app logs thinking-agent-modal --follow

# Get recent logs
modal app logs thinking-agent-modal --lines 100
```

### Stop a Deployment

```bash
# Delete an app
modal app stop thinking-agent-modal
```

### Update Secrets

```bash
# Update Anthropic key
modal secret create anthropic-secret \
  ANTHROPIC_API_KEY=new-key \
  --force
```

---

## 🐛 Troubleshooting

### "Secret not found"

```bash
modal secret list
modal secret create anthropic-secret ANTHROPIC_API_KEY=your-key
```

### "Authentication failed"

```bash
modal token set \
  --token-id ak-CNC6lcJihRz4vhP3WnR2YE \
  --token-secret as-BRa4kKXSby7B8NhgFBFfak
```

### "Function timeout"

Edit function in code:
```python
@app.function(timeout=1800)  # 30 minutes
```

### "Out of memory"

```python
@app.function(memory=8192)  # 8GB
```

---

## 📚 Documentation

- **Setup Guide**: `SETUP.md` - Detailed setup instructions
- **Main README**: `README.md` - Overview and examples
- **Modal Docs**: `README_MODAL.md` - Full documentation
- **Official**: https://modal.com/docs

---

## 🎯 Next Steps

1. **Run quickstart**: `./quickstart.sh`
2. **Deploy an example**: `modal deploy thinking_agent_modal.py`
3. **Test webhook**: `python test_webhook.py`
4. **Check dashboard**: https://modal.com/dashboard
5. **Build your own**: Use examples as templates

---

## 🔐 Security Reminder

**Keep these secure:**
- ✅ Your Modal tokens
- ✅ Your Anthropic API key
- ✅ Your webhook credentials

**Never:**
- ❌ Commit `.env` files
- ❌ Share credentials publicly
- ❌ Hardcode API keys in code

---

**You're all set! 🚀 Run `./quickstart.sh` to get started!**
