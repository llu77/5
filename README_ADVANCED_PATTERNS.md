# Advanced Claude Patterns & Tools

Comprehensive collection of advanced AI patterns including metaprompting, orchestrator-workers, extended thinking, and practical applications.

## 📚 What's Included

### 1. **Metaprompt Tool** (`metaprompt_tool.py`)
Generate high-quality prompts for any task automatically.

**Solves:** The "blank page problem" - not knowing how to structure a prompt

**How it works:**
- Analyzes your task description
- Generates structured, example-rich prompts
- Extracts input variables automatically
- Tests generated prompts interactively

### 2. **Orchestrator-Workers** (`orchestrator_workers.py`)
Dynamically break down complex tasks into specialized subtasks.

**Solves:** Tasks that benefit from multiple perspectives or approaches

**How it works:**
- Orchestrator analyzes task and determines best approaches
- Workers execute each approach independently
- Returns multiple variations/perspectives

### 3. **Extended Thinking Tools**
- `extended_thinking_examples.py` - Basic thinking examples
- `thinking_problem_solver.py` - CLI for complex problem solving
- `thinking_with_tools_examples.py` - Thinking + tool use
- `thinking_agent_builder.py` - Agent framework with thinking

### 4. **Financial Analysis** (domain example)
- Financial ratio calculations
- Industry benchmarking
- Trend analysis

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install required packages
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="your-key-here"
```

---

## 🎯 Metaprompt Tool

### What It Does
Generates expert-level prompts for any task by analyzing what makes prompts effective.

### Usage

**Interactive Mode:**
```bash
python metaprompt_tool.py --interactive

# Example interaction:
📝 Enter your task: Analyze customer reviews for sentiment
Variables: REVIEW PRODUCT
# → Generates complete prompt template
```

**Single Task:**
```bash
# Generate prompt
python metaprompt_tool.py "Summarize research papers for non-experts"

# With specific variables
python metaprompt_tool.py "Grade student essays" --variables ESSAY RUBRIC

# Save to file
python metaprompt_tool.py "Translate technical docs" --output translator.txt

# Test immediately
python metaprompt_tool.py "Extract key facts from articles" --test
```

### Example Output

**Input Task:**
```
"Write product descriptions for e-commerce"
```

**Generated Prompt:**
```
You will be writing product descriptions for e-commerce listings.

Here is the product information:
<product>
{$PRODUCT_INFO}
</product>

Target audience: {$TARGET_AUDIENCE}

Write a compelling product description that:
1. Highlights key features and benefits
2. Addresses customer pain points
3. Uses persuasive but honest language
4. Includes a clear call-to-action

Format your response:
<thinking>
Identify the product's main selling points and target audience needs.
</thinking>

<description>
Your product description here.
</description>
```

### When to Use
- ✅ Building new AI applications
- ✅ Need consistent prompt structure
- ✅ Want to follow best practices
- ✅ Solving similar problems repeatedly
- ❌ One-off simple tasks
- ❌ You already have a great prompt

---

## 🎭 Orchestrator-Workers Pattern

### What It Does
Analyzes tasks and dynamically creates specialized approaches, then executes them in parallel.

### Usage

**Marketing Content:**
```bash
# Generate multiple marketing variations
python orchestrator_workers.py marketing \
  "Create product launch announcement for AI coding assistant"

# With context
python orchestrator_workers.py marketing \
  "Email campaign for new feature" \
  --context "target_audience=developers" "tone=technical"
```

**Research Analysis:**
```bash
# Multiple analytical perspectives
python orchestrator_workers.py research \
  "What are the impacts of AI on employment?"

# Save results
python orchestrator_workers.py research \
  "Analyze blockchain scalability solutions" \
  --output analysis.json
```

**Creative Writing:**
```bash
# Different creative styles
python orchestrator_workers.py creative \
  "Write a company mission statement for sustainable fashion brand"

# Quiet mode (less output)
python orchestrator_workers.py creative \
  "Blog post about remote work benefits" \
  --quiet
```

### Example Flow

**Input:**
```
Task: "Create product description for eco-friendly water bottle"
Context: target_audience="millennials", features=["plastic-free", "insulated"]
```

**Orchestrator Analysis:**
```
🎯 ORCHESTRATOR ANALYSIS
================================================================================
This task requires different marketing angles. I recommend:

1. Feature-focused technical approach (specifications, materials)
2. Lifestyle-emotional approach (values, sustainability)
3. Practical benefits approach (everyday use, cost savings)

Each serves different decision-making styles.
```

**Worker Results:**
```
📊 RESULTS
================================================================================

Approach 1: TECHNICAL-SPECIFICATIONS
--------------------------------------------------------------------------------
Premium 18/8 stainless steel construction
Double-wall vacuum insulation (24hr cold/12hr hot)
100% BPA-free, 95% recyclable materials
Lifetime warranty, 15+ year lifespan
...

Approach 2: LIFESTYLE-EMOTIONAL
--------------------------------------------------------------------------------
More Than Hydration. A Daily Ritual of Change.

Every sip is a choice for the planet. Join millions who understand
that sustainability isn't about perfection—it's about progress.
...

