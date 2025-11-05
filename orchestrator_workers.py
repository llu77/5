#!/usr/bin/env python3
"""
Orchestrator-Workers Pattern Implementation

Dynamically break down complex tasks into specialized subtasks,
then delegate to worker LLMs for parallel execution.
"""

import os
import sys
import json
import argparse
import re
from typing import Dict, List, Any, Optional
from anthropic import Anthropic


def extract_xml(text: str, tag: str) -> str:
    """Extract content between XML tags."""
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


def parse_tasks(tasks_xml: str) -> List[Dict]:
    """Parse XML tasks into a list of task dictionaries."""
    tasks = []
    current_task = {}

    for line in tasks_xml.split("\n"):
        line = line.strip()
        if not line:
            continue

        if line.startswith("<task>"):
            current_task = {}
        elif line.startswith("<type>"):
            current_task["type"] = line[6:-7].strip()
        elif line.startswith("<description>"):
            current_task["description"] = line[13:-14].strip()
        elif line.startswith("</task>"):
            if "description" in current_task:
                if "type" not in current_task:
                    current_task["type"] = "default"
                tasks.append(current_task)

    return tasks


class OrchestratorWorkers:
    """Orchestrate complex tasks by delegating to specialized workers."""

    def __init__(
        self,
        orchestrator_prompt: str,
        worker_prompt: str,
        model: str = "claude-sonnet-4-5",
        api_key: str = None
    ):
        """
        Initialize orchestrator-workers system.

        Args:
            orchestrator_prompt: Template for orchestrator analysis
            worker_prompt: Template for worker execution
            model: Claude model to use
            api_key: Anthropic API key
        """
        self.orchestrator_prompt = orchestrator_prompt
        self.worker_prompt = worker_prompt
        self.model = model
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with variables."""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required variable: {e}")

    def _call_llm(self, prompt: str, system_prompt: str = "") -> str:
        """Make an LLM call."""
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def process(
        self,
        task: str,
        context: Optional[Dict] = None,
        verbose: bool = True
    ) -> Dict:
        """
        Process task through orchestrator-workers pattern.

        Args:
            task: The main task to accomplish
            context: Additional context variables
            verbose: Print progress information

        Returns:
            Dictionary with analysis and worker results
        """
        context = context or {}

        # Step 1: Orchestrator Analysis
        if verbose:
            print("\n" + "="*80)
            print("🎯 ORCHESTRATOR ANALYSIS")
            print("="*80)

        orchestrator_input = self._format_prompt(
            self.orchestrator_prompt,
            task=task,
            **context
        )

        orchestrator_response = self._call_llm(orchestrator_input)

        # Parse orchestrator response
        analysis = extract_xml(orchestrator_response, "analysis")
        tasks_xml = extract_xml(orchestrator_response, "tasks")
        tasks = parse_tasks(tasks_xml)

        if verbose:
            print(f"\n{analysis}\n")
            print("\n" + "="*80)
            print(f"📋 IDENTIFIED {len(tasks)} APPROACHES")
            print("="*80)

            for i, task_info in enumerate(tasks, 1):
                print(f"\n{i}. {task_info['type'].upper()}")
                print(f"   {task_info['description']}")

        # Step 2: Execute Workers
        if verbose:
            print("\n" + "="*80)
            print("⚙️  EXECUTING WORKERS")
            print("="*80 + "\n")

        worker_results = []
        for i, task_info in enumerate(tasks, 1):
            if verbose:
                print(f"[{i}/{len(tasks)}] {task_info['type']}...", end=" ", flush=True)

            worker_input = self._format_prompt(
                self.worker_prompt,
                original_task=task,
                task_type=task_info["type"],
                task_description=task_info["description"],
                **context
            )

            try:
                worker_response = self._call_llm(worker_input)
                worker_content = extract_xml(worker_response, "response")

                if not worker_content or not worker_content.strip():
                    worker_content = f"[Error: Worker failed to generate content]"
                    if verbose:
                        print("⚠️")
                else:
                    if verbose:
                        print("✓")

                worker_results.append({
                    "type": task_info["type"],
                    "description": task_info["description"],
                    "result": worker_content
                })

            except Exception as e:
                if verbose:
                    print(f"✗ ({e})")
                worker_results.append({
                    "type": task_info["type"],
                    "description": task_info["description"],
                    "result": f"[Error: {e}]"
                })

        # Display results
        if verbose:
            print("\n" + "="*80)
            print("📊 RESULTS")
            print("="*80)

            for i, result in enumerate(worker_results, 1):
                print(f"\n{'-'*80}")
                print(f"Approach {i}: {result['type'].upper()}")
                print(f"{'-'*80}")
                print(f"\n{result['result']}\n")

        return {
            "task": task,
            "analysis": analysis,
            "approaches": tasks,
            "results": worker_results,
            "orchestrator_response": orchestrator_response
        }


# Pre-built templates
MARKETING_ORCHESTRATOR = """
Analyze this marketing task and break it down into 2-4 distinct approaches:

Task: {task}

Context:
{context_str}

Consider different:
- Target audiences (demographics, psychographics)
- Messaging styles (emotional, rational, humorous, professional)
- Channels (social media, email, print, video)
- Content formats (long-form, short-form, visual, interactive)

