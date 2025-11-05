#!/usr/bin/env python3
"""
Extended Thinking Agent with Modal

Serverless extended thinking using Claude Sonnet 4.5.
Runs on Modal's cloud infrastructure with automatic scaling.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import modal

# Create Modal app with Anthropic SDK
app = modal.App(
    image=modal.Image.debian_slim().pip_install("anthropic")
)


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=600  # 10 minutes for complex thinking tasks
)
def think_and_solve(
    task: str,
    context: Optional[str] = None,
    thinking_budget: int = 3000,
    domain: str = "general"
) -> Dict[str, Any]:
    """
    Process task with extended thinking.

    Args:
        task: Problem or question to solve
        context: Additional context
        thinking_budget: Token budget for thinking (default: 3000)
        domain: Domain-specific system prompt (general, math, code, strategy)

    Returns:
        Dictionary with thinking, answer, and usage stats
    """
    import anthropic

    client = anthropic.Anthropic()

    # Domain-specific system prompts
    system_prompts = {
        "general": "You are an expert problem solver with deep analytical capabilities.",
        "math": "You are an expert mathematician. Show all work and explain your reasoning clearly.",
        "code": "You are an expert software engineer. Analyze code carefully and provide detailed explanations.",
        "strategy": "You are a strategic thinker. Consider multiple perspectives and long-term implications.",
        "data": "You are a data analyst. Examine data carefully and draw evidence-based conclusions.",
        "research": "You are a research scientist. Evaluate evidence critically and consider alternative hypotheses."
    }

    system_prompt = system_prompts.get(domain, system_prompts["general"])

    if context:
        system_prompt += f"\n\nContext: {context}"

    # Create message with extended thinking
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        thinking={
            "type": "enabled",
            "budget_tokens": thinking_budget
        },
        system=system_prompt,
        messages=[{"role": "user", "content": task}]
    )

    # Extract thinking and answer
    thinking = ""
    answer = ""

    for block in response.content:
        if block.type == "thinking":
            thinking = block.thinking
        elif block.type == "text":
            answer = block.text

    return {
        "thinking": thinking,
        "answer": answer,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        },
        "model": response.model,
        "stop_reason": response.stop_reason
    }


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=900  # 15 minutes for multi-step problems
)
def solve_iteratively(
    task: str,
    max_iterations: int = 5,
    thinking_budget: int = 2000
) -> Dict[str, Any]:
    """
    Solve complex problems iteratively with thinking.

    Useful for problems that benefit from multiple rounds of reasoning.

    Args:
        task: Complex problem to solve
        max_iterations: Maximum reasoning iterations
        thinking_budget: Token budget per iteration

    Returns:
        Dictionary with all iterations and final answer
    """
    import anthropic

    client = anthropic.Anthropic()

    conversation = []
    iterations = []

    system_prompt = (
        "You are solving a complex problem step by step. "
        "After each step, you may request to continue thinking if needed. "
        "Signal completion by starting your response with 'FINAL ANSWER:'"
    )

    for i in range(max_iterations):
        # Add task to conversation (first iteration) or continuation prompt
        if i == 0:
            conversation.append({"role": "user", "content": task})
        else:
            conversation.append({
                "role": "user",
                "content": "Continue reasoning. If ready, provide FINAL ANSWER:"
            })

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=3000,
            thinking={
                "type": "enabled",
                "budget_tokens": thinking_budget
            },
            system=system_prompt,
            messages=conversation
        )

        # Extract thinking and answer
        thinking = ""
        answer = ""

        for block in response.content:
            if block.type == "thinking":
                thinking = block.thinking
            elif block.type == "text":
                answer = block.text

        iterations.append({
            "iteration": i + 1,
            "thinking": thinking,
            "answer": answer
        })

        # Add assistant response to conversation
        conversation.append({"role": "assistant", "content": answer})

        # Check if final answer provided
        if answer.strip().startswith("FINAL ANSWER:"):
            break

    return {
        "iterations": iterations,
        "total_iterations": len(iterations),
        "final_answer": iterations[-1]["answer"] if iterations else ""
    }


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=1800,  # 30 minutes for batch processing
    cpu=2.0  # More CPU for parallel processing
)
def batch_analyze(
    tasks: List[Dict[str, str]],
    thinking_budget: int = 2000
) -> List[Dict[str, Any]]:
    """
    Process multiple tasks with thinking in parallel.

    Args:
        tasks: List of task dictionaries with 'task' and optional 'context'
        thinking_budget: Token budget per task

    Returns:
        List of results for each task
    """
    import anthropic

    client = anthropic.Anthropic()
    results = []

    for task_data in tasks:
        task = task_data.get("task", "")
        context = task_data.get("context")
        domain = task_data.get("domain", "general")

        result = think_and_solve.local(
            task=task,
            context=context,
            thinking_budget=thinking_budget,
            domain=domain
        )

        results.append({
            "task": task,
            "result": result
        })

    return results


@app.local_entrypoint()
def main(
    task: Optional[str] = None,
    context: Optional[str] = None,
    thinking_budget: int = 3000,
    domain: str = "general",
    iterative: bool = False,
    max_iterations: int = 5
):
    """
    CLI entrypoint for thinking agent.

    Examples:
        # Basic thinking
        modal run thinking_agent_modal.py --task "Calculate 17^3"

        # With context
        modal run thinking_agent_modal.py \
            --task "Explain this algorithm" \
            --context "$(cat algorithm.py)"

        # Iterative problem solving
        modal run thinking_agent_modal.py \
            --task "Solve the traveling salesman problem for 5 cities" \
            --iterative True \
            --max-iterations 5

        # Domain-specific
        modal run thinking_agent_modal.py \
            --task "Prove the Pythagorean theorem" \
            --domain math
    """

    if task is None:
        # Default example
        task = "What is the 10th Fibonacci number? Show your reasoning."
        domain = "math"

    print(f"\n{'='*70}")
    print(f"TASK: {task}")
    if context:
        print(f"CONTEXT: {context[:100]}..." if len(context) > 100 else f"CONTEXT: {context}")
    print(f"DOMAIN: {domain}")
    print(f"THINKING BUDGET: {thinking_budget} tokens")
    print(f"{'='*70}\n")

    if iterative:
        # Use iterative solver
        result = solve_iteratively.remote(
            task=task,
            max_iterations=max_iterations,
            thinking_budget=thinking_budget
        )

        print(f"ITERATIONS: {result['total_iterations']}\n")

        for iteration in result["iterations"]:
            print(f"--- Iteration {iteration['iteration']} ---")
            print(f"\nTHINKING:")
            print(iteration["thinking"][:500] + "..." if len(iteration["thinking"]) > 500 else iteration["thinking"])
            print(f"\nANSWER:")
            print(iteration["answer"])
            print()

        print(f"\n{'='*70}")
        print("FINAL ANSWER:")
        print(result["final_answer"])
        print(f"{'='*70}\n")

    else:
        # Single-shot thinking
        result = think_and_solve.remote(
            task=task,
            context=context,
            thinking_budget=thinking_budget,
            domain=domain
        )

        print("THINKING:")
        print("-" * 70)
        print(result["thinking"])
        print()

        print("ANSWER:")
        print("-" * 70)
        print(result["answer"])
        print()

        print("USAGE:")
        print(f"  Input tokens:  {result['usage']['input_tokens']}")
        print(f"  Output tokens: {result['usage']['output_tokens']}")
        print(f"  Model: {result['model']}")
        print(f"  Stop reason: {result['stop_reason']}")
        print()


# Web endpoint example
@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")]
)
@modal.web_endpoint(method="POST")
def api(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Web API endpoint for thinking agent.

    POST https://your-modal-url.modal.run
    {
        "task": "Your problem here",
        "context": "Optional context",
        "thinking_budget": 3000,
        "domain": "general"
    }
    """
    task = request_data.get("task")
    if not task:
        return {"error": "Missing 'task' field"}

    result = think_and_solve.remote(
        task=task,
        context=request_data.get("context"),
        thinking_budget=request_data.get("thinking_budget", 3000),
        domain=request_data.get("domain", "general")
    )

    return result


if __name__ == "__main__":
    # Example batch processing
    tasks = [
        {"task": "Calculate 15!", "domain": "math"},
        {"task": "Explain quicksort algorithm", "domain": "code"},
        {"task": "What are the ethical implications of AI?", "domain": "strategy"}
    ]

    print("Running batch analysis...")
    results = batch_analyze.remote(tasks=tasks)

    for i, result in enumerate(results, 1):
        print(f"\n{'='*70}")
        print(f"Task {i}: {result['task']}")
        print(f"{'='*70}")
        print(f"Answer: {result['result']['answer'][:200]}...")
