#!/usr/bin/env python3
"""
Orchestrator-Workers Pattern with Modal

Distributes work across parallel Modal functions.
Each worker can scale independently on Modal's infrastructure.
"""

from typing import Dict, Any, List, Optional
import modal
import re

# Create Modal app
app = modal.App(
    image=modal.Image.debian_slim().pip_install("anthropic")
)


def extract_xml(text: str, tag: str) -> str:
    """Extract content between XML tags."""
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def parse_worker_tasks(orchestrator_response: str) -> List[Dict[str, str]]:
    """Parse worker tasks from orchestrator XML response."""
    workers_xml = extract_xml(orchestrator_response, "workers")
    worker_blocks = re.findall(r"<worker>.*?</worker>", workers_xml, re.DOTALL)

    tasks = []
    for block in worker_blocks:
        role = extract_xml(block, "role")
        task = extract_xml(block, "task")
        if role and task:
            tasks.append({"role": role, "task": task})

    return tasks


ORCHESTRATOR_PROMPT = """You are an orchestrator that analyzes tasks and delegates them to specialized workers.

Given a task, you should:
1. Break it down into subtasks
2. Determine what specialist roles are needed
3. Output the task assignments in XML format

Use this format:
<analysis>
Your analysis of the task and decomposition strategy
</analysis>

<workers>
<worker>
<role>Role name (e.g., "Data Analyst", "Security Researcher")</role>
<task>Specific task for this worker</task>
</worker>
<!-- More workers as needed -->
</workers>

Limit to 5 workers maximum for efficiency."""


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=300
)
def orchestrate(task: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze task and create worker assignments.

    Args:
        task: Main task to decompose
        context: Additional context

    Returns:
        Analysis and worker task assignments
    """
    import anthropic

    client = anthropic.Anthropic()

    prompt = task
    if context:
        prompt = f"Task: {task}\n\nContext: {context}"

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=ORCHESTRATOR_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract response text
    response_text = ""
    for block in response.content:
        if block.type == "text":
            response_text = block.text

    # Parse analysis and worker tasks
    analysis = extract_xml(response_text, "analysis")
    worker_tasks = parse_worker_tasks(response_text)

    return {
        "analysis": analysis,
        "workers": worker_tasks,
        "raw_response": response_text
    }


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=600
)
def run_worker(
    role: str,
    task: str,
    original_task: str,
    worker_id: int
) -> Dict[str, Any]:
    """
    Execute worker task with specialized role.

    Args:
        role: Worker's specialized role
        task: Specific task for this worker
        original_task: Original overall task
        worker_id: Unique worker identifier

    Returns:
        Worker result with role and findings
    """
    import anthropic

    client = anthropic.Anthropic()

    system_prompt = f"""You are a {role}.

Your specific task:
{task}

Provide a focused response based on your expertise. Be thorough but concise."""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"Original task: {original_task}\n\nYour specific assignment: {task}"
        }]
    )

    # Extract result
    result = ""
    for block in response.content:
        if block.type == "text":
            result = block.text

    return {
        "worker_id": worker_id,
        "role": role,
        "task": task,
        "result": result
    }


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=300
)
def synthesize(
    original_task: str,
    analysis: str,
    worker_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Synthesize worker results into comprehensive answer.

    Args:
        original_task: Original task
        analysis: Orchestrator's analysis
        worker_results: Results from all workers

    Returns:
        Synthesized final answer
    """
    import anthropic

    client = anthropic.Anthropic()

    # Build synthesis prompt
    prompt = f"Original task: {original_task}\n\n"
    prompt += f"Orchestrator analysis:\n{analysis}\n\n"
    prompt += "Worker results:\n\n"

    for worker in worker_results:
        prompt += f"## {worker['role']} (Worker {worker['worker_id']})\n"
        prompt += f"{worker['result']}\n\n"

    prompt += "Synthesize these results into a comprehensive answer to the original task."

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract synthesis
    synthesis = ""
    for block in response.content:
        if block.type == "text":
            synthesis = block.text

    return {
        "synthesis": synthesis,
        "worker_count": len(worker_results)
    }


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=1800  # 30 minutes for full pipeline
)
def process_with_orchestrator(
    task: str,
    context: Optional[str] = None,
    max_workers: int = 5
) -> Dict[str, Any]:
    """
    Complete orchestrator-workers pipeline.

    Args:
        task: Main task
        context: Additional context
        max_workers: Maximum number of workers

    Returns:
        Complete results including analysis, worker results, and synthesis
    """
    # Step 1: Orchestrate
    print(f"Orchestrating task: {task}")
    orchestration = orchestrate.remote(task, context)

    analysis = orchestration["analysis"]
    worker_tasks = orchestration["workers"][:max_workers]

    print(f"Analysis: {analysis[:200]}...")
    print(f"Created {len(worker_tasks)} workers")

    # Step 2: Run workers in parallel using Modal's map
    print("Running workers in parallel...")

    worker_results = []
    for i, worker_task in enumerate(worker_tasks):
        result = run_worker.remote(
            role=worker_task["role"],
            task=worker_task["task"],
            original_task=task,
            worker_id=i + 1
        )
        worker_results.append(result)

    print(f"Completed {len(worker_results)} workers")

    # Step 3: Synthesize results
    print("Synthesizing results...")
    synthesis_result = synthesize.remote(
        original_task=task,
        analysis=analysis,
        worker_results=worker_results
    )

    return {
        "task": task,
        "analysis": analysis,
        "workers": worker_results,
        "synthesis": synthesis_result["synthesis"],
        "metadata": {
            "worker_count": len(worker_results),
            "max_workers": max_workers
        }
    }


