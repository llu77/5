"""
Extended Thinking with Tool Use Examples

Demonstrates how Claude's extended thinking combines with tool/function calling,
showing transparent reasoning about when and how to use tools.
"""

import os
import json
from anthropic import Anthropic

# Initialize client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-5"


def example_1_calculator_with_thinking():
    """Example: Math tools with visible reasoning about when to use them."""
    print("=" * 70)
    print("EXAMPLE 1: Calculator Tools with Extended Thinking")
    print("=" * 70)

    # Define calculator tools
    tools = [
        {
            "name": "calculate",
            "description": "Perform mathematical calculations. Use this for complex arithmetic.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2 + 2', '17 * 23')"
                    }
                },
                "required": ["expression"]
            }
        },
        {
            "name": "factorial",
            "description": "Calculate the factorial of a number (n!)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "The number to calculate factorial for"
                    }
                },
                "required": ["n"]
            }
        }
    ]

    def calculate(expression):
        """Safely evaluate mathematical expressions."""
        try:
            # Only allow basic math operations
            allowed_chars = set("0123456789+-*/().^ ")
            if not all(c in allowed_chars for c in expression):
                return {"error": "Expression contains invalid characters"}

            # Replace ^ with **
            expression = expression.replace("^", "**")
            result = eval(expression)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}

    def factorial(n):
        """Calculate factorial."""
        if n < 0:
            return {"error": "Factorial not defined for negative numbers"}
        if n > 100:
            return {"error": "Number too large"}

        result = 1
        for i in range(2, n + 1):
            result *= i
        return {"result": result}

    # Make request with thinking
    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        thinking={"type": "enabled", "budget_tokens": 2000},
        tools=tools,
        messages=[{
            "role": "user",
            "content": "Calculate 17^3 + 23^2. Also, what's 5 factorial? Show your reasoning."
        }]
    )

    # Process the conversation
    conversation = [{
        "role": "user",
        "content": "Calculate 17^3 + 23^2. Also, what's 5 factorial? Show your reasoning."
    }]

    while response.stop_reason == "tool_use":
        # Print thinking if present
        for block in response.content:
            if block.type == "thinking":
                print("\n🧠 THINKING:")
                print("-" * 70)
                print(block.thinking)
                print("-" * 70)

        # Add assistant response to conversation
        conversation.append({
            "role": "assistant",
            "content": response.content
        })

        # Execute tools
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"\n🔧 TOOL CALL: {block.name}")
                print(f"   Input: {block.input}")

                if block.name == "calculate":
                    result = calculate(block.input["expression"])
                elif block.name == "factorial":
                    result = factorial(block.input["n"])
                else:
                    result = {"error": "Unknown tool"}

                print(f"   Result: {result}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result)
                })

        # Add tool results
        conversation.append({
            "role": "user",
            "content": tool_results
        })

        # Continue conversation
        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            thinking={"type": "enabled", "budget_tokens": 2000},
            tools=tools,
            messages=conversation
        )

    # Print final answer
    for block in response.content:
        if block.type == "text":
            print("\n✓ FINAL ANSWER:")
            print(block.text)

    print("\n")


def example_2_data_analysis_with_thinking():
    """Example: Data query tools with reasoning about data interpretation."""
    print("=" * 70)
    print("EXAMPLE 2: Data Analysis Tools with Extended Thinking")
    print("=" * 70)

    # Define data tools
    tools = [
        {
            "name": "query_sales",
            "description": "Query sales data for a specific month",
            "input_schema": {
                "type": "object",
                "properties": {
                    "month": {
                        "type": "string",
                        "description": "Month name (e.g., 'January', 'February')"
                    }
                },
                "required": ["month"]
            }
        },
        {
            "name": "calculate_average",
            "description": "Calculate average of a list of numbers",
            "input_schema": {
                "type": "object",
                "properties": {
                    "numbers": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "List of numbers to average"
                    }
                },
                "required": ["numbers"]
            }
        }
    ]

    # Mock data
    sales_data = {
        "January": {"revenue": 50000, "units": 500, "customers": 120},
        "February": {"revenue": 65000, "units": 650, "customers": 145},
        "March": {"revenue": 72000, "units": 700, "customers": 160},
        "April": {"revenue": 68000, "units": 680, "customers": 155}
    }

    def query_sales(month):
        return sales_data.get(month, {"error": f"No data for {month}"})

    def calculate_average(numbers):
        if not numbers:
            return {"error": "Empty list"}
        return {"average": sum(numbers) / len(numbers)}

    # Make request
    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        thinking={"type": "enabled", "budget_tokens": 3000},
        tools=tools,
        messages=[{
            "role": "user",
            "content": "What was our average monthly revenue for Q1 (January-March)? Show your analysis."
        }]
    )

    conversation = [{
        "role": "user",
        "content": "What was our average monthly revenue for Q1 (January-March)? Show your analysis."
    }]

    iteration = 0
    while response.stop_reason == "tool_use" and iteration < 10:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")

        # Print thinking
        for block in response.content:
            if block.type == "thinking":
                print("\n🧠 REASONING:")
                print(block.thinking[:500] + "..." if len(block.thinking) > 500 else block.thinking)

        # Add assistant response
        conversation.append({
            "role": "assistant",
            "content": response.content
        })

        # Execute tools
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"\n🔧 {block.name}({block.input})")

                if block.name == "query_sales":
                    result = query_sales(block.input["month"])
                elif block.name == "calculate_average":
                    result = calculate_average(block.input["numbers"])
                else:
                    result = {"error": "Unknown tool"}

                print(f"   → {result}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result)
                })

        conversation.append({
            "role": "user",
            "content": tool_results
        })

        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            thinking={"type": "enabled", "budget_tokens": 3000},
            tools=tools,
            messages=conversation
        )

    # Final answer
    for block in response.content:
        if block.type == "text":
            print("\n✓ ANALYSIS RESULT:")
            print(block.text)

    print("\n")


