# Extended Thinking with Tool Use

Comprehensive examples and tools for combining Claude's **extended thinking** with **tool/function calling**, providing transparency into AI reasoning about when and how to use tools.

## What's Included

### 1. `thinking_with_tools_examples.py`
Three complete examples demonstrating thinking + tools:

- **Calculator Tools** - Math operations with visible reasoning
- **Data Analysis** - Multi-step data queries with analysis
- **File Operations** - File system navigation with strategic thinking

### 2. `thinking_agent_builder.py`
A framework for building custom agents with thinking + tools:

- **Calculator Agent** - Math and factorial operations
- **Research Agent** - Knowledge base lookups
- **Data Analyst Agent** - Sales data analysis

## Key Concepts

### Extended Thinking + Tools = Transparent AI

**Without Extended Thinking:**
```
User: "Calculate 17^3 + 5!"
Assistant: [calls tools] → "The answer is 5033"
```

**With Extended Thinking:**
```
User: "Calculate 17^3 + 5!"

🧠 THINKING:
"I need to calculate two things:
1. 17^3 (17 cubed)
2. 5! (5 factorial)
Then add them together.

I'll use the calculate tool for 17^3 and
the factorial tool for 5!..."

🔧 TOOL: calculate(17^3) → 4913
🔧 TOOL: factorial(5) → 120

✓ ANSWER: 17^3 + 5! = 4913 + 120 = 5033
```

## Setup

```bash
# API key should already be set
export ANTHROPIC_API_KEY="your-key-here"

# anthropic SDK should already be installed
pip install anthropic
```

## Usage

### Running Examples

```bash
# Example 1: Calculator with thinking
python thinking_with_tools_examples.py

# Or edit to run specific examples:
# - example_1_calculator_with_thinking()
# - example_2_data_analysis_with_thinking()
# - example_3_file_operations_with_thinking()
```

### Using the Agent Builder

**Calculator Agent:**
```bash
# With thinking visible
python thinking_agent_builder.py calculator "Calculate 17^3 + 5 factorial"

# Hide thinking (just show results)
python thinking_agent_builder.py --no-thinking calculator "Quick: 23 * 17"

# Verbose mode (show all details)
python thinking_agent_builder.py --verbose calculator "What's 100 factorial?"
```

**Research Agent:**
```bash
# Look up information
python thinking_agent_builder.py research "Tell me about Python"

# Compare topics
python thinking_agent_builder.py research "Compare Python and JavaScript"

# Search and analyze
python thinking_agent_builder.py research "Find all programming languages"
```

**Data Analyst Agent:**
```bash
# Query specific months
python thinking_agent_builder.py analyst "What were our January sales?"

# Calculate averages
python thinking_agent_builder.py analyst "What was our average Q1 revenue?"

# Multi-step analysis
python thinking_agent_builder.py analyst "Compare revenue trends for Jan-Mar"

# Complex queries
python thinking_agent_builder.py analyst "Which month had the highest revenue per customer?"
```

## Building Custom Agents

```python
from thinking_agent_builder import ThinkingAgent

# Create agent
agent = ThinkingAgent(
    name="My Agent",
    system_prompt="You are a helpful assistant that...",
    thinking_budget=3000
)

# Add custom tools
def my_tool(param1: str, param2: int) -> dict:
    # Your tool logic here
    return {"result": "some value"}

agent.add_tool(
    name="my_tool",
    description="What this tool does",
    parameters={
        "param1": {
            "type": "string",
            "description": "First parameter"
        },
        "param2": {
            "type": "integer",
            "description": "Second parameter"
        }
    },
    function=my_tool
)

# Run agent
result = agent.run("Your task here")
print(result["answer"])
```

## Important Notes

### Thinking Block Preservation
**Critical:** When using tools, you MUST preserve thinking blocks in the conversation:

```python
# ❌ WRONG - Missing thinking blocks
conversation.append({
    "role": "assistant",
    "content": [tool_use_block]  # Missing thinking!
})

# ✅ CORRECT - Include ALL blocks
conversation.append({
    "role": "assistant",
    "content": response.content  # Includes thinking + tools
})
```

### Thinking Appears BEFORE Tool Use
- Thinking blocks show reasoning about which tools to use
- NO new thinking blocks after receiving tool results
- New thinking only appears on the next user turn

### Multi-Turn Tool Conversations
```python
Turn 1: User asks question
Turn 2: [Thinking] + [Tool Use]
Turn 3: [Tool Results]
Turn 4: [Tool Use again] (no new thinking)
Turn 5: [Tool Results]
Turn 6: [Final Answer] (no new thinking)
```

## Example Output