Approach 3: BENEFIT-PRACTICAL
--------------------------------------------------------------------------------
Tired of lukewarm coffee by mid-morning? The EcoFlow Bottle:
✓ Keeps drinks at perfect temperature all day
✓ Saves $500+/year vs. disposable bottles
✓ Leak-proof, fits cup holders, dishwasher safe
...
```

### When to Use
- ✅ Need multiple perspectives on same task
- ✅ Can't predict best approach in advance
- ✅ Want to compare different strategies
- ✅ Content generation, analysis, creative writing
- ❌ Simple single-output tasks
- ❌ Latency-critical applications
- ❌ Subtasks are always the same

---

## 🧠 Extended Thinking Examples

### Basic Thinking
```bash
# Solve math problems with visible reasoning
python thinking_problem_solver.py --domain math \
  "Calculate 17^3 + 5 factorial"

# Logic puzzles
python thinking_problem_solver.py --domain logic \
  "If 5 machines make 5 widgets in 5 minutes..."

# Interactive mode
python thinking_problem_solver.py -i --domain code
```

### Thinking + Tools
```bash
# Calculator agent
python thinking_agent_builder.py calculator \
  "Calculate 7! + 23^2"

# Data analysis
python thinking_agent_builder.py analyst \
  "What was our Q2 average revenue?"

# Verbose mode (see all tool calls)
python thinking_agent_builder.py --verbose analyst \
  "Compare January and June sales"
```

---

## 🔗 Combining Patterns

### Pattern 1: Metaprompt → Custom Agent

```bash
# Step 1: Generate prompt for financial analysis
python metaprompt_tool.py \
  "Analyze financial statements and provide investment recommendations" \
  --variables "FINANCIALS COMPANY_NAME" \
  --output financial_analyzer.txt

# Step 2: Use prompt with thinking agent
# (Copy prompt into custom agent code)
```

### Pattern 2: Orchestrator → Thinking Workers

```python
# Orchestrator determines approaches
# Each worker uses extended thinking
# Results combined with thinking transparency
```

### Pattern 3: Metaprompt → Orchestrator

```bash
# Step 1: Generate orchestrator prompt
python metaprompt_tool.py \
  "Break down research questions into analytical perspectives"

# Step 2: Use generated prompt as orchestrator template
```

---

## 📊 Real-World Examples

### Example 1: Content Marketing Suite

**Problem:** Need various marketing content for product launch

**Solution:**
```bash
# Generate multiple content types
python orchestrator_workers.py marketing \
  "Create content for smart home device launch" \
  --context "target=tech-savvy homeowners" "price_point=premium"

# Outputs:
# - Social media posts (emotional/visual)
# - Email campaign (benefit-focused)
# - Product page copy (technical/detailed)
# - Press release (newsworthy angle)
```

### Example 2: Research Assistant

**Problem:** Need comprehensive analysis from multiple angles

**Solution:**
```bash
# Multi-perspective analysis
python orchestrator_workers.py research \
  "Evaluate blockchain for supply chain management" \
  --context "industry=manufacturing" "scale=enterprise"

# Outputs:
# - Technical feasibility analysis
# - Cost-benefit analysis
# - Security and compliance review
# - Implementation roadmap
```

### Example 3: Financial Analysis

**Problem:** Analyze company financials with reasoning

**Solution:**
```bash
# Use thinking agent for financial ratios
python thinking_agent_builder.py analyst \
  "Calculate and interpret all financial ratios for Q1-Q4" \
  --thinking-budget 5000

# Shows:
# 🧠 THINKING: "I need to calculate liquidity, profitability..."
# 🔧 TOOL: query_sales("Q1") → $50K
# ✓ ANSWER: "ROE of 18.5% indicates strong performance..."
```

### Example 4: Custom Prompt Library

**Problem:** Need consistent prompts for recurring tasks

**Solution:**
```bash
# Build library of prompts
python metaprompt_tool.py "Review code for security issues" -o code_review.txt
python metaprompt_tool.py "Summarize meeting notes" -o meeting_summary.txt
python metaprompt_tool.py "Draft customer support responses" -o support_agent.txt

