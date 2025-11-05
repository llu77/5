# Extended Thinking Examples & Tool

This directory contains examples and a practical tool for using Claude's **extended thinking** feature with custom system prompts.

## What's Included

### 1. `extended_thinking_examples.py`
Demonstrates different use cases combining system prompts with extended thinking:

- **Financial Analysis** - Investment decisions with thorough reasoning
- **Code Review** - Security and bug analysis with detailed thinking
- **Medical Reasoning** - Differential diagnosis (educational)
- **Comparison** - Side-by-side with/without thinking

### 2. `thinking_problem_solver.py`
A full-featured CLI tool for solving complex problems using extended thinking.

## Setup

```bash
# Make sure you have your API key set
export ANTHROPIC_API_KEY="your-api-key-here"

# Install anthropic SDK if needed
pip install anthropic
```

## Usage

### Running Examples

```bash
# Run all examples
python extended_thinking_examples.py

# Or edit the file to run specific examples:
# - example_1_financial_analysis()
# - example_2_code_review()
# - example_3_medical_reasoning()
# - example_4_compare_with_without_thinking()
```

### Using the Problem Solver Tool

**Basic usage:**
```bash
python thinking_problem_solver.py "What is the 20th Fibonacci number?"
```

**With domain-specific prompts:**
```bash
# Math problems
python thinking_problem_solver.py --domain math "Solve: x^2 + 5x + 6 = 0"

# Code review
python thinking_problem_solver.py --domain code "Review this: def divide(a,b): return a/b"

# Logic puzzles
python thinking_problem_solver.py --domain logic "Three switches control three bulbs..."

# Strategic planning
python thinking_problem_solver.py --domain strategy "Should we prioritize growth or profitability?"

# Financial analysis
python thinking_problem_solver.py --domain financial "Calculate NPV of a 5-year project with..."
```

**Advanced options:**
```bash
# Stream the response (see thinking in real-time)
python thinking_problem_solver.py --stream "Explain quantum entanglement"

# Adjust thinking budget (1024-32000 tokens)
python thinking_problem_solver.py --thinking-budget 5000 "Complex problem here"

# Hide thinking process (just show answer)
python thinking_problem_solver.py --no-thinking "Quick calculation: 17 * 23"

# Interactive mode
python thinking_problem_solver.py --interactive
```

**Interactive mode example:**
```bash
$ python thinking_problem_solver.py -i --domain math

🤔 Thinking Problem Solver (Interactive Mode)
Type 'quit' or 'exit' to stop

📝 Enter problem: What is 15^3?

🧠 THINKING PROCESS
==================================================
Let me calculate 15^3, which means 15 × 15 × 15...
==================================================

✓ SOLUTION:
15^3 = 3,375

📝 Enter problem: quit
Goodbye!
```

## Domains Available

Each domain has a specialized system prompt:

- **general** - Default, versatile reasoning
- **math** - Step-by-step calculations with verification
- **code** - Bug detection, security, best practices
- **logic** - Systematic constraint analysis
- **strategy** - Scenario planning, risk analysis
- **medical** - Differential diagnosis (educational only)
- **financial** - Investment analysis, calculations

## Key Features

### Extended Thinking Benefits
✓ **Transparency** - See Claude's reasoning process
✓ **Accuracy** - More careful analysis on complex problems
✓ **Debugging** - Understand how conclusions were reached
✓ **Learning** - Watch problem-solving approaches

### Tool Features
✓ Domain-specific system prompts
✓ Streaming support
✓ Interactive mode for multiple problems
✓ Adjustable thinking budget
✓ Toggle thinking visibility

## Tips for Best Results

1. **Start with 2000-3000 thinking tokens** for most problems
2. **Use domain-specific prompts** for specialized problems
3. **Stream responses** for long problems to see progress
4. **Adjust thinking budget** based on problem complexity:
   - Simple: 1024-2000 tokens
   - Medium: 2000-5000 tokens
   - Complex: 5000-10000+ tokens

## Example Output

```
🧠 THINKING PROCESS
==================================================
This is a classic logic puzzle. Let me work through it step by step:

1. First, I'll identify the constraints...
2. Next, I'll consider what we know about each person...
3. Then I'll eliminate impossibilities...
...
==================================================

✓ SOLUTION:
Based on the logical deduction above, the answer is...
```

## Cost Considerations

- Extended thinking tokens are billed as **output tokens**
- Typical cost: ~3-5x more than standard responses
- Worth it for complex problems requiring accuracy
- Use `--no-thinking` for simple queries to save tokens

## Troubleshooting

**Error: "ANTHROPIC_API_KEY not found"**
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

**Error: "thinking budget too small"**
```bash
# Minimum is 1024 tokens
python thinking_problem_solver.py --thinking-budget 1024 "problem"
```

**Want to see raw API response?**
- Modify the code to print `response` object
- Check `response.usage` for token counts

## Resources

- [Extended Thinking Docs](https://docs.claude.com/en/docs/build-with-claude/extended-thinking)
- [Claude Cookbooks](https://github.com/anthropics/claude-cookbooks)
- [API Reference](https://docs.anthropic.com/en/api/messages)

## Next Steps

1. Try the examples to see thinking in action
2. Use the tool for your own complex problems
3. Customize system prompts for your specific use cases
4. Integrate into your own applications

Happy problem solving! 🧠
