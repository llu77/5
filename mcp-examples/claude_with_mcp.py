#!/usr/bin/env python3
"""
Claude with MCP (Model Context Protocol) Integration

Use Claude with MCP servers for enhanced capabilities like filesystem access,
database queries, and more.
"""

import os
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic

# MCP beta header
MCP_BETA_HEADER = "mcp-client-2025-04-04"


class ClaudeMCPClient:
    """Claude client with MCP server integration."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.mcp_servers = {}

    def configure_mcp_server(self, name: str, config: Dict[str, Any]):
        """
        Configure an MCP server.

        Args:
            name: Server name (e.g., "filesystem", "database")
            config: Server configuration

        Example:
            client.configure_mcp_server("filesystem", {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-filesystem"],
                "env": {
                    "ALLOWED_PATHS": "/Users/me/projects"
                }
            })
        """
        self.mcp_servers[name] = config
        print(f"✓ Configured MCP server: {name}")

    def get_mcp_config(self) -> Dict[str, Any]:
        """Get complete MCP configuration."""
        return {"mcpServers": self.mcp_servers}

    def chat(
        self,
        message: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        enable_thinking: bool = False,
        thinking_budget: int = 3000
    ) -> Dict[str, Any]:
        """
        Send message to Claude with MCP support.

        Args:
            message: User message
            system: System prompt
            max_tokens: Maximum response tokens
            enable_thinking: Enable extended thinking
            thinking_budget: Token budget for thinking

        Returns:
            Response with text, thinking (if enabled), and usage stats
        """
        request_params = {
            "model": "claude-sonnet-4-5",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": message}]
        }

        if system:
            request_params["system"] = system

        if enable_thinking:
            request_params["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_budget
            }

        # Add MCP beta header if MCP servers configured
        extra_headers = {}
        if self.mcp_servers:
            extra_headers["anthropic-beta"] = MCP_BETA_HEADER

        response = self.client.messages.create(
            **request_params,
            extra_headers=extra_headers if extra_headers else None
        )

        # Extract response
        thinking = ""
        text = ""

        for block in response.content:
            if block.type == "thinking":
                thinking = block.thinking
            elif block.type == "text":
                text = block.text

        return {
            "text": text,
            "thinking": thinking if enable_thinking else None,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            "model": response.model
        }

    def analyze_files(
        self,
        query: str,
        file_paths: List[str],
        enable_thinking: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze files using MCP filesystem server.

        Args:
            query: Analysis query
            file_paths: List of file paths to analyze
            enable_thinking: Enable extended thinking

        Returns:
            Analysis results
        """
        # Build context from file paths
        context = f"Analyze these files:\n"
        for path in file_paths:
            context += f"- {path}\n"

        context += f"\nQuery: {query}"

        return self.chat(
            message=context,
            system="You have access to filesystem via MCP. Analyze the requested files.",
            enable_thinking=enable_thinking,
            thinking_budget=3000
        )

    def code_search(
        self,
        query: str,
        directory: str,
        file_pattern: str = "*.py"
    ) -> Dict[str, Any]:
        """
        Search and analyze code in a directory.

        Args:
            query: What to look for
            directory: Directory to search
            file_pattern: File pattern (e.g., "*.py", "*.js")

        Returns:
            Search results and analysis
        """
        message = f"""Search for code in directory: {directory}
File pattern: {file_pattern}
Query: {query}

Please:
1. Find relevant files
2. Analyze the code
3. Provide summary of findings"""

        return self.chat(
            message=message,
            system="You have filesystem access via MCP. Search and analyze code.",
            enable_thinking=True
        )


