#!/usr/bin/env python3
"""
Thinking Agent Builder

A tool for creating AI agents that combine extended thinking with custom tools.
Great for building transparent, reasoning-capable assistants for specific domains.
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any, Callable
from anthropic import Anthropic


class ThinkingAgent:
    """Agent with extended thinking and custom tools."""

    def __init__(
        self,
        name: str = "Assistant",
        system_prompt: str = "",
        api_key: str = None,
        thinking_budget: int = 3000,
        max_tokens: int = 4000,
        show_thinking: bool = True,
        verbose: bool = False
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-5"
        self.thinking_budget = thinking_budget
        self.max_tokens = max_tokens
        self.show_thinking = show_thinking
        self.verbose = verbose

        self.tools = []
        self.tool_functions = {}

    def add_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        function: Callable
    ):
        """
        Add a tool to the agent.

        Args:
            name: Tool name
            description: What the tool does
            parameters: JSON schema for tool parameters
            function: Python function to execute
        """
        tool_schema = {
            "name": name,
            "description": description,
            "input_schema": {
                "type": "object",
                "properties": parameters,
                "required": list(parameters.keys())
            }
        }

        self.tools.append(tool_schema)
        self.tool_functions[name] = function

        if self.verbose:
            print(f"✓ Added tool: {name}")

    def run(self, prompt: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Run the agent with a prompt.

        Args:
            prompt: User's request
            max_iterations: Max tool call iterations

        Returns:
            Dictionary with final answer and metadata
        """
        conversation = [{"role": "user", "content": prompt}]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            thinking={
                "type": "enabled",
                "budget_tokens": self.thinking_budget
            },
            system=self.system_prompt if self.system_prompt else None,
            tools=self.tools if self.tools else None,
            messages=conversation
        )

        iteration = 0
        tool_calls_made = []

        while response.stop_reason == "tool_use" and iteration < max_iterations:
            iteration += 1

            if self.verbose:
                print(f"\n{'='*60}")
                print(f"Iteration {iteration}")
                print('='*60)

            # Show thinking process
            for block in response.content:
                if block.type == "thinking" and self.show_thinking:
                    print("\n🧠 THINKING:")
                    print("-" * 60)
                    print(block.thinking)
                    print("-" * 60)

            # Add assistant response to conversation
            conversation.append({
                "role": "assistant",
                "content": response.content
            })

            # Execute tools
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    if self.verbose or not self.show_thinking:
                        print(f"\n🔧 TOOL: {tool_name}")
                        print(f"   Input: {json.dumps(tool_input, indent=2)}")

                    # Execute the tool
                    if tool_name in self.tool_functions:
                        try:
                            result = self.tool_functions[tool_name](**tool_input)
                        except Exception as e:
                            result = {"error": str(e)}
                    else:
                        result = {"error": f"Unknown tool: {tool_name}"}

                    if self.verbose or not self.show_thinking:
                        print(f"   Result: {json.dumps(result, indent=2)}")

                    tool_calls_made.append({
                        "tool": tool_name,
                        "input": tool_input,
                        "result": result
                    })

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })

            # Add tool results to conversation
            conversation.append({
                "role": "user",
                "content": tool_results
            })

            # Continue conversation
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                thinking={
                    "type": "enabled",
                    "budget_tokens": self.thinking_budget
                },
                system=self.system_prompt if self.system_prompt else None,
                tools=self.tools if self.tools else None,
                messages=conversation
            )

        # Extract final answer
        final_answer = ""
        for block in response.content:
            if block.type == "text":
                final_answer = block.text

        if self.show_thinking or self.verbose:
            print("\n" + "="*60)
            print("✓ FINAL ANSWER:")
            print("="*60)
            print(final_answer)

        return {
            "answer": final_answer,
            "tool_calls": tool_calls_made,
            "iterations": iteration,
            "conversation": conversation
        }


# Pre-built agent templates
def create_calculator_agent(show_thinking=True, verbose=False):
    """Create an agent with calculator tools."""
    agent = ThinkingAgent(
        name="Calculator Agent",
        system_prompt="""You are a helpful calculator assistant.
When doing calculations:
1. Use the provided tools for complex arithmetic
2. Show your reasoning step-by-step
3. Verify your results make sense""",
        show_thinking=show_thinking,
        verbose=verbose
    )

    def calculate(expression: str) -> Dict[str, Any]:
        """Evaluate a mathematical expression."""
        try:
            # Only allow safe operations
            allowed = set("0123456789+-*/().^ ")
            if not all(c in allowed for c in expression):
                return {"error": "Invalid characters in expression"}

            expression = expression.replace("^", "**")
            result = eval(expression)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}

    def factorial(n: int) -> Dict[str, Any]:
        """Calculate factorial of n."""
        if n < 0:
            return {"error": "Factorial undefined for negative numbers"}
        if n > 100:
            return {"error": "Number too large"}

        result = 1
        for i in range(2, n + 1):
            result *= i
        return {"result": result}

    agent.add_tool(
        name="calculate",
        description="Evaluate a mathematical expression",
        parameters={
            "expression": {
                "type": "string",
                "description": "Math expression (e.g., '17 * 23 + 45')"
            }
        },
        function=calculate
    )

    agent.add_tool(
        name="factorial",
        description="Calculate factorial (n!)",
        parameters={
            "n": {
                "type": "integer",
                "description": "Number to calculate factorial for"
            }
        },
        function=factorial
    )

    return agent


