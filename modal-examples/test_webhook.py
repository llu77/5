#!/usr/bin/env python3
"""
Modal Webhook Testing Script

Test deployed Modal webhooks with proper authentication headers.
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Your Modal webhook credentials
WEBHOOK_CREDENTIALS = {
    "key": "wk-MqtJuh2UbPbBHNuKTf8BOm",
    "secret": "ws-erJAdpAlGXBKXJFXzhlWR3"
}

# Account ID
ACCOUNT_ID = "ac-qp2iIJLVPa4JpwLDc95lW3"


def call_webhook(
    url: str,
    payload: Dict[str, Any],
    use_auth: bool = True,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Call Modal webhook with optional authentication.

    Args:
        url: Webhook URL
        payload: JSON payload
        use_auth: Include authentication headers
        timeout: Request timeout in seconds

    Returns:
        Response data
    """
    headers = {
        "Content-Type": "application/json"
    }

    if use_auth:
        headers["Modal-Key"] = WEBHOOK_CREDENTIALS["key"]
        headers["Modal-Secret"] = WEBHOOK_CREDENTIALS["secret"]

    try:
        print(f"📤 Calling: {url}")
        print(f"🔐 Auth: {'Enabled' if use_auth else 'Disabled'}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}\n")

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=timeout
        )

        print(f"✅ Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"📊 Response:")
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return {"error": response.text, "status_code": response.status_code}

    except requests.exceptions.Timeout:
        print(f"⏱️  Request timed out after {timeout} seconds")
        return {"error": "Request timeout"}
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {"error": str(e)}


def test_thinking_agent(base_url: str):
    """Test thinking agent endpoint."""
    print("\n" + "="*70)
    print("TEST 1: THINKING AGENT")
    print("="*70 + "\n")

    url = f"{base_url}/api" if not base_url.endswith("/api") else base_url

    payload = {
        "task": "Calculate the 20th Fibonacci number and explain your reasoning",
        "domain": "math",
        "thinking_budget": 2000
    }

    result = call_webhook(url, payload)
    return result


def test_orchestrator(base_url: str):
    """Test orchestrator-workers endpoint."""
    print("\n" + "="*70)
    print("TEST 2: ORCHESTRATOR-WORKERS")
    print("="*70 + "\n")

    url = f"{base_url}/api" if not base_url.endswith("/api") else base_url

    payload = {
        "task": "Analyze the security implications of using JWT tokens for authentication",
        "max_workers": 3
    }

    result = call_webhook(url, payload, timeout=600)
    return result


def test_code_analyzer(base_url: str):
    """Test code analyzer endpoint."""
    print("\n" + "="*70)
    print("TEST 3: CODE ANALYZER - Security Audit")
    print("="*70 + "\n")

    url = f"{base_url}/api_security_audit" if not base_url.endswith("/api_security_audit") else base_url

    payload = {
        "code": '''
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    return cursor.fetchone()
''',
        "language": "python"
    }

    result = call_webhook(url, payload)
    return result


def test_code_analysis(base_url: str):
    """Test code analysis endpoint."""
    print("\n" + "="*70)
    print("TEST 4: CODE ANALYZER - Code Analysis")
    print("="*70 + "\n")

    url = f"{base_url}/api_analyze" if not base_url.endswith("/api_analyze") else base_url

    payload = {
        "code": '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
''',
        "query": "Analyze this code and suggest optimizations",
        "model": "claude-3-haiku-20240307"
    }

    result = call_webhook(url, payload)
    return result


def interactive_test():
    """Interactive testing mode."""
    print("\n" + "="*70)
    print("MODAL WEBHOOK TESTER - Interactive Mode")
    print("="*70 + "\n")

    url = input("Enter webhook URL: ").strip()

    print("\nSelect test:")
    print("1. Thinking Agent")
    print("2. Orchestrator-Workers")
    print("3. Code Security Audit")
    print("4. Code Analysis")
    print("5. Custom Payload")

    choice = input("\nChoice (1-5): ").strip()

    if choice == "1":
        test_thinking_agent(url)
    elif choice == "2":
        test_orchestrator(url)
    elif choice == "3":
        test_code_analyzer(url)
    elif choice == "4":
        test_code_analysis(url)
    elif choice == "5":
        print("\nEnter JSON payload (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)

        payload_str = "\n".join(lines[:-1])  # Remove last empty line
        try:
            payload = json.loads(payload_str)
            call_webhook(url, payload)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
    else:
        print("Invalid choice")


def main():
    """CLI entrypoint."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test Modal webhook endpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python test_webhook.py

  # Test thinking agent
  python test_webhook.py --url https://your-modal-url.modal.run --test thinking

  # Test code security audit
  python test_webhook.py --url https://your-modal-url.modal.run --test security

  # Custom payload
  python test_webhook.py --url https://your-modal-url.modal.run \
    --payload '{"task": "Your question"}'

  # No authentication
  python test_webhook.py --url https://your-modal-url.modal.run \
    --test thinking --no-auth
"""
    )

    parser.add_argument(
        "--url",
        help="Webhook URL"
    )

    parser.add_argument(
        "--test",
        choices=["thinking", "orchestrator", "security", "analyze"],
        help="Test type"
    )

    parser.add_argument(
        "--payload",
        help="Custom JSON payload"
    )

    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Don't include authentication headers"
    )

    args = parser.parse_args()

    if not args.url:
        # Interactive mode
        interactive_test()
        return

    # Command-line mode
    if args.payload:
        try:
            payload = json.loads(args.payload)
            call_webhook(args.url, payload, use_auth=not args.no_auth)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON payload: {e}")
            sys.exit(1)

    elif args.test == "thinking":
        test_thinking_agent(args.url)

    elif args.test == "orchestrator":
        test_orchestrator(args.url)

    elif args.test == "security":
        test_code_analyzer(args.url)

    elif args.test == "analyze":
        test_code_analysis(args.url)

    else:
        print("❌ Please specify --test or --payload")
        sys.exit(1)


if __name__ == "__main__":
    main()