Return your response in this format:

<analysis>
Explain which marketing approaches would be most valuable for this task and why.
Consider how each approach serves different audiences or objectives.
</analysis>

<tasks>
    <task>
    <type>approach-name</type>
    <description>Specific instructions for this marketing approach</description>
    </task>
</tasks>
"""

MARKETING_WORKER = """
Generate marketing content based on:

Original Task: {original_task}
Approach: {task_type}
Guidelines: {task_description}

Context:
{context_str}

Create compelling, professional content that follows the specified approach.

<response>
Your marketing content here, following the guidelines exactly.
</response>
"""

RESEARCH_ORCHESTRATOR = """
Analyze this research question and identify 2-4 different analytical perspectives:

Question: {task}

Context:
{context_str}

Consider different:
- Analytical frameworks (quantitative, qualitative, comparative)
- Perspectives (historical, technical, practical, theoretical)
- Depths (overview, deep-dive, critical analysis)
- Audiences (experts, general public, decision-makers)

Return your response in this format:

<analysis>
Explain which analytical approaches would provide the most comprehensive answer.
</analysis>

<tasks>
    <task>
    <type>perspective-name</type>
    <description>Specific analytical approach and focus areas</description>
    </task>
</tasks>
"""

RESEARCH_WORKER = """
Provide analysis based on:

Research Question: {original_task}
Analytical Perspective: {task_type}
Focus: {task_description}

Context:
{context_str}

Provide thorough, well-reasoned analysis from this perspective.

<response>
Your analysis here, maintaining the specified perspective.
</response>
"""

CREATIVE_ORCHESTRATOR = """
Analyze this creative writing task and identify 2-4 different creative approaches:

Task: {task}

Context:
{context_str}

Consider different:
- Tones (serious, humorous, dramatic, whimsical)
- Styles (concise, elaborate, poetic, conversational)
- Perspectives (first-person, third-person, narrative, descriptive)
- Formats (story, dialogue, letter, article)

<analysis>
Explain which creative approaches would best serve this task.
</analysis>

<tasks>
    <task>
    <type>style-name</type>
    <description>Specific creative approach and stylistic guidelines</description>
    </task>
</tasks>
"""

CREATIVE_WORKER = """
Create content based on:

Creative Task: {original_task}
Style: {task_type}
Approach: {task_description}

Context:
{context_str}

Write engaging, creative content in the specified style.

<response>
Your creative content here.
</response>
"""


def format_context(context: Dict) -> str:
    """Format context dictionary as readable string."""
    if not context:
        return "None provided"

    lines = []
    for key, value in context.items():
        formatted_key = key.replace("_", " ").title()
        if isinstance(value, list):
            lines.append(f"- {formatted_key}: {', '.join(str(v) for v in value)}")
        else:
            lines.append(f"- {formatted_key}: {value}")

    return "\n".join(lines)


def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(
        description="Orchestrator-Workers pattern for complex task delegation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Marketing content generation
  python orchestrator_workers.py marketing \\
    "Create product launch announcement for eco-friendly water bottle"

  # Research analysis
  python orchestrator_workers.py research \\
    "How does remote work impact team productivity?"

  # Creative writing
  python orchestrator_workers.py creative \\
    "Write a company mission statement for a sustainable fashion brand"

  # Custom task with context
  python orchestrator_workers.py marketing \\
    "Email campaign for new feature" \\
    --context "target_audience=developers" "tone=technical"

  # Save results to file
  python orchestrator_workers.py creative \\
    "Blog post about AI ethics" \\
    --output results.json
        """
    )

    parser.add_argument(
        "mode",
        choices=["marketing", "research", "creative"],
        help="Type of task"
    )

    parser.add_argument(
        "task",
        help="Description of the task"
    )

    parser.add_argument(
        "--context", "-c",
        nargs="+",
        help="Context key=value pairs (e.g., audience=developers tone=formal)"
    )

    parser.add_argument(
        "--output", "-o",
        help="Save results to JSON file"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output"
    )

    args = parser.parse_args()

    # Parse context
    context = {}
    if args.context:
        for item in args.context:
            if "=" in item:
                key, value = item.split("=", 1)
                context[key] = value

    # Add formatted context string
    context["context_str"] = format_context(context)

    # Select templates
    templates = {
        "marketing": (MARKETING_ORCHESTRATOR, MARKETING_WORKER),
        "research": (RESEARCH_ORCHESTRATOR, RESEARCH_WORKER),
        "creative": (CREATIVE_ORCHESTRATOR, CREATIVE_WORKER)
    }

    orchestrator_prompt, worker_prompt = templates[args.mode]

    # Create orchestrator
    try:
        orchestrator = OrchestratorWorkers(
            orchestrator_prompt=orchestrator_prompt,
            worker_prompt=worker_prompt
        )
    except Exception as e:
        print(f"Error: Could not initialize. Make sure ANTHROPIC_API_KEY is set.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)

    # Process task
    try:
        print(f"\n🎯 {args.mode.upper()} TASK")
        print(f"Task: {args.task}\n")

        results = orchestrator.process(
            task=args.task,
            context=context,
            verbose=not args.quiet
        )

        # Save if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dumps(results, f, indent=2)
            print(f"\n💾 Results saved to {args.output}")

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
