#!/usr/bin/env python3
"""
Resilient Batch Processor with Modal

Combines resilient file handling with Modal's serverless processing.
Process large datasets with automatic retries and fault tolerance.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import modal
import json

# Create Modal app with additional dependencies
app = modal.App(
    image=modal.Image.debian_slim().pip_install("anthropic")
)


# Resilient file operations (embedded for Modal)
def safe_read_json(path: str, default: Any = None) -> Any:
    """Safely read JSON file with fallback."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {path}, using default")
        return default if default is not None else {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in {path}, using default")
        return default if default is not None else {}
    except Exception as e:
        print(f"Error reading {path}: {e}, using default")
        return default if default is not None else {}


def safe_write_json(path: str, data: Any) -> bool:
    """Safely write JSON file with error handling."""
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error writing {path}: {e}")
        return False


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=300,
    retries=3  # Automatic retries on failure
)
def process_item(
    item: Dict[str, Any],
    prompt_template: str = "Analyze: {content}"
) -> Dict[str, Any]:
    """
    Process a single item with resilience.

    Args:
        item: Item to process
        prompt_template: Template for prompt

    Returns:
        Processed result with metadata
    """
    import anthropic

    try:
        client = anthropic.Anthropic()

        # Build prompt from template
        content = item.get("content", str(item))
        prompt = prompt_template.format(content=content)

        # Process with Claude
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        result = ""
        for block in response.content:
            if block.type == "text":
                result = block.text

        return {
            "item_id": item.get("id", "unknown"),
            "result": result,
            "status": "success",
            "error": None,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }

    except Exception as e:
        return {
            "item_id": item.get("id", "unknown"),
            "result": None,
            "status": "error",
            "error": str(e),
            "usage": None
        }


@app.function(
    timeout=3600,
    network_file_systems={
        "/data": modal.NetworkFileSystem.from_name("batch-data", create_if_missing=True)
    }
)
def batch_process(
    input_file: str,
    output_file: str,
    prompt_template: str = "Analyze: {content}",
    checkpoint_interval: int = 10
) -> Dict[str, Any]:
    """
    Process batch of items with checkpointing.

    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file
        prompt_template: Template for prompts
        checkpoint_interval: Save checkpoint every N items

    Returns:
        Processing summary
    """
    # Read input with resilience
    data = safe_read_json(input_file, default=[])

    if not data:
        return {
            "status": "error",
            "message": f"No data found in {input_file}",
            "processed": 0,
            "errors": 0
        }

    # Check for existing results (resume capability)
    existing_results = safe_read_json(output_file, default={})
    completed_ids = set(existing_results.get("completed", []))

    # Filter items that haven't been processed
    items_to_process = [
        item for item in data
        if item.get("id") not in completed_ids
    ]

    print(f"Total items: {len(data)}")
    print(f"Already completed: {len(completed_ids)}")
    print(f"To process: {len(items_to_process)}")

    # Process items
    results = existing_results.get("results", [])
    errors = existing_results.get("errors", [])

    for i, item in enumerate(items_to_process):
        print(f"Processing item {i+1}/{len(items_to_process)}: {item.get('id')}")

        result = process_item.remote(item, prompt_template)

        if result["status"] == "success":
            results.append(result)
            completed_ids.add(result["item_id"])
        else:
            errors.append(result)

        # Checkpoint periodically
        if (i + 1) % checkpoint_interval == 0:
            checkpoint_data = {
                "results": results,
                "errors": errors,
                "completed": list(completed_ids),
                "progress": {
                    "total": len(data),
                    "completed": len(completed_ids),
                    "pending": len(data) - len(completed_ids)
                }
            }
            safe_write_json(output_file, checkpoint_data)
            print(f"Checkpoint saved: {len(completed_ids)}/{len(data)} completed")

    # Final save
    final_data = {
        "results": results,
        "errors": errors,
        "completed": list(completed_ids),
        "summary": {
            "total": len(data),
            "successful": len(results),
            "failed": len(errors),
            "completion_rate": len(results) / len(data) if data else 0
        }
    }

    safe_write_json(output_file, final_data)

    return final_data["summary"]


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=1800
)
def parallel_batch_process(
    items: List[Dict[str, Any]],
    prompt_template: str = "Analyze: {content}",
    batch_size: int = 100
) -> Dict[str, Any]:
    """
    Process items in parallel batches using Modal's map.

    Args:
        items: List of items to process
        prompt_template: Template for prompts
        batch_size: Items per batch

    Returns:
        Processing summary
    """
    print(f"Processing {len(items)} items in parallel")

    # Process all items in parallel using Modal's map
    results = list(process_item.starmap(
        [(item, prompt_template) for item in items]
    ))

    # Separate successes and errors
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "error"]

    # Calculate statistics
    total_input_tokens = sum(
        r["usage"]["input_tokens"]
        for r in successful
        if r["usage"]
    )
    total_output_tokens = sum(
        r["usage"]["output_tokens"]
        for r in successful
        if r["usage"]
    )

    return {
        "total": len(items),
        "successful": len(successful),
        "failed": len(failed),
        "completion_rate": len(successful) / len(items) if items else 0,
        "results": successful,
        "errors": failed,
        "usage": {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens
        }
    }


