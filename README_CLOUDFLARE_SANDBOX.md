# Cloudflare Sandbox SDK Integration

Integration examples combining Cloudflare Sandbox SDK with Claude AI patterns for secure, isolated code execution at the edge.

## 📚 What's Included

### 1. **Thinking Agent with Sandbox** (`thinking-agent-sandbox.ts`)
Extended thinking pattern with code execution in isolated containers.

### 2. **Orchestrator-Workers with Sandboxes** (`orchestrator-workers-sandbox.ts`)
Distributed work processing with each worker in its own isolated sandbox.

### 3. **Claude Code Automation** (`claude-code-automation.ts`)
Automated repository cloning, feature implementation, and diff generation.

---

## 🌟 Cloudflare Sandbox SDK Overview

**What it is:** A development toolkit that lets you run untrusted code safely in isolated Docker containers on Cloudflare's edge network.

**Key Features:**
- ✅ Secure isolation - each sandbox runs in its own container
- ✅ Code execution - supports Python, Node.js, and shell commands
- ✅ File management - read, write, and organize files
- ✅ Process management - run background processes with streaming
- ✅ Git integration - clone repositories directly
- ✅ Preview URLs - expose services publicly
- ✅ Global deployment - runs on Cloudflare's edge network

**Status:** Open Beta - stable API, safe for production use

---

## 🚀 Quick Start

### Prerequisites

1. **Node.js** 16.17.0 or later
2. **Docker** running locally (for development)
3. **Cloudflare account** (for production deployment)
4. **Anthropic API key** (for Claude integration)

### Installation

```bash
cd cloudflare-sandbox-examples

# Install dependencies
npm install

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Configure wrangler
cp wrangler.toml.example wrangler.toml
# Edit wrangler.toml with your settings

# Start local development
npm run dev
```

### Deploy to Production

```bash
# Set secrets
wrangler secret put ANTHROPIC_API_KEY

# Deploy
npm run deploy
```

---

## 💭 Example 1: Thinking Agent with Sandbox

Combines extended thinking with secure code execution.

### Features

- Extended thinking with configurable budget
- Automatic code extraction and execution
- Isolated sandbox per request
- Support for Python and Node.js

### Usage

**Request:**
```bash
curl -X POST https://your-worker.workers.dev \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Calculate the first 10 Fibonacci numbers and find their sum",
    "thinkingBudget": 2000,
    "requiresCodeExecution": true
  }'
```

**Response:**
```json
{
  "thinking": "To solve this, I need to:\n1. Generate Fibonacci sequence\n2. Calculate sum\n...",
  "answer": "The first 10 Fibonacci numbers are: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55\nTheir sum is 143",
  "codeExecutionResults": [
    {
      "code": "fib = [1, 1]\nfor i in range(8):\n    fib.append(fib[-1] + fib[-2])\nprint(sum(fib))",
      "output": "143",
      "success": true
    }
  ]
}
```

### How It Works

1. **Extended Thinking**: Claude reasons through the problem with visible thinking process
2. **Code Extraction**: Automatically detects code blocks in response
3. **Sandbox Execution**: Runs code in isolated Docker container
4. **Result Integration**: Returns thinking, answer, and execution results

### Configuration

```typescript
interface ThinkingRequest {
  task: string;                      // The problem to solve
  context?: string;                  // Additional context
  thinkingBudget?: number;           // Tokens for thinking (default: 2000)
  requiresCodeExecution?: boolean;   // Enable code execution
}
```

### Deployment

```bash
# Update wrangler.toml
[vars]
main = "thinking-agent-sandbox.ts"

# Deploy
wrangler deploy
```

---

## 🔄 Example 2: Orchestrator-Workers with Sandboxes

Distributed task processing with isolated worker sandboxes.

### Features

- Automatic task decomposition
- Parallel worker execution
- Each worker in isolated sandbox
- Result synthesis

### Usage

**Request:**
```bash
curl -X POST https://your-worker.workers.dev \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Analyze the security implications of a new authentication system using JWT tokens",
    "context": "The system needs to support mobile apps and web browsers",
    "maxWorkers": 3
  }'
```

