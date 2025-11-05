#!/usr/bin/env python3
"""
Code Quality MCP Integration Examples

Demonstrates Codacy and CodeLogic MCP server integrations
for code quality analysis and impact assessment.
"""

import os
import json
from typing import Dict, Any, Optional
from anthropic import Anthropic

MCP_BETA_HEADER = "mcp-client-2025-04-04"


class CodeQualityMCPClient:
    """Claude client with code quality MCP server integrations."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.mcp_servers = {}

    def configure_codacy(self, account_token: Optional[str] = None):
        """
        Configure Codacy MCP server.

        Provides code quality, security, and coverage analysis.

        Args:
            account_token: Codacy API token (defaults to CODACY_ACCOUNT_TOKEN env var)
        """
        token = account_token or os.environ.get("CODACY_ACCOUNT_TOKEN", "your-codacy-api-token")
        self.mcp_servers["codacy"] = {
            "command": "npx",
            "args": ["-y", "@codacy/mcp-server"],
            "env": {
                "CODACY_ACCOUNT_TOKEN": token
            }
        }
        print("✓ Configured Codacy MCP server")

    def configure_codelogic(
        self,
        server_url: Optional[str] = None,
        api_token: Optional[str] = None,
        workspace: Optional[str] = None
    ):
        """
        Configure CodeLogic MCP server.

        Provides software dependency and impact analysis.

        Args:
            server_url: CodeLogic server URL
            api_token: CodeLogic API token
            workspace: Workspace name
        """
        self.mcp_servers["codelogic"] = {
            "command": "uvx",
            "args": ["codelogic-mcp-server"],
            "env": {
                "CODELOGIC_SERVER_URL": server_url or os.environ.get("CODELOGIC_SERVER_URL", "https://your-codelogic-server.com"),
                "CODELOGIC_API_TOKEN": api_token or os.environ.get("CODELOGIC_API_TOKEN", "your-api-token"),
                "CODELOGIC_WORKSPACE": workspace or os.environ.get("CODELOGIC_WORKSPACE", "your-workspace-name")
            }
        }
        print("✓ Configured CodeLogic MCP server")

    def chat(
        self,
        message: str,
        system: Optional[str] = None,
        enable_thinking: bool = False,
        thinking_budget: int = 3000
    ) -> Dict[str, Any]:
        """
        Send message to Claude with MCP support.

        Args:
            message: User message
            system: System prompt
            enable_thinking: Enable extended thinking
            thinking_budget: Token budget for thinking

        Returns:
            Response with text, thinking, and usage stats
        """
        request_params = {
            "model": "claude-sonnet-4-5",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": message}]
        }

        if system:
            request_params["system"] = system

        if enable_thinking:
            request_params["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_budget
            }

        # Add MCP beta header
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
            }
        }


def example_codacy_quality_analysis():
    """Example: Analyze code quality with Codacy."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Codacy Code Quality Analysis")
    print("="*70 + "\n")

    client = CodeQualityMCPClient()
    client.configure_codacy()

    # Analyze code quality
    result = client.chat(
        message="""Analyze my repository's code quality:

1. List all active repositories
2. Show quality issues by severity
3. Identify security vulnerabilities
4. Review code coverage metrics
5. Analyze recent pull requests for quality trends

Provide specific recommendations for improvement.""",
        system="You have access to Codacy for code quality analysis. Analyze quality metrics and provide actionable insights.",
        enable_thinking=True,
        thinking_budget=3000
    )

    print("THINKING:")
    print("-" * 70)
    print(result["thinking"])
    print()

    print("QUALITY ANALYSIS:")
    print("-" * 70)
    print(result["text"])
    print()


def example_codacy_security_scan():
    """Example: Security vulnerability scanning with Codacy."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Codacy Security Vulnerability Scan")
    print("="*70 + "\n")

    client = CodeQualityMCPClient()
    client.configure_codacy()

    # Security analysis
    result = client.chat(
        message="""Perform comprehensive security analysis:

