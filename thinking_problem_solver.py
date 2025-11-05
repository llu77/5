#!/usr/bin/env python3
"""
Thinking Problem Solver Tool

A CLI tool that uses Claude's extended thinking to solve complex problems.
Great for math, logic puzzles, debugging, strategic planning, etc.
"""

import os
import sys
import argparse
from anthropic import Anthropic


class ThinkingProblemSolver:
    """Problem solver using Claude's extended thinking."""

    def __init__(self, api_key=None):
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-5"

    def solve(
        self,
        problem: str,
        domain: str = "general",
        thinking_budget: int = 3000,
        max_tokens: int = 4000,
        show_thinking: bool = True,
        stream: bool = False
    ):
        """
        Solve a problem using extended thinking.

        Args:
            problem: The problem to solve
            domain: Problem domain (math, code, logic, strategy, medical, financial)
            thinking_budget: Tokens allocated for thinking (min 1024)
            max_tokens: Maximum response tokens
            show_thinking: Whether to show the thinking process
            stream: Whether to stream the response
        """
        # Domain-specific system prompts
        system_prompts = {
            "math": """You are a mathematics expert. When solving problems:
1. Show all steps in your calculations
2. Check your work for arithmetic errors
3. Consider multiple solution approaches
4. Verify your final answer makes sense
Think carefully and methodically.""",

            "code": """You are a senior software engineer and debugging expert. When analyzing code:
1. Identify bugs, security issues, and performance problems
2. Consider edge cases and error handling
3. Think about maintainability and best practices
4. Test your reasoning with example inputs
Think through all possibilities carefully.""",

            "logic": """You are a logic and reasoning expert. When solving puzzles:
1. Identify all constraints and rules
2. Consider contradictions and impossibilities
3. Work through edge cases systematically
4. Verify your solution satisfies all conditions
Think step-by-step through the logic.""",

            "strategy": """You are a strategic advisor. When analyzing situations:
1. Consider multiple scenarios and outcomes
2. Identify key assumptions and uncertainties
3. Evaluate risks and opportunities
4. Think through second-order effects
Provide thorough strategic analysis.""",

            "medical": """You are a medical education assistant (for educational purposes only).
When analyzing cases:
1. Build a comprehensive differential diagnosis
2. Consider prevalence and key distinguishing features
3. Think about diagnostic tests and their utility
4. Reason through the most likely diagnosis
Note: This is for learning, not real medical advice.""",

            "financial": """You are a financial analyst. When analyzing scenarios:
1. Break down calculations step-by-step
2. Consider multiple perspectives and scenarios
3. Identify key assumptions and risks
4. Check all arithmetic carefully
Provide thorough financial analysis.""",

            "general": """You are a helpful AI assistant with strong reasoning capabilities.
Think carefully through problems before providing your answer.
Show your work and explain your reasoning."""
        }

        system_prompt = system_prompts.get(domain, system_prompts["general"])

        if stream:
            return self._solve_streaming(
                problem, system_prompt, thinking_budget, max_tokens, show_thinking
            )
        else:
            return self._solve_standard(
                problem, system_prompt, thinking_budget, max_tokens, show_thinking
            )

    def _solve_standard(self, problem, system_prompt, thinking_budget, max_tokens, show_thinking):
        """Standard (non-streaming) solve."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            thinking={
                "type": "enabled",
                "budget_tokens": thinking_budget
            },
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": problem
            }]
        )

        result = {
            "thinking_blocks": [],
            "answer": "",
            "redacted_blocks": []
        }

        for block in response.content:
            if block.type == "thinking":
                result["thinking_blocks"].append(block.thinking)
                if show_thinking:
                    print("\n" + "=" * 70)
                    print("🧠 THINKING PROCESS")
                    print("=" * 70)
                    print(block.thinking)
                    print("=" * 70 + "\n")

            elif block.type == "redacted_thinking":
                result["redacted_blocks"].append(block.data)
                if show_thinking:
                    print("\n🔒 [Some thinking was redacted by safety systems]\n")

            elif block.type == "text":
                result["answer"] = block.text
                print("✓ SOLUTION:")
                print(block.text)

        return result

    def _solve_streaming(self, problem, system_prompt, thinking_budget, max_tokens, show_thinking):
        """Streaming solve."""
        result = {
            "thinking_blocks": [],
            "answer": "",
            "redacted_blocks": []
        }

        current_block_type = None
        current_content = ""

        with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            thinking={
                "type": "enabled",
                "budget_tokens": thinking_budget
            },
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": problem
            }]
        ) as stream:
            for event in stream:
                if event.type == "content_block_start":
                    current_block_type = event.content_block.type
                    current_content = ""

                    if current_block_type == "thinking" and show_thinking:
                        print("\n" + "=" * 70)
                        print("🧠 THINKING PROCESS")
                        print("=" * 70)

                    elif current_block_type == "text":
                        print("\n✓ SOLUTION:")

                elif event.type == "content_block_delta":
                    if event.delta.type == "thinking_delta":
                        current_content += event.delta.thinking
                        if show_thinking:
                            print(event.delta.thinking, end="", flush=True)

                    elif event.delta.type == "text_delta":
                        current_content += event.delta.text
                        print(event.delta.text, end="", flush=True)

                elif event.type == "content_block_stop":
                    if current_block_type == "thinking":
                        result["thinking_blocks"].append(current_content)
                        if show_thinking:
                            print("\n" + "=" * 70 + "\n")

                    elif current_block_type == "text":
                        result["answer"] = current_content
                        print("\n")

                    elif current_block_type == "redacted_thinking":
                        result["redacted_blocks"].append(current_content)
                        if show_thinking:
                            print("\n🔒 [Some thinking was redacted by safety systems]\n")

        return result


def main():
    """CLI interface for the problem solver."""
    parser = argparse.ArgumentParser(
        description="Solve complex problems using Claude's extended thinking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Math problem
  python thinking_problem_solver.py --domain math "What is 17^3 + 89^2 - sqrt(2401)?"

  # Logic puzzle
  python thinking_problem_solver.py --domain logic "Five houses, five colors, five nationalities..."

  # Code review
  python thinking_problem_solver.py --domain code "Review this function: def foo(x): return x/0"

  # Strategic analysis
  python thinking_problem_solver.py --domain strategy "Should we expand to Europe or Asia first?"

  # With streaming
  python thinking_problem_solver.py --stream "Explain the Monty Hall problem"

  # Hide thinking process
  python thinking_problem_solver.py --no-thinking "Quick answer: what's 2+2?"
        """
    )

    parser.add_argument(
        "problem",
        nargs="?",
        help="The problem to solve (or use --interactive)"
    )

    parser.add_argument(
        "--domain",
        choices=["general", "math", "code", "logic", "strategy", "medical", "financial"],
        default="general",
        help="Problem domain (default: general)"
    )

    parser.add_argument(
        "--thinking-budget",
        type=int,
        default=3000,
        help="Tokens allocated for thinking (min 1024, default: 3000)"
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4000,
        help="Maximum response tokens (default: 4000)"
    )

    parser.add_argument(
        "--no-thinking",
        action="store_true",
        help="Hide the thinking process, only show final answer"
    )

    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream the response as it's generated"
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive mode for multiple problems"
    )

    args = parser.parse_args()

    # Validate
    if not args.interactive and not args.problem:
        parser.error("Please provide a problem or use --interactive mode")

    if args.thinking_budget < 1024:
        parser.error("Thinking budget must be at least 1024 tokens")

    # Create solver
    try:
        solver = ThinkingProblemSolver()
    except Exception as e:
        print(f"Error: Could not initialize solver. Make sure ANTHROPIC_API_KEY is set.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)

    # Interactive mode
    if args.interactive:
        print("🤔 Thinking Problem Solver (Interactive Mode)")
        print("Type 'quit' or 'exit' to stop\n")

        while True:
            try:
                problem = input("\n📝 Enter problem: ").strip()

                if problem.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break

                if not problem:
                    continue

                print()
                solver.solve(
                    problem=problem,
                    domain=args.domain,
                    thinking_budget=args.thinking_budget,
                    max_tokens=args.max_tokens,
                    show_thinking=not args.no_thinking,
                    stream=args.stream
                )

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}", file=sys.stderr)

    # Single problem mode
    else:
        solver.solve(
            problem=args.problem,
            domain=args.domain,
            thinking_budget=args.thinking_budget,
            max_tokens=args.max_tokens,
            show_thinking=not args.no_thinking,
            stream=args.stream
        )


if __name__ == "__main__":
    main()