@app.function(
    network_file_systems={
        "/data": modal.NetworkFileSystem.from_name("batch-data", create_if_missing=True)
    }
)
def merge_results(
    result_files: List[str],
    output_file: str
) -> Dict[str, Any]:
    """
    Merge multiple result files resiliently.

    Args:
        result_files: List of result file paths
        output_file: Output path for merged results

    Returns:
        Merge summary
    """
    all_results = []
    all_errors = []
    all_completed = set()

    for file_path in result_files:
        data = safe_read_json(file_path, default={})

        if data:
            all_results.extend(data.get("results", []))
            all_errors.extend(data.get("errors", []))
            all_completed.update(data.get("completed", []))

    merged = {
        "results": all_results,
        "errors": all_errors,
        "completed": list(all_completed),
        "summary": {
            "total_files": len(result_files),
            "successful": len(all_results),
            "failed": len(all_errors),
            "unique_items": len(all_completed)
        }
    }

    safe_write_json(output_file, merged)

    return merged["summary"]


@app.local_entrypoint()
def main(
    input_file: Optional[str] = None,
    output_file: str = "output.json",
    prompt: str = "Summarize: {content}",
    parallel: bool = False
):
    """
    CLI entrypoint for resilient batch processor.

    Examples:
        # Sequential with checkpointing
        modal run resilient_batch_processor.py \
            --input-file data.json \
            --output-file results.json

        # Parallel processing
        modal run resilient_batch_processor.py \
            --input-file data.json \
            --output-file results.json \
            --parallel True

        # Custom prompt template
        modal run resilient_batch_processor.py \
            --input-file data.json \
            --prompt "Extract key points from: {content}"
    """

    if input_file is None:
        # Create sample data
        sample_data = [
            {"id": 1, "content": "Explain machine learning"},
            {"id": 2, "content": "What is blockchain?"},
            {"id": 3, "content": "How does encryption work?"},
            {"id": 4, "content": "Describe cloud computing"},
            {"id": 5, "content": "What is DevOps?"}
        ]

        input_file = "sample_input.json"
        safe_write_json(input_file, sample_data)
        print(f"Created sample input: {input_file}")

    print(f"\n{'='*70}")
    print(f"RESILIENT BATCH PROCESSOR")
    print(f"{'='*70}")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"Mode: {'Parallel' if parallel else 'Sequential with checkpoints'}")
    print(f"{'='*70}\n")

    if parallel:
        # Parallel processing
        items = safe_read_json(input_file, default=[])

        if items:
            result = parallel_batch_process.remote(
                items=items,
                prompt_template=prompt
            )

            # Save results
            safe_write_json(output_file, result)

            print("\nRESULTS:")
            print(f"  Total: {result['total']}")
            print(f"  Successful: {result['successful']}")
            print(f"  Failed: {result['failed']}")
            print(f"  Completion rate: {result['completion_rate']:.1%}")
            print(f"  Total tokens: {result['usage']['total_input_tokens'] + result['usage']['total_output_tokens']}")

    else:
        # Sequential with checkpointing
        summary = batch_process.remote(
            input_file=input_file,
            output_file=output_file,
            prompt_template=prompt,
            checkpoint_interval=5
        )

        print("\nRESULTS:")
        print(f"  Total: {summary['total']}")
        print(f"  Successful: {summary['successful']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Completion rate: {summary['completion_rate']:.1%}")

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    # Example: Resume interrupted processing
    items = [{"id": i, "content": f"Task {i}"} for i in range(1, 51)]

    safe_write_json("large_batch.json", items)

    print("Processing large batch with checkpointing...")
    result = batch_process.remote(
        input_file="large_batch.json",
        output_file="large_batch_results.json",
        checkpoint_interval=10
    )

    print(f"Completed: {result['successful']}/{result['total']}")