def example_3_file_operations_with_thinking():
    """Example: File system tools with reasoning about file operations."""
    print("=" * 70)
    print("EXAMPLE 3: File Operations with Extended Thinking")
    print("=" * 70)

    tools = [
        {
            "name": "list_files",
            "description": "List files in a directory",
            "input_schema": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory path"
                    }
                },
                "required": ["directory"]
            }
        },
        {
            "name": "read_file",
            "description": "Read contents of a file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "File name to read"
                    }
                },
                "required": ["filename"]
            }
        },
        {
            "name": "search_content",
            "description": "Search for text in files",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text to search for"
                    }
                },
                "required": ["query"]
            }
        }
    ]

    # Mock file system
    mock_files = {
        "documents": ["report.txt", "notes.txt", "summary.md"],
        "report.txt": "Q1 sales were excellent. Revenue increased 30%.",
        "notes.txt": "Remember to follow up with clients about Q2 plans.",
        "summary.md": "# Summary\nRevenue trends show strong growth."
    }

    def list_files(directory):
        return {"files": mock_files.get(directory, [])}

    def read_file(filename):
        content = mock_files.get(filename)
        if content:
            return {"content": content}
        return {"error": "File not found"}

    def search_content(query):
        results = []
        for name, content in mock_files.items():
            if isinstance(content, str) and query.lower() in content.lower():
                results.append({"file": name, "snippet": content[:100]})
        return {"matches": results}

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        thinking={"type": "enabled", "budget_tokens": 2500},
        tools=tools,
        messages=[{
            "role": "user",
            "content": "Find all mentions of 'revenue' in my documents and summarize what you find."
        }]
    )

    conversation = [{
        "role": "user",
        "content": "Find all mentions of 'revenue' in my documents and summarize what you find."
    }]

    iteration = 0
    while response.stop_reason == "tool_use" and iteration < 10:
        iteration += 1

        # Show thinking
        for block in response.content:
            if block.type == "thinking":
                print(f"\n🧠 THINKING (Iteration {iteration}):")
                print(block.thinking[:400] + "..." if len(block.thinking) > 400 else block.thinking)

        conversation.append({
            "role": "assistant",
            "content": response.content
        })

        # Execute tools
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"\n🔧 {block.name}: {block.input}")

                if block.name == "list_files":
                    result = list_files(block.input["directory"])
                elif block.name == "read_file":
                    result = read_file(block.input["filename"])
                elif block.name == "search_content":
                    result = search_content(block.input["query"])
                else:
                    result = {"error": "Unknown tool"}

                print(f"   Result: {result}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result)
                })

        conversation.append({
            "role": "user",
            "content": tool_results
        })

        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            thinking={"type": "enabled", "budget_tokens": 2500},
            tools=tools,
            messages=conversation
        )

    # Final answer
    for block in response.content:
        if block.type == "text":
            print("\n✓ SUMMARY:")
            print(block.text)

    print("\n")


if __name__ == "__main__":
    print("\n🧠 Extended Thinking with Tool Use Examples\n")

    # Run examples (uncomment to try)
    example_1_calculator_with_thinking()
    # example_2_data_analysis_with_thinking()
    # example_3_file_operations_with_thinking()

    print("✅ Examples complete!\n")
