# Modal Setup Guide

Step-by-step guide to set up Modal with your credentials and deploy the examples.

## 🔐 Your Credentials

You have the following Modal credentials:

### Authentication Token
- **Token ID**: `ak-CNC6lcJihRz4vhP3WnR2YE`
- **Token Secret**: `as-BRa4kKXSby7B8NhgFBFfak`

### Webhook Credentials
- **Token ID**: `wk-MqtJuh2UbPbBHNuKTf8BOm`
- **Token Secret**: `ws-erJAdpAlGXBKXJFXzhlWR3`

### Account ID
- **ID**: `ac-qp2iIJLVPa4JpwLDc95lW3`

---

## 📦 Step 1: Install Modal

```bash
# Install Modal CLI
pip install modal

# Verify installation
modal --version
```

---

## 🔑 Step 2: Authenticate

```bash
# Set your Modal token
modal token set --token-id ak-CNC6lcJihRz4vhP3WnR2YE --token-secret as-BRa4kKXSby7B8NhgFBFfak

# Verify authentication
modal profile current
```

---

## 🔒 Step 3: Create Anthropic Secret

You need to add your Anthropic API key to Modal's secrets:

```bash
# Interactive method (recommended)
modal secret create anthropic-secret

# You'll be prompted to enter:
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# Or one-line method
modal secret create anthropic-secret ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Verify the secret was created:**
```bash
modal secret list
```

You should see `anthropic-secret` in the list.

---

## 🚀 Step 4: Test Examples

### Test 1: Thinking Agent

```bash
cd modal-examples

# Run locally (no deployment)
modal run thinking_agent_modal.py \
  --task "What is 15 factorial?" \
  --domain math
```

**Expected output:**
```
THINKING:
----------------------------------------------------------------------
To calculate 15!, I need to multiply: 15 × 14 × 13 × ... × 2 × 1
...

ANSWER:
----------------------------------------------------------------------
15! = 1,307,674,368,000
```

### Test 2: Code Analyzer

```bash
# Analyze a file
modal run code_analyzer_modal.py \
  --file thinking_agent_modal.py \
  --query "What does this code do?"
```

### Test 3: Orchestrator-Workers

```bash
# Complex task decomposition
modal run orchestrator_workers_modal.py \
  --task "Analyze the pros and cons of microservices architecture" \
  --max-workers 3
```

### Test 4: Batch Processor

```bash
# Create sample data
echo '[
  {"id": 1, "content": "Explain AI"},
  {"id": 2, "content": "What is Python?"},
  {"id": 3, "content": "How does HTTP work?"}
]' > test_data.json

# Process batch
modal run resilient_batch_processor.py \
  --input-file test_data.json \
  --output-file results.json
```

---

## 🌐 Step 5: Deploy Web Endpoints

### Deploy Thinking Agent API

```bash
# Deploy to Modal cloud
modal deploy thinking_agent_modal.py

# Output will show your endpoint URL:
# ✓ Created web function => https://your-username--thinking-agent-modal-api.modal.run
```

**Test the deployed endpoint:**
```bash
curl -X POST https://your-username--thinking-agent-modal-api.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Optimize this SQL: SELECT * FROM users",
    "domain": "code",
    "thinking_budget": 2000
  }'
```

### Deploy Code Analyzer API

```bash
modal deploy code_analyzer_modal.py

# Test security audit endpoint
curl -X POST https://your-username--code-analyzer-modal-api-security-audit.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "code": "query = \"SELECT * FROM users WHERE id = \" + user_id",
    "language": "python"
  }'
```

### Deploy Orchestrator-Workers API

```bash
modal deploy orchestrator_workers_modal.py

# Test
curl -X POST https://your-username--orchestrator-workers-modal-api.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Evaluate blockchain security considerations",
    "max_workers": 4
  }'