def create_research_agent(show_thinking=True, verbose=False):
    """Create an agent with research/lookup tools."""
    agent = ThinkingAgent(
        name="Research Agent",
        system_prompt="""You are a research assistant that helps find and analyze information.
Use the available tools to look up data and provide comprehensive answers.""",
        show_thinking=show_thinking,
        verbose=verbose
    )

    # Mock knowledge base
    knowledge_base = {
        "python": {
            "type": "programming language",
            "created": 1991,
            "creator": "Guido van Rossum",
            "paradigm": "multi-paradigm"
        },
        "javascript": {
            "type": "programming language",
            "created": 1995,
            "creator": "Brendan Eich",
            "paradigm": "multi-paradigm"
        },
        "claude": {
            "type": "AI assistant",
            "creator": "Anthropic",
            "capabilities": ["conversation", "analysis", "coding"]
        }
    }

    def lookup(topic: str) -> Dict[str, Any]:
        """Look up information about a topic."""
        topic_lower = topic.lower()
        if topic_lower in knowledge_base:
            return knowledge_base[topic_lower]
        return {"error": f"No information found for '{topic}'"}

    def search(query: str) -> Dict[str, Any]:
        """Search for topics matching a query."""
        matches = []
        query_lower = query.lower()
        for topic, info in knowledge_base.items():
            if query_lower in topic or query_lower in str(info).lower():
                matches.append(topic)
        return {"matches": matches}

    agent.add_tool(
        name="lookup",
        description="Look up detailed information about a topic",
        parameters={
            "topic": {
                "type": "string",
                "description": "Topic to look up"
            }
        },
        function=lookup
    )

    agent.add_tool(
        name="search",
        description="Search for topics matching a query",
        parameters={
            "query": {
                "type": "string",
                "description": "Search query"
            }
        },
        function=search
    )

    return agent


def create_data_analyst_agent(show_thinking=True, verbose=False):
    """Create an agent with data analysis tools."""
    agent = ThinkingAgent(
        name="Data Analyst",
        system_prompt="""You are a data analyst assistant.
Analyze data carefully and provide insights with supporting evidence.
Use the tools to query and process data.""",
        show_thinking=show_thinking,
        verbose=verbose,
        thinking_budget=4000
    )

    # Mock database
    sales_data = {
        "January": {"revenue": 50000, "units": 500, "customers": 120},
        "February": {"revenue": 65000, "units": 650, "customers": 145},
        "March": {"revenue": 72000, "units": 700, "customers": 160},
        "April": {"revenue": 68000, "units": 680, "customers": 155},
        "May": {"revenue": 75000, "units": 750, "customers": 170},
        "June": {"revenue": 82000, "units": 820, "customers": 185}
    }

    def query_sales(month: str) -> Dict[str, Any]:
        """Query sales data for a specific month."""
        return sales_data.get(month, {"error": f"No data for {month}"})

    def calculate_stats(values: List[float], stat_type: str) -> Dict[str, Any]:
        """Calculate statistics on a list of values."""
        if not values:
            return {"error": "Empty values list"}

        if stat_type == "average":
            return {"result": sum(values) / len(values)}
        elif stat_type == "sum":
            return {"result": sum(values)}
        elif stat_type == "min":
            return {"result": min(values)}
        elif stat_type == "max":
            return {"result": max(values)}
        else:
            return {"error": f"Unknown stat type: {stat_type}"}

    agent.add_tool(
        name="query_sales",
        description="Query sales data for a specific month",
        parameters={
            "month": {
                "type": "string",
                "description": "Month name (e.g., 'January')"
            }
        },
        function=query_sales
    )

    agent.add_tool(
        name="calculate_stats",
        description="Calculate statistics (average, sum, min, max) on values",
        parameters={
            "values": {
                "type": "array",
                "items": {"type": "number"},
                "description": "List of numbers"
            },
            "stat_type": {
                "type": "string",
                "description": "Type of statistic: 'average', 'sum', 'min', or 'max'"
            }
        },
        function=calculate_stats
    )

    return agent


def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(
        description="Build and run AI agents with extended thinking and custom tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calculator agent
  python thinking_agent_builder.py calculator "What's 17^3 + 23^2?"

  # Research agent
  python thinking_agent_builder.py research "Tell me about Python and JavaScript"

  # Data analyst
  python thinking_agent_builder.py analyst "What was our Q1 average revenue?"

  # Hide thinking process
  python thinking_agent_builder.py --no-thinking calculator "Quick: 5 factorial"

  # Verbose mode (show all details)
  python thinking_agent_builder.py --verbose analyst "Compare Jan and Feb sales"
        """
    )

    parser.add_argument(
        "agent_type",
        choices=["calculator", "research", "analyst"],
        help="Type of agent to create"
    )

    parser.add_argument(
        "prompt",
        help="Task for the agent"
    )

    parser.add_argument(
        "--no-thinking",
        action="store_true",
        help="Hide the thinking process"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed execution information"
    )

    parser.add_argument(
        "--thinking-budget",
        type=int,
        default=3000,
        help="Thinking token budget (default: 3000)"
    )

    args = parser.parse_args()

    # Create the appropriate agent
    show_thinking = not args.no_thinking

    if args.agent_type == "calculator":
        agent = create_calculator_agent(show_thinking, args.verbose)
    elif args.agent_type == "research":
        agent = create_research_agent(show_thinking, args.verbose)
    elif args.agent_type == "analyst":
        agent = create_data_analyst_agent(show_thinking, args.verbose)
    else:
        print(f"Unknown agent type: {args.agent_type}", file=sys.stderr)
        sys.exit(1)

    # Update thinking budget if specified
    agent.thinking_budget = args.thinking_budget

    # Run the agent
    try:
        print(f"\n🤖 {agent.name}")
        print("="*60)
        result = agent.run(args.prompt)

        if args.verbose:
            print(f"\n📊 METADATA:")
            print(f"   Tool calls: {len(result['tool_calls'])}")
            print(f"   Iterations: {result['iterations']}")

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