# Parallel map example for large-scale processing
@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=60
)
def analyze_single_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single item (used with map for parallel execution)."""
    import anthropic

    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-3-haiku-20240307",  # Faster model for batch processing
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": item.get("prompt", "Analyze this: " + str(item))
        }]
    )

    result = ""
    for block in response.content:
        if block.type == "text":
            result = block.text

    return {
        "item_id": item.get("id", "unknown"),
        "result": result
    }


@app.function(timeout=3600)
def batch_process_parallel(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process many items in parallel using Modal's map.

    Modal automatically distributes work across containers.

    Args:
        items: List of items to process

    Returns:
        Results from all items
    """
    # Use Modal's map for automatic parallelization
    results = list(analyze_single_item.map(items))
    return results


@app.local_entrypoint()
def main(
    task: Optional[str] = None,
    context: Optional[str] = None,
    max_workers: int = 5
):
    """
    CLI entrypoint for orchestrator-workers pattern.

    Examples:
        # Basic orchestration
        modal run orchestrator_workers_modal.py \
            --task "Analyze security best practices for REST APIs"

        # With context
        modal run orchestrator_workers_modal.py \
            --task "Review this codebase architecture" \
            --context "$(cat ARCHITECTURE.md)"

        # Limit workers
        modal run orchestrator_workers_modal.py \
            --task "Comprehensive market analysis for SaaS product" \
            --max-workers 3
    """

    if task is None:
        # Default example
        task = "Analyze the feasibility of migrating a monolith to microservices"
        context = "Current stack: Python Django, PostgreSQL, Redis. Team size: 10 engineers. 50k daily active users."

    print(f"\n{'='*70}")
    print(f"ORCHESTRATOR-WORKERS PIPELINE")
    print(f"{'='*70}")
    print(f"Task: {task}")
    if context:
        print(f"Context: {context}")
    print(f"Max workers: {max_workers}")
    print(f"{'='*70}\n")

    # Run orchestrator-workers pipeline
    result = process_with_orchestrator.remote(
        task=task,
        context=context,
        max_workers=max_workers
    )

    # Display results
    print("\n" + "="*70)
    print("ORCHESTRATOR ANALYSIS")
    print("="*70)
    print(result["analysis"])

    print("\n" + "="*70)
    print(f"WORKER RESULTS ({len(result['workers'])} workers)")
    print("="*70)

    for worker in result["workers"]:
        print(f"\n--- {worker['role']} (Worker {worker['worker_id']}) ---")
        print(f"Task: {worker['task']}")
        print(f"\nResult:")
        print(worker["result"])
        print()

    print("="*70)
    print("SYNTHESIS")
    print("="*70)
    print(result["synthesis"])
    print()

    print("="*70)
    print("METADATA")
    print("="*70)
    print(f"Workers used: {result['metadata']['worker_count']}")
    print(f"Max workers: {result['metadata']['max_workers']}")
    print()


# Web API endpoint
@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")]
)
@modal.web_endpoint(method="POST")
def api(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Web API for orchestrator-workers.

    POST https://your-modal-url.modal.run
    {
        "task": "Your complex task",
        "context": "Optional context",
        "max_workers": 5
    }
    """
    task = request_data.get("task")
    if not task:
        return {"error": "Missing 'task' field"}

    result = process_with_orchestrator.remote(
        task=task,
        context=request_data.get("context"),
        max_workers=request_data.get("max_workers", 5)
    )

    return result


if __name__ == "__main__":
    # Example: Batch parallel processing
    items = [
        {"id": 1, "prompt": "Explain photosynthesis"},
        {"id": 2, "prompt": "What is quantum computing?"},
        {"id": 3, "prompt": "How do neural networks work?"},
        {"id": 4, "prompt": "Explain blockchain technology"},
        {"id": 5, "prompt": "What is the theory of relativity?"}
    ]

    print("Running batch parallel processing...")
    results = batch_process_parallel.remote(items)

    for result in results:
        print(f"\nItem {result['item_id']}:")
        print(result["result"][:200] + "...")