**Response:**
```json
{
  "analysis": "This task requires expertise in: security analysis, authentication protocols, and implementation best practices...",
  "workers": [
    {
      "workerId": "worker-1",
      "role": "Security Researcher",
      "result": "JWT token analysis:\n- Signature verification is critical\n- Token expiration must be enforced...",
      "sandboxOutput": "..."
    },
    {
      "workerId": "worker-2",
      "role": "Authentication Specialist",
      "result": "Implementation considerations:\n- Refresh token rotation\n- Secure storage...",
      "sandboxOutput": null
    }
  ],
  "synthesis": "Comprehensive security analysis:\n1. Token Management: ...\n2. Best Practices: ..."
}
```

### How It Works

1. **Orchestrator**: Analyzes task and creates worker assignments
2. **Workers**: Each runs in isolated sandbox with specialized role
3. **Parallel Execution**: All workers run simultaneously
4. **Synthesis**: Combines results into comprehensive answer

### Configuration

```typescript
interface OrchestratorRequest {
  task: string;          // Main task
  context?: string;      // Additional context
  maxWorkers?: number;   // Limit number of workers (default: 5)
}
```

### Architecture

```
                    ┌──────────────┐
                    │ Orchestrator │
                    │    (Claude)  │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐    ┌────▼─────┐    ┌────▼─────┐
    │ Worker 1  │    │ Worker 2 │    │ Worker 3 │
    │ (Sandbox) │    │ (Sandbox)│    │ (Sandbox)│
    └─────┬─────┘    └────┬─────┘    └────┬─────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                    ┌──────▼───────┐
                    │  Synthesizer │
                    │    (Claude)  │
                    └──────────────┘
```

---

## 🤖 Example 3: Claude Code Automation

Automate feature implementation and bug fixes in repositories.

### Features

- Automatic repository cloning
- Claude Code execution in sandbox
- Git diff generation
- File change tracking
- Custom system prompts

### Usage

**Request:**
```bash
curl -X POST https://your-worker.workers.dev \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "https://github.com/user/my-project",
    "task": "Add input validation to the user registration form",
    "branch": "develop"
  }'
```

**Response:**
```json
{
  "success": true,
  "logs": "Claude Code execution logs...",
  "diff": "diff --git a/src/forms/registration.ts b/src/forms/registration.ts\n...",
  "filesChanged": [
    "src/forms/registration.ts",
    "src/validators/user.ts",
    "tests/forms/registration.test.ts"
  ]
}
```

### How It Works

1. **Clone**: Git checkout repository to sandbox
2. **Execute**: Run Claude Code with task
3. **Capture**: Get git diff and logs
4. **Return**: Send changes back for review/application

### Configuration

```typescript
interface AutomationRequest {
  repo: string;                  // Repository URL
  task: string;                  // Feature/fix description
  branch?: string;               // Branch to checkout (default: main)
  appendSystemPrompt?: string;   // Custom system prompt
}
```

### Custom System Prompts

```bash
curl -X POST https://your-worker.workers.dev \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "https://github.com/user/project",
    "task": "Optimize database queries",
    "appendSystemPrompt": "Focus on PostgreSQL-specific optimizations. Add indexes where appropriate. Include performance benchmarks in comments."
  }'
```

### Use Cases

**Feature Implementation:**
```json
{
  "task": "Add dark mode toggle to settings page",
  "repo": "https://github.com/company/web-app"
}
```

**Bug Fixing:**
```json
{
  "task": "Fix memory leak in image processing service",
  "repo": "https://github.com/company/image-processor"
}
```

**Refactoring:**
```json
{
  "task": "Extract authentication logic into separate service",
  "repo": "https://github.com/company/monolith"
}
```

---

## 🔧 Integration Patterns

### Pattern 1: CI/CD Automation

