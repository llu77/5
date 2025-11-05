"""
Examples combining system prompts with extended thinking.

This demonstrates how to use Claude's extended thinking feature
with custom system prompts for different use cases.
"""

import os
from anthropic import Anthropic

# Initialize client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def example_1_financial_analysis():
    """Example: Financial analyst with extended thinking."""
    print("=" * 60)
    print("EXAMPLE 1: Financial Analysis with Extended Thinking")
    print("=" * 60)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        thinking={
            "type": "enabled",
            "budget_tokens": 3000
        },
        system="""You are an expert financial analyst. When analyzing financial scenarios:

1. Break down complex calculations step-by-step
2. Consider multiple perspectives (bull case, bear case, base case)
3. Identify key assumptions and their impact
4. Check your arithmetic carefully
5. Provide clear, actionable recommendations

Think thoroughly before providing your final analysis.""",
        messages=[{
            "role": "user",
            "content": """A company has:
- Revenue: $10M (growing 30% YoY)
- Operating expenses: $7M
- Customer acquisition cost (CAC): $500
- Lifetime value (LTV): $2000
- Burn rate: $500K/month
- Current cash: $6M

Should they raise more funding or focus on profitability? Consider runway and growth trade-offs."""
        }]
    )

    # Print the response
    for block in response.content:
        if block.type == "thinking":
            print("\n🧠 THINKING PROCESS:")
            print("-" * 60)
            print(block.thinking[:1000] + "..." if len(block.thinking) > 1000 else block.thinking)
            print("-" * 60)
        elif block.type == "text":
            print("\n✓ FINAL RECOMMENDATION:")
            print(block.text)

    print("\n")


def example_2_code_review():
    """Example: Code reviewer with extended thinking."""
    print("=" * 60)
    print("EXAMPLE 2: Code Review with Extended Thinking")
    print("=" * 60)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        thinking={
            "type": "enabled",
            "budget_tokens": 2000
        },
        system="""You are a senior software engineer conducting code reviews. When reviewing code:

1. Identify potential bugs and security vulnerabilities
2. Check for performance issues and edge cases
3. Evaluate code maintainability and readability
4. Consider testing coverage
5. Think about scalability implications

Take your time to analyze thoroughly before providing feedback.""",
        messages=[{
            "role": "user",
            "content": """Review this Python function:

```python
def process_payment(user_id, amount):
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    if user.balance >= amount:
        user.balance -= amount
        db.execute(f"UPDATE users SET balance = {user.balance} WHERE id = {user_id}")
        return True
    return False
```

What issues do you see?"""
        }]
    )

    # Print the response
    for block in response.content:
        if block.type == "thinking":
            print("\n🧠 ANALYSIS PROCESS:")
            print("-" * 60)
            print(block.thinking[:800] + "..." if len(block.thinking) > 800 else block.thinking)
            print("-" * 60)
        elif block.type == "text":
            print("\n✓ CODE REVIEW FINDINGS:")
            print(block.text)

    print("\n")


def example_3_medical_reasoning():
    """Example: Medical reasoning with extended thinking."""
    print("=" * 60)
    print("EXAMPLE 3: Medical Reasoning with Extended Thinking")
    print("=" * 60)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        thinking={
            "type": "enabled",
            "budget_tokens": 4000
        },
        system="""You are a medical education assistant helping students practice differential diagnosis.

When analyzing symptoms:
1. List all possible diagnoses (broad differential)
2. Consider the probability of each based on prevalence
3. Identify key distinguishing features
4. Think about what tests would rule in/out conditions
5. Consider the most likely diagnosis

Note: This is for educational purposes only, not real medical advice.
Think carefully through the diagnostic reasoning.""",
        messages=[{
            "role": "user",
            "content": """Patient presentation:
- 45-year-old male
- Chief complaint: Severe chest pain for 30 minutes
- Pain radiates to left arm
- Diaphoretic (sweating heavily)
- Nausea present
- History: Smoker, high blood pressure
- Vital signs: BP 160/95, HR 110, RR 22

What's your differential diagnosis and most likely diagnosis?"""
        }]
    )

    # Print the response
    for block in response.content:
        if block.type == "thinking":
            print("\n🧠 DIAGNOSTIC REASONING:")
            print("-" * 60)
            print(block.thinking[:1200] + "..." if len(block.thinking) > 1200 else block.thinking)
            print("-" * 60)
        elif block.type == "text":
            print("\n✓ DIFFERENTIAL DIAGNOSIS:")
            print(block.text)

    print("\n")


def example_4_compare_with_without_thinking():
    """Compare responses with and without thinking."""
    print("=" * 60)
    print("EXAMPLE 4: Comparing With/Without Extended Thinking")
    print("=" * 60)

    prompt = "What's the 15th number in the Fibonacci sequence, and explain how you calculated it?"

    # Without thinking
    print("\n--- WITHOUT EXTENDED THINKING ---")
    response_no_thinking = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    print(response_no_thinking.content[0].text)

    # With thinking
    print("\n--- WITH EXTENDED THINKING ---")
    response_with_thinking = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        thinking={
            "type": "enabled",
            "budget_tokens": 1500
        },
        messages=[{"role": "user", "content": prompt}]
    )

    for block in response_with_thinking.content:
        if block.type == "thinking":
            print("\n🧠 THINKING:")
            print(block.thinking[:500] + "..." if len(block.thinking) > 500 else block.thinking)
        elif block.type == "text":
            print("\n✓ ANSWER:")
            print(block.text)

    print("\n")


if __name__ == "__main__":
    # Run examples (uncomment the ones you want to try)

    print("\n🚀 Extended Thinking Examples\n")

    # Example 1: Financial Analysis
    example_1_financial_analysis()

    # Example 2: Code Review
    # example_2_code_review()

    # Example 3: Medical Reasoning
    # example_3_medical_reasoning()

    # Example 4: Comparison
    # example_4_compare_with_without_thinking()

    print("✅ Examples complete!\n")