```
🧠 THINKING:
==================================================
The user wants to calculate the average Q1 revenue.
Q1 includes January, February, and March.

I need to:
1. Query sales for January
2. Query sales for February
3. Query sales for March
4. Extract revenue values
5. Calculate the average

Let me start by querying January...
==================================================

🔧 TOOL: query_sales
   Input: {"month": "January"}
   Result: {"revenue": 50000, "units": 500, "customers": 120}

🔧 TOOL: query_sales
   Input: {"month": "February"}
   Result: {"revenue": 65000, "units": 650, "customers": 145}

🔧 TOOL: query_sales
   Input: {"month": "March"}
   Result: {"revenue": 72000, "units": 700, "customers": 160}

🔧 TOOL: calculate_stats
   Input: {"values": [50000, 65000, 72000], "stat_type": "average"}
   Result: {"result": 62333.33}

✓ FINAL ANSWER:
==================================================
Based on the data:
- January: $50,000
- February: $65,000
- March: $72,000

Your Q1 average monthly revenue was **$62,333.33**.

This shows strong growth throughout Q1, with March
being the strongest month at $72,000.
==================================================
```

## Benefits

### Transparency
✓ See reasoning about tool selection
✓ Understand multi-step problem solving
✓ Debug tool usage issues
✓ Learn AI decision-making process

### Accuracy
✓ Careful reasoning before tool calls
✓ Verification of tool results
✓ Strategic planning for complex tasks
✓ Error detection and handling

### Debugging
✓ Track tool call sequences
✓ Identify incorrect tool usage
✓ Understand conversation flow
✓ Validate tool results

## Advanced Features

### Adjusting Thinking Budget
```bash
# More thinking for complex tasks
python thinking_agent_builder.py \
  --thinking-budget 5000 \
  analyst "Complex multi-step analysis..."
```

### Combining Multiple Agents
```python
# Use different agents for different tasks
calc_agent = create_calculator_agent()
research_agent = create_research_agent()

# Complex workflow
calc_result = calc_agent.run("Calculate X")
research_result = research_agent.run(f"Research {calc_result}")
```

### Custom Tool Patterns

**Database Query Tool:**
```python
def query_db(table: str, conditions: dict) -> dict:
    # Execute SQL query
    return {"rows": [...]}

agent.add_tool("query_db", "Query database", {...}, query_db)
```

**API Call Tool:**
```python
def api_call(endpoint: str, method: str, data: dict) -> dict:
    # Make HTTP request
    return {"status": 200, "data": {...}}

agent.add_tool("api_call", "Call external API", {...}, api_call)
```

**File System Tool:**
```python
def read_file(path: str) -> dict:
    with open(path) as f:
        return {"content": f.read()}

agent.add_tool("read_file", "Read file contents", {...}, read_file)
```

## Common Patterns

### Pattern 1: Research → Calculate
```python
# Agent first researches, then calculates
"Find the population of Tokyo and calculate density"
→ [Think] → [Lookup Tokyo] → [Calculate] → [Answer]
```

### Pattern 2: Multi-Source Data Aggregation
```python
# Query multiple sources, then aggregate
"Compare Q1 revenue across all regions"
→ [Think] → [Query Region 1] → [Query Region 2] →
   [Query Region 3] → [Aggregate] → [Answer]
```

### Pattern 3: Iterative Refinement
```python
# Search → Analyze → Search Again
"Find mentions of 'revenue' and summarize context"
→ [Think] → [Search] → [Read Files] → [Analyze] → [Answer]
```

## Troubleshooting

**Error: "thinking blocks must be preserved"**
```python
# Make sure to include ALL content blocks
conversation.append({
    "role": "assistant",
    "content": response.content  # Not just tool_use blocks!
})
```

**No thinking shown after tool results**
```
This is expected! Thinking only appears:
- Before initial tool calls
- On new user turns (not tool results)
```

**Tool called incorrectly**
```
Check the thinking block to see reasoning.
This helps debug tool selection logic.
```

## Cost Considerations

- Thinking tokens are billed as **output tokens**
- Each tool call adds overhead
- Complex multi-tool tasks can be expensive
- Use `--no-thinking` for production if needed

**Typical costs:**
- Simple query: ~2K-4K tokens
- Multi-step analysis: ~5K-10K tokens
- Complex research: ~10K-20K tokens

## Resources

- [Extended Thinking Docs](https://docs.claude.com/en/docs/build-with-claude/extended-thinking)
- [Tool Use Guide](https://docs.anthropic.com/en/docs/tool-use)
- [Agent SDK Docs](https://docs.claude.com/en/api/agent-sdk/overview)

## Next Steps

1. Try the pre-built examples
2. Use agent templates for common tasks
3. Build custom agents for your use cases
4. Combine thinking + tools in your applications

Happy building! 🤖🧠