# Use in production with consistent quality
```

---

## 🎨 Use Case Matrix

| Pattern | Best For | Complexity | Speed | Cost |
|---------|----------|------------|-------|------|
| Metaprompt | Prompt engineering | Low | Fast | $ |
| Orchestrator-Workers | Multiple perspectives | Medium | Slow | $$$ |
| Extended Thinking | Complex reasoning | Medium | Medium | $$ |
| Thinking + Tools | Multi-step tasks | High | Slow | $$$ |

**Legend:**
- Speed: Fast (<5s), Medium (5-20s), Slow (20s+)
- Cost: $ (1-2 calls), $$ (3-5 calls), $$$ (6+ calls)

---

## 💡 Best Practices

### Metaprompt
- ✅ Clearly describe what you want accomplished
- ✅ Specify if task needs reasoning/examples
- ✅ Test generated prompts with real inputs
- ✅ Iterate on task description if output isn't ideal
- ❌ Don't over-specify - let metaprompt determine structure

### Orchestrator-Workers
- ✅ Provide rich context for orchestrator
- ✅ Use when approaches aren't predictable
- ✅ Review orchestrator reasoning to validate
- ✅ Consider parallel execution for speed
- ❌ Don't use for simple tasks
- ❌ Don't pre-define what subtasks should be

### Extended Thinking
- ✅ Start with 2000-3000 token budgets
- ✅ Use for problems requiring careful analysis
- ✅ Review thinking to debug reasoning
- ✅ Adjust budget based on complexity
- ❌ Don't use for simple lookups
- ❌ Don't expect thinking after tool results

### Thinking + Tools
- ✅ Preserve thinking blocks in conversation
- ✅ Provide clear tool descriptions
- ✅ Use verbose mode for debugging
- ✅ Handle tool errors gracefully
- ❌ Don't modify thinking blocks
- ❌ Don't expect new thinking after every turn

---

## 🔧 Customization

### Custom Orchestrator Template

```python
CUSTOM_ORCHESTRATOR = """
Analyze this {domain} task: {task}

Context: {context_str}

Break into 2-4 approaches considering:
- {consideration_1}
- {consideration_2}

<analysis>
Your reasoning here
</analysis>

<tasks>
    <task>
    <type>approach-name</type>
    <description>Specific instructions</description>
    </task>
</tasks>
"""
```

### Custom Thinking Agent

```python
from thinking_agent_builder import ThinkingAgent

agent = ThinkingAgent(
    name="Custom Agent",
    system_prompt="You are a specialist in...",
    thinking_budget=4000
)

# Add domain-specific tools
def my_tool(param: str) -> dict:
    return {"result": "..."}

agent.add_tool(
    name="my_tool",
    description="What it does",
    parameters={"param": {"type": "string", "description": "..."}},
    function=my_tool
)

result = agent.run("Your task")
```

---

## 📈 Performance Tips

### Speed Optimization
```python
# Use faster models for workers
orchestrator.model = "claude-sonnet-4-5"  # Orchestrator
worker.model = "claude-haiku-4-5"         # Workers (faster, cheaper)

# Parallel execution
import asyncio
results = await asyncio.gather(*[worker.run(task) for task in tasks])
```

### Cost Optimization
```python
# Adjust thinking budgets
agent.thinking_budget = 1024  # Minimum for simple tasks
agent.thinking_budget = 10000 # Complex analysis

# Limit orchestrator subtasks
"Break into 2-3 approaches (not more)"
```

### Quality Optimization
```python
# Use Opus for orchestrator, Sonnet for workers
orchestrator_model = "claude-opus-4-5"    # Best reasoning
worker_model = "claude-sonnet-4-5"        # Good quality

# Increase thinking budget for critical tasks
critical_agent.thinking_budget = 16000
```

---

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY not found"
```bash
export ANTHROPIC_API_KEY="your-key-here"
# Or add to ~/.bashrc or ~/.zshrc
```

### "Thinking blocks must be preserved"
```python
# ❌ Wrong - missing thinking
conversation.append({"role": "assistant", "content": [tool_use]})

# ✅ Correct - includes thinking
conversation.append({"role": "assistant", "content": response.content})
```

### "Orchestrator returns invalid XML"
```python
# Add validation and retry
if not extract_xml(response, "tasks"):
    # Retry with clarified prompt
    prompt += "\n\nRemember to use XML tags exactly as shown."
```

### "Worker returns empty response"
```python
# Add fallback handling
if not worker_content.strip():
    worker_content = "[Error: Worker returned empty response]"
```

---

## 📚 Additional Resources

**Documentation:**
- [Extended Thinking Docs](https://docs.claude.com/en/docs/build-with-claude/extended-thinking)
- [Prompt Engineering Guide](https://docs.anthropic.com/en/docs/prompt-engineering)
- [Agent SDK Overview](https://docs.claude.com/en/api/agent-sdk/overview)

**Cookbooks:**
- [Claude Cookbooks Repo](https://github.com/anthropics/claude-cookbooks)
- Skills examples
- Workflow patterns

**This Repository:**
- `README_THINKING.md` - Extended thinking basics
- `README_THINKING_TOOLS.md` - Thinking + tools
- `README_ADVANCED_PATTERNS.md` - This file

---

## 🎯 Next Steps

1. **Try the examples**
   ```bash
   python metaprompt_tool.py --interactive
   python orchestrator_workers.py marketing "Your task"
   python thinking_problem_solver.py -i
   ```

2. **Build custom agents**
   - Modify orchestrator prompts for your domain
   - Add domain-specific tools
   - Create specialized worker templates

3. **Combine patterns**
   - Use metaprompt to generate orchestrator templates
   - Add thinking to workers for transparency
   - Build end-to-end workflows

4. **Optimize for production**
   - Implement parallel execution
   - Add error handling and retries
   - Monitor costs and performance
   - Cache common patterns

---

## 🤝 Contributing

Suggestions for improvements:
- Additional orchestrator templates
- More domain-specific examples
- Performance optimizations
- Integration patterns

---

## 📝 License

MIT License - Use these patterns freely in your projects!

---

**Happy building! 🚀**