```typescript
// Webhook handler for automated feature implementation
async function handleWebhook(request: Request, env: Env) {
  const { issue, repository } = await request.json();

  // Trigger automation for labeled issues
  if (issue.labels.includes('auto-implement')) {
    const result = await runAutomation(env, {
      repo: repository.clone_url,
      task: issue.title + '\n\n' + issue.body,
      branch: 'auto/' + issue.number
    });

    // Create PR with changes
    if (result.success && result.diff) {
      await createPullRequest(
        repository,
        result.diff,
        `Fix #${issue.number}: ${issue.title}`
      );
    }
  }
}
```

### Pattern 2: Multi-Repository Analysis

```typescript
// Analyze security across multiple repos
async function analyzeRepositories(repos: string[], env: Env) {
  const tasks = repos.map(repo => ({
    id: crypto.randomUUID().slice(0, 8),
    role: 'Security Analyzer',
    task: `Analyze ${repo} for security vulnerabilities`,
    sandboxId: crypto.randomUUID().slice(0, 8)
  }));

  const results = await Promise.all(
    tasks.map(task => runWorker(env, task, 'Security audit'))
  );

  return synthesizeResults(env, 'Security audit', 'Multi-repo analysis', results);
}
```

### Pattern 3: Interactive Code Execution

```typescript
// REPL-style interaction with persistent sandbox
class InteractiveSandbox {
  private sandbox: any;
  private context: string;

  async executeWithThinking(code: string, env: Env) {
    // Use thinking agent for code explanation
    const thinking = await processWithThinking(env, {
      task: `Explain what this code does:\n${code}`,
      thinkingBudget: 1000
    });

    // Execute in sandbox
    const result = await this.sandbox.exec(`python3 -c "${code}"`);

    return {
      explanation: thinking.answer,
      output: result.stdout,
      reasoning: thinking.thinking
    };
  }
}
```

### Pattern 4: Hybrid Local + Edge

```python
# Local Python tool calls edge sandbox
import requests

class EdgeSandboxClient:
    def __init__(self, worker_url: str, api_key: str):
        self.worker_url = worker_url
        self.api_key = api_key

    def execute_with_thinking(self, task: str, requires_code: bool = False):
        response = requests.post(
            self.worker_url,
            json={
                'task': task,
                'thinkingBudget': 3000,
                'requiresCodeExecution': requires_code
            }
        )
        return response.json()

# Use from existing Python tools
from thinking_agent_builder import ThinkingAgent

agent = ThinkingAgent(domain='data_analysis')
edge_sandbox = EdgeSandboxClient('https://my-worker.workers.dev', api_key)

# Heavy computation runs on edge
result = edge_sandbox.execute_with_thinking(
    'Process 1M records and find anomalies',
    requires_code=True
)
```

---

## 📊 Comparison: Local vs Edge Sandboxes

| Feature | Local Docker | Cloudflare Sandbox |
|---------|--------------|-------------------|
| **Setup** | Complex (Docker install) | Simple (deploy worker) |
| **Scaling** | Limited by machine | Auto-scales globally |
| **Cold Start** | Slow (container startup) | Fast (edge optimization) |
| **Cost** | Infrastructure costs | Pay-per-use |
| **Location** | Single machine | Global edge network |
| **Isolation** | Container-level | Container + edge isolation |
| **Integration** | Direct system access | HTTP API |
| **Use Case** | Development, testing | Production, global scale |

---

## 🎯 Use Cases

### Use Case 1: Automated Code Review

**Problem:** Manual code review is time-consuming

**Solution:**
```typescript
// Review PR automatically
const result = await runAutomation(env, {
  repo: pr.head.repo.clone_url,
  task: 'Review this code for:\n- Security vulnerabilities\n- Performance issues\n- Best practices violations',
  branch: pr.head.ref,
  appendSystemPrompt: 'Provide specific file/line references for all issues found'
});

// Post review comments
await postReviewComments(pr.number, result.diff);
```

### Use Case 2: Data Analysis Pipeline

**Problem:** Need secure execution for user-provided analysis scripts

**Solution:**
```typescript
// Execute user's data analysis safely
const result = await processWithThinking(env, {
  task: `Analyze this dataset: ${datasetUrl}\n\nUser requirements: ${userQuery}`,
  thinkingBudget: 5000,
  requiresCodeExecution: true
});

// Results isolated per user, no data leakage
return result.codeExecutionResults;
```

### Use Case 3: Multi-Perspective Research

**Problem:** Complex topics need multiple expert viewpoints

**Solution:**
```typescript
// Get insights from multiple specialized agents
const analysis = await processWithOrchestrator(env, {
  task: 'Evaluate the technical feasibility of migrating our monolith to microservices',
  context: 'Current stack: Ruby on Rails, PostgreSQL, Redis. Team size: 8 engineers.',
  maxWorkers: 5
});