def example_filesystem_analysis():
    """Example: Analyze Python files in a project."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Filesystem Analysis with MCP")
    print("="*70 + "\n")

    # Initialize client
    client = ClaudeMCPClient()

    # Configure filesystem MCP server
    client.configure_mcp_server("filesystem", {
        "command": "npx",
        "args": ["@modelcontextprotocol/server-filesystem"],
        "env": {
            "ALLOWED_PATHS": "/Users/me/projects"
        }
    })

    print("MCP Configuration:")
    print(json.dumps(client.get_mcp_config(), indent=2))
    print()

    # Analyze files
    result = client.analyze_files(
        query="What is the architecture of this codebase?",
        file_paths=[
            "/Users/me/projects/app/main.py",
            "/Users/me/projects/app/models.py",
            "/Users/me/projects/app/routes.py"
        ],
        enable_thinking=True
    )

    print("THINKING:")
    print("-" * 70)
    print(result["thinking"])
    print()

    print("ANALYSIS:")
    print("-" * 70)
    print(result["text"])
    print()

    print("USAGE:")
    print(f"  Input:  {result['usage']['input_tokens']} tokens")
    print(f"  Output: {result['usage']['output_tokens']} tokens")
    print()


def example_code_search():
    """Example: Search for security vulnerabilities."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Code Search with MCP")
    print("="*70 + "\n")

    client = ClaudeMCPClient()

    # Configure MCP
    client.configure_mcp_server("filesystem", {
        "command": "npx",
        "args": ["@modelcontextprotocol/server-filesystem"],
        "env": {
            "ALLOWED_PATHS": "/Users/me/projects"
        }
    })

    # Search for security issues
    result = client.code_search(
        query="Find potential SQL injection vulnerabilities",
        directory="/Users/me/projects/app",
        file_pattern="*.py"
    )

    print("SECURITY AUDIT:")
    print("-" * 70)
    print(result["text"])
    print()


def example_project_documentation():
    """Example: Generate documentation from code."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Documentation Generation with MCP")
    print("="*70 + "\n")

    client = ClaudeMCPClient()

    # Configure MCP
    client.configure_mcp_server("filesystem", {
        "command": "npx",
        "args": ["@modelcontextprotocol/server-filesystem"],
        "env": {
            "ALLOWED_PATHS": "/Users/me/projects"
        }
    })

    # Generate docs
    result = client.chat(
        message="""Analyze the codebase at /Users/me/projects/app and generate:
1. README.md with project overview
2. API documentation
3. Architecture diagram (in Mermaid)
4. Setup instructions""",
        system="You have filesystem access. Read the code and generate comprehensive documentation.",
        enable_thinking=True,
        thinking_budget=5000
    )

    print("GENERATED DOCUMENTATION:")
    print("-" * 70)
    print(result["text"])
    print()


def example_interactive_session():
    """Example: Interactive session with MCP."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Interactive Code Analysis")
    print("="*70 + "\n")

    client = ClaudeMCPClient()

    # Configure MCP
    client.configure_mcp_server("filesystem", {
        "command": "npx",
        "args": ["@modelcontextprotocol/server-filesystem"],
        "env": {
            "ALLOWED_PATHS": "/Users/me/projects"
        }
    })

    # Conversation history
    conversation = []

    queries = [
        "What files are in the project?",
        "Show me the main entry point",
        "Are there any security vulnerabilities?",
        "Suggest improvements to the architecture"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}: {query}")
        print("-" * 70)

        result = client.chat(
            message=query,
            system="You have filesystem access. Answer questions about the codebase.",
            enable_thinking=False
        )

        print(result["text"])
        conversation.append({
            "query": query,
            "response": result["text"]
        })

    print("\n" + "="*70)
    print("Session complete!")
    print(f"Total queries: {len(conversation)}")
    print("="*70)


def main():
    """Run all examples."""
    print("\n" + "╔"+ "="*68 + "╗")
    print("║" + " "*10 + "Claude with MCP - Filesystem Integration" + " "*16 + "║")
    print("╚" + "="*68 + "╝")

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n⚠️  Warning: ANTHROPIC_API_KEY not set")
        print("Set it with: export ANTHROPIC_API_KEY=your-key\n")
        return

    try:
        # Run examples
        example_filesystem_analysis()
        example_code_search()
        example_project_documentation()
        example_interactive_session()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