```

---

## 🔗 Step 6: Set Up Webhooks with Authentication

For webhooks that require authentication, include these headers:

```bash
# Example webhook request
curl -X POST https://your-webhook-url.modal.run \
  -H "Content-Type: application/json" \
  -H "Modal-Key: wk-MqtJuh2UbPbBHNuKTf8BOm" \
  -H "Modal-Secret: ws-erJAdpAlGXBKXJFXzhlWR3" \
  -d '{"your": "data"}'
```

---

## 📊 Step 7: Monitor Deployments

### View Apps

```bash
# List all deployed apps
modal app list

# Get details about a specific app
modal app show thinking-agent-modal
```

### View Logs

```bash
# Stream logs from a running function
modal app logs thinking-agent-modal

# View logs for specific function
modal function logs thinking-agent-modal::think_and_solve
```

### View Usage

```bash
# Check resource usage
modal volume list
modal secret list
modal object list
```

---

## 🔧 Troubleshooting

### Issue: "Secret not found"

```bash
# List all secrets
modal secret list

# Recreate the secret
modal secret create anthropic-secret ANTHROPIC_API_KEY=your-key
```

### Issue: "Authentication failed"

```bash
# Check current profile
modal profile current

# Re-authenticate
modal token set --token-id ak-CNC6lcJihRz4vhP3WnR2YE --token-secret as-BRa4kKXSby7B8NhgFBFfak
```

### Issue: "Function timeout"

Edit the function decorator in your code:

```python
@app.function(
    timeout=1800,  # Increase to 30 minutes
    retries=3      # Add retries
)
```

### Issue: "Out of memory"

```python
@app.function(
    memory=8192,  # Increase to 8GB
    cpu=2.0       # Add more CPU
)
```

---

## 💡 Pro Tips

### 1. Development Workflow

```bash
# Run locally for testing
modal run your_script.py

# Deploy to cloud when ready
modal deploy your_script.py

# Update deployment
modal deploy your_script.py --force
```

### 2. Environment Variables

Create a `.env` file (don't commit this!):

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-your-key
MODAL_TOKEN_ID=ak-CNC6lcJihRz4vhP3WnR2YE
MODAL_TOKEN_SECRET=as-BRa4kKXSby7B8NhgFBFfak
```

### 3. Testing Locally

```python
# Add to your script for local testing
if __name__ == "__main__":
    # Test logic here
    result = your_function.local(args)
    print(result)
```

### 4. Cost Optimization

```bash
# Use faster/cheaper models for testing
model="claude-3-haiku-20240307"  # Cheaper

# Use Sonnet for production
model="claude-sonnet-4-5"  # More capable
```

---

## 📚 Next Steps

1. **Deploy your first endpoint**:
   ```bash
   modal deploy thinking_agent_modal.py
   ```

2. **Test with curl**:
   ```bash
   curl -X POST your-endpoint-url -H "Content-Type: application/json" -d '{"task": "test"}'
   ```

3. **Integrate with your app**:
   ```python
   import requests

   response = requests.post(
       "https://your-modal-endpoint.modal.run",
       json={"task": "Your task here"}
   )
   print(response.json())
   ```

4. **Monitor usage**:
   - Visit [Modal Dashboard](https://modal.com/dashboard)
   - Check logs, usage, and costs

5. **Scale up**:
   - Modal automatically scales
   - No infrastructure management needed
   - Pay only for what you use

---

## 🔐 Security Best Practices

**DO:**
- ✅ Use Modal secrets for API keys
- ✅ Add webhook authentication headers
- ✅ Validate input in your functions
- ✅ Set appropriate timeouts
- ✅ Monitor logs for suspicious activity

**DON'T:**
- ❌ Hardcode API keys in code
- ❌ Commit `.env` files
- ❌ Expose endpoints without authentication
- ❌ Skip input validation
- ❌ Ignore timeout settings

---

## 📖 Resources

- [Modal Documentation](https://modal.com/docs)
- [Modal Examples](https://modal.com/docs/examples)
- [Modal Pricing](https://modal.com/pricing)
- [Anthropic API Docs](https://docs.anthropic.com/)

---

**Ready to deploy! 🚀**