// Each worker analyzes from their perspective (security, scalability, cost, etc.)
```

### Use Case 4: Educational Platform

**Problem:** Students need safe code execution environment

**Solution:**
```typescript
// Student submits code for assignment
const result = await executeInSandbox(sandbox, studentCode, 'python');

// Thinking agent provides feedback
const feedback = await processWithThinking(env, {
  task: `Review student code and provide educational feedback:\n${studentCode}\n\nOutput: ${result.output}`,
  context: 'Be encouraging and explain concepts clearly'
});
```

---

## 🐛 Troubleshooting

### Issue: "Docker not found" (Local Development)

**Solution:**
```bash
# Ensure Docker is running
docker ps

# Pull sandbox container manually
docker pull cloudflare/sandbox:latest
```

### Issue: "Sandbox timeout"

**Solution:**
```typescript
// Increase timeout for long-running tasks
const result = await sandbox.exec(cmd, {
  timeout: 300000  // 5 minutes
});
```

### Issue: "API key not set"

**Solution:**
```bash
# Set secret in Cloudflare
wrangler secret put ANTHROPIC_API_KEY

# For local dev, use .dev.vars file
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .dev.vars
```

### Issue: "Container port not found"

**Solution:**
```dockerfile
# Add EXPOSE directive to Dockerfile
EXPOSE 8000 8080 3000
```

### Issue: "Worker exceeds size limit"

**Solution:**
```bash
# Use external dependencies via npm
# Bundle only necessary code
# Consider splitting into multiple workers
```

---

## 📚 Best Practices

### Security

**DO:**
- ✅ Validate all input before execution
- ✅ Use unique sandbox IDs per request
- ✅ Set resource limits (timeout, memory)
- ✅ Sanitize git repository URLs
- ✅ Use secrets for API keys

**DON'T:**
- ❌ Execute arbitrary code without validation
- ❌ Reuse sandboxes across users
- ❌ Store sensitive data in sandbox
- ❌ Trust user-provided repository URLs

### Performance

**DO:**
- ✅ Run workers in parallel when possible
- ✅ Use caching for repeated operations
- ✅ Set appropriate timeouts
- ✅ Clean up sandboxes after use
- ✅ Monitor execution times

**DON'T:**
- ❌ Create sandboxes unnecessarily
- ❌ Run synchronous operations in sequence
- ❌ Keep sandboxes alive indefinitely
- ❌ Ignore error handling

### Cost Optimization

**DO:**
- ✅ Use sandbox pooling for similar tasks
- ✅ Set reasonable worker limits
- ✅ Implement request throttling
- ✅ Cache results when appropriate
- ✅ Monitor usage metrics

**DON'T:**
- ❌ Create new sandbox for every request
- ❌ Run unlimited parallel workers
- ❌ Skip timeout configuration
- ❌ Ignore cold start optimization

---

## 🔗 Additional Resources

**Official Documentation:**
- [Cloudflare Sandbox SDK](https://developers.cloudflare.com/sandbox/)
- [Cloudflare Workers](https://developers.cloudflare.com/workers/)
- [Anthropic API](https://docs.anthropic.com/)

**This Repository:**
- `README_THINKING_TOOLS.md` - Extended thinking with tools
- `README_ADVANCED_PATTERNS.md` - Metaprompt & orchestrator patterns
- `README_COMMIT_HELPER.md` - Commit message generation
- `README_RESILIENT_PPTX.md` - File handling & PowerPoint generation

**Source Code:**
- [Cloudflare Sandbox SDK GitHub](https://github.com/cloudflare/sandbox-sdk)
- [Examples in this repo](./cloudflare-sandbox-examples/)

---

## 🎯 Next Steps

1. **Set up development environment:**
   ```bash
   cd cloudflare-sandbox-examples
   npm install
   cp wrangler.toml.example wrangler.toml
   ```

2. **Try examples locally:**
   ```bash
   npm run dev
   # Test with curl or Postman
   ```

3. **Deploy to production:**
   ```bash
   wrangler secret put ANTHROPIC_API_KEY
   npm run deploy
   ```

4. **Build custom integrations:**
   - Combine with existing Python tools
   - Create hybrid local/edge workflows
   - Build CI/CD automation
   - Develop educational platforms

---

**Run code safely at the edge! 🚀🔒**