1. Scan for SAST (Static Analysis) vulnerabilities
2. Detect exposed secrets and credentials
3. Identify Software Composition Analysis (SCA) issues
4. Review Infrastructure as Code (IaC) security
5. Analyze security trends over time

Prioritize findings by severity and exploitability.""",
        system="You have access to Codacy security scanning. Provide detailed security assessment with remediation steps.",
        enable_thinking=True,
        thinking_budget=3500
    )

    print("THINKING:")
    print("-" * 70)
    print(result["thinking"][:500] + "..." if len(result["thinking"]) > 500 else result["thinking"])
    print()

    print("SECURITY REPORT:")
    print("-" * 70)
    print(result["text"])
    print()


def example_codacy_pr_review():
    """Example: Pull request quality review with Codacy."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Codacy Pull Request Quality Review")
    print("="*70 + "\n")

    client = CodeQualityMCPClient()
    client.configure_codacy()

    # PR analysis
    result = client.chat(
        message="""Review recent pull requests for quality:

1. Show all open pull requests
2. Analyze quality gate status for each PR
3. Identify PRs with new quality issues
4. Review code coverage impact
5. Highlight PRs that need attention

Provide recommendations for PR approval process.""",
        system="You have access to Codacy PR analysis. Review pull requests and provide quality insights.",
        enable_thinking=False
    )

    print("PR QUALITY REVIEW:")
    print("-" * 70)
    print(result["text"])
    print()


def example_codelogic_method_impact():
    """Example: Method impact analysis with CodeLogic."""
    print("\n" + "="*70)
    print("EXAMPLE 4: CodeLogic Method Impact Analysis")
    print("="*70 + "\n")

    client = CodeQualityMCPClient()
    client.configure_codelogic()

    # Method impact analysis
    result = client.chat(
        message="""Analyze method impact in our codebase:

1. Identify the most frequently called methods
2. Show dependency graph for critical methods
3. Analyze impact radius of changing specific methods
4. Find methods with the widest downstream effects
5. Identify tightly coupled components

Provide refactoring recommendations to reduce coupling.""",
        system="You have access to CodeLogic for impact analysis. Analyze method dependencies and provide architectural insights.",
        enable_thinking=True,
        thinking_budget=4000
    )

    print("THINKING:")
    print("-" * 70)
    print(result["thinking"])
    print()

    print("METHOD IMPACT ANALYSIS:")
    print("-" * 70)
    print(result["text"])
    print()


def example_codelogic_database_impact():
    """Example: Database impact analysis with CodeLogic."""
    print("\n" + "="*70)
    print("EXAMPLE 5: CodeLogic Database Impact Analysis")
    print("="*70 + "\n")

    client = CodeQualityMCPClient()
    client.configure_codelogic()

    # Database impact analysis
    result = client.chat(
        message="""Analyze database schema impact:

1. Show all database tables and their dependencies
2. Identify which code depends on specific tables
3. Analyze impact of changing table schemas
4. Find queries that would break with schema changes
5. Map database->code dependencies

Provide migration strategy for schema changes.""",
        system="You have access to CodeLogic database analysis. Analyze database dependencies and provide migration guidance.",
        enable_thinking=True,
        thinking_budget=3500
    )

    print("THINKING:")
    print("-" * 70)
    print(result["thinking"][:500] + "..." if len(result["thinking"]) > 500 else result["thinking"])
    print()

    print("DATABASE IMPACT ANALYSIS:")
    print("-" * 70)
    print(result["text"])
    print()


def example_combined_quality_impact():
    """Example: Combined code quality and impact analysis."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Combined Quality + Impact Analysis")
    print("="*70 + "\n")

    client = CodeQualityMCPClient()
    client.configure_codacy()
    client.configure_codelogic()

    # Comprehensive analysis
    result = client.chat(
        message="""Perform comprehensive code quality and impact analysis:

1. Code Quality (Codacy):
   - Identify files with highest number of quality issues
   - Show security vulnerabilities by severity
   - Review code coverage gaps

2. Impact Analysis (CodeLogic):
   - For files with quality issues, show their impact radius
   - Identify which other components depend on problematic code
   - Analyze refactoring risk

3. Recommendations:
   - Prioritize fixes based on quality issues + impact
   - Suggest refactoring order (low impact -> high impact)
   - Identify quick wins (high quality issues, low impact)
   - Highlight high-risk areas (quality issues + high impact)

Provide actionable improvement roadmap.""",
        system="You have access to both Codacy and CodeLogic. Provide integrated analysis combining quality metrics with impact assessment.",
        enable_thinking=True,
        thinking_budget=5000
    )

    print("THINKING:")
    print("-" * 70)
    print(result["thinking"][:500] + "..." if len(result["thinking"]) > 500 else result["thinking"])
    print()

    print("COMPREHENSIVE ANALYSIS:")
    print("-" * 70)
    print(result["text"])
    print()


def example_refactoring_safety():
    """Example: Assess refactoring safety."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Refactoring Safety Assessment")
    print("="*70 + "\n")

    client = CodeQualityMCPClient()
    client.configure_codacy()
    client.configure_codelogic()

    # Refactoring safety analysis
    result = client.chat(
        message="""I want to refactor the authentication module. Assess safety:

1. Quality Assessment (Codacy):
   - Current quality issues in auth module
   - Test coverage for auth code
   - Security vulnerabilities in auth

2. Impact Assessment (CodeLogic):
   - Which components depend on auth module?
   - What's the blast radius of changes?
   - Which databases/APIs are accessed?

3. Safety Recommendation:
   - Is refactoring safe now?
   - What should be done first?
   - Which tests need to be added?
   - What's the rollback plan?

Provide go/no-go decision with detailed reasoning.""",
        system="You have access to Codacy and CodeLogic. Assess refactoring safety and provide risk analysis.",
        enable_thinking=True,
        thinking_budget=4000
    )

    print("THINKING:")
    print("-" * 70)
    print(result["thinking"][:500] + "..." if len(result["thinking"]) > 500 else result["thinking"])
    print()

    print("REFACTORING SAFETY ASSESSMENT:")
    print("-" * 70)
    print(result["text"])
    print()


def main():
    """Run all examples."""
    print("\n" + "╔"+ "="*68 + "╗")
    print("║" + " "*10 + "Code Quality MCP Integration - Codacy & CodeLogic" + " "*8 + "║")
    print("╚" + "="*68 + "╝")

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n⚠️  Warning: ANTHROPIC_API_KEY not set")
        print("Set it with: export ANTHROPIC_API_KEY=your-key\n")
        return

    try:
        # Check for Codacy token
        if os.environ.get("CODACY_ACCOUNT_TOKEN"):
            example_codacy_quality_analysis()
            example_codacy_security_scan()
            example_codacy_pr_review()
        else:
            print("\n⚠️  Skipping Codacy examples (CODACY_ACCOUNT_TOKEN not set)")

        # Check for CodeLogic credentials
        if os.environ.get("CODELOGIC_SERVER_URL") and os.environ.get("CODELOGIC_API_TOKEN"):
            example_codelogic_method_impact()
            example_codelogic_database_impact()
        else:
            print("\n⚠️  Skipping CodeLogic examples (CODELOGIC_SERVER_URL or CODELOGIC_API_TOKEN not set)")

        # Combined example if both available
        if (os.environ.get("CODACY_ACCOUNT_TOKEN") and
            os.environ.get("CODELOGIC_SERVER_URL") and
            os.environ.get("CODELOGIC_API_TOKEN")):
            example_combined_quality_impact()
            example_refactoring_safety()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
