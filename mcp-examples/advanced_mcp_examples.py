#!/usr/bin/env python3
"""
Advanced MCP Integration Examples

Demonstrates Cloudflare and Iceberg MCP server integrations
for observability, bindings, and data lake analytics.
"""

import os
import json
from typing import Dict, Any, Optional
from anthropic import Anthropic

MCP_BETA_HEADER = "mcp-client-2025-04-04"


class AdvancedMCPClient:
    """Claude client with advanced MCP server integrations."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.mcp_servers = {}

    def configure_cloudflare_observability(self):
        """
        Configure Cloudflare Observability MCP server.

        Provides access to Cloudflare analytics and monitoring data.
        """
        self.mcp_servers["cloudflare-observability"] = {
            "command": "npx",
            "args": ["mcp-remote", "https://observability.mcp.cloudflare.com/mcp"],
            "env": {}
        }
        print("✓ Configured Cloudflare Observability MCP server")

    def configure_cloudflare_bindings(self):
        """
        Configure Cloudflare Bindings MCP server.

        Provides access to Cloudflare Workers bindings (KV, D1, R2, etc.).
        """
        self.mcp_servers["cloudflare-bindings"] = {
            "command": "npx",
            "args": ["mcp-remote", "https://bindings.mcp.cloudflare.com/mcp"],
            "env": {}
        }
        print("✓ Configured Cloudflare Bindings MCP server")

    def configure_iceberg(
        self,
        impala_host: str,
        impala_port: str = "21050",
        impala_user: str = "",
        impala_password: str = "",
        impala_database: str = "default"
    ):
        """
        Configure Iceberg MCP server for Apache Iceberg table queries.

        Args:
            impala_host: Impala server hostname
            impala_port: Impala port (default: 21050)
            impala_user: Authentication username
            impala_password: Authentication password
            impala_database: Database name
        """
        self.mcp_servers["iceberg"] = {
            "command": "uvx",
            "args": ["git+https://github.com/cloudera/iceberg-mcp-server@main"],
            "env": {
                "IMPALA_HOST": impala_host,
                "IMPALA_PORT": impala_port,
                "IMPALA_USER": impala_user,
                "IMPALA_PASSWORD": impala_password,
                "IMPALA_DATABASE": impala_database,
                "MCP_TRANSPORT": "stdio"
            }
        }
        print(f"✓ Configured Iceberg MCP server (Database: {impala_database})")

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


def example_cloudflare_observability():
    """Example: Query Cloudflare analytics and metrics."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Cloudflare Observability Analytics")
    print("="*70 + "\n")

    client = AdvancedMCPClient()
    client.configure_cloudflare_observability()

    # Query analytics
    result = client.chat(
        message="""Analyze my Cloudflare traffic patterns:
1. Show top countries by requests
2. Identify peak traffic hours
3. Analyze cache hit rates
4. Detect any unusual patterns or anomalies""",
        system="You have access to Cloudflare observability data. Analyze metrics and provide insights.",
        enable_thinking=True,
        thinking_budget=3000
    )

    print("THINKING:")
    print("-" * 70)
    print(result["thinking"])
    print()

    print("ANALYTICS REPORT:")
    print("-" * 70)
    print(result["text"])
    print()


def example_cloudflare_bindings():
    """Example: Interact with Cloudflare Workers bindings."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Cloudflare Bindings Management")
    print("="*70 + "\n")

    client = AdvancedMCPClient()
    client.configure_cloudflare_bindings()

    # Query KV store
    result = client.chat(
        message="""Manage Cloudflare KV storage:
1. List all KV namespaces
2. Show keys in the 'cache' namespace
3. Analyze storage usage
4. Suggest optimization strategies""",
        system="You have access to Cloudflare Workers bindings (KV, D1, R2). Manage and optimize storage.",
        enable_thinking=False
    )

    print("KV MANAGEMENT:")
    print("-" * 70)
    print(result["text"])
    print()


def example_iceberg_data_lake():
    """Example: Query Apache Iceberg data lake."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Iceberg Data Lake Analytics")
    print("="*70 + "\n")

    client = AdvancedMCPClient()

    # Configure Iceberg (use environment variables for credentials)
    client.configure_iceberg(
        impala_host=os.getenv("IMPALA_HOST", "localhost"),
        impala_port=os.getenv("IMPALA_PORT", "21050"),
        impala_user=os.getenv("IMPALA_USER", ""),
        impala_password=os.getenv("IMPALA_PASSWORD", ""),
        impala_database=os.getenv("IMPALA_DATABASE", "default")
    )

    # Query data lake
    result = client.chat(
        message="""Analyze our data lake:
1. Show available tables in the database
2. Query the 'sales' table for last month's revenue
3. Identify top-selling products
4. Provide year-over-year comparison""",
        system="You have read-only access to Iceberg tables via Impala. Query and analyze data.",
        enable_thinking=True,
        thinking_budget=4000
    )

    print("THINKING:")
    print("-" * 70)
    print(result["thinking"])
    print()

    print("DATA LAKE ANALYSIS:")
    print("-" * 70)
    print(result["text"])
    print()


def example_multi_source_integration():
    """Example: Combine multiple MCP sources."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Multi-Source Integration")
    print("="*70 + "\n")

    client = AdvancedMCPClient()

    # Configure all servers
    client.configure_cloudflare_observability()
    client.configure_cloudflare_bindings()
    client.configure_iceberg(
        impala_host=os.getenv("IMPALA_HOST", "localhost"),
        impala_database=os.getenv("IMPALA_DATABASE", "default")
    )

    # Comprehensive analysis across sources
    result = client.chat(
        message="""Perform cross-platform analysis:

1. Cloudflare Analytics:
   - Show traffic patterns and top endpoints
   - Identify high-latency requests

2. Cloudflare Storage:
   - Analyze KV cache hit rates
   - Review D1 database performance

3. Data Lake:
   - Query user activity from Iceberg tables
   - Correlate with traffic patterns

4. Recommendations:
   - Suggest caching strategies
   - Identify optimization opportunities
   - Provide cost-saving recommendations""",
        system="You have access to Cloudflare observability, bindings, and Iceberg data lake. Provide comprehensive analysis.",
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


def example_iceberg_schema_analysis():
    """Example: Analyze Iceberg table schemas."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Iceberg Schema Analysis")
    print("="*70 + "\n")

    client = AdvancedMCPClient()
    client.configure_iceberg(
        impala_host=os.getenv("IMPALA_HOST", "localhost"),
        impala_database=os.getenv("IMPALA_DATABASE", "default")
    )

    # Schema analysis
    result = client.chat(
        message="""Analyze database schema:
1. List all tables
2. Show schema for each table
3. Identify relationships between tables
4. Suggest indexes for performance
5. Recommend partitioning strategies""",
        system="You have access to Iceberg tables. Analyze schemas and provide optimization recommendations.",
        enable_thinking=True
    )

    print("SCHEMA ANALYSIS:")
    print("-" * 70)
    print(result["text"])
    print()


def example_cloudflare_performance_tuning():
    """Example: Cloudflare performance optimization."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Cloudflare Performance Tuning")
    print("="*70 + "\n")

    client = AdvancedMCPClient()
    client.configure_cloudflare_observability()
    client.configure_cloudflare_bindings()

    # Performance analysis
    result = client.chat(
        message="""Optimize Cloudflare performance:

Observability Analysis:
- Identify slowest endpoints
- Analyze cache effectiveness
- Review error rates by endpoint

Bindings Optimization:
- Evaluate KV access patterns
- Suggest Worker optimizations
- Recommend caching strategies

Provide:
1. Performance bottlenecks
2. Specific optimization steps
3. Expected performance gains
4. Implementation priority""",
        system="You have full access to Cloudflare metrics and bindings. Optimize for performance.",
        enable_thinking=True,
        thinking_budget=4000
    )

    print("THINKING:")
    print("-" * 70)
    print(result["thinking"][:500] + "..." if len(result["thinking"]) > 500 else result["thinking"])
    print()

    print("OPTIMIZATION RECOMMENDATIONS:")
    print("-" * 70)
    print(result["text"])
    print()


def main():
    """Run all examples."""
    print("\n" + "╔"+ "="*68 + "╗")
    print("║" + " "*8 + "Advanced MCP Integration - Cloudflare & Iceberg" + " "*14 + "║")
    print("╚" + "="*68 + "╝")

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n⚠️  Warning: ANTHROPIC_API_KEY not set")
        print("Set it with: export ANTHROPIC_API_KEY=your-key\n")
        return

    try:
        # Run examples
        example_cloudflare_observability()
        example_cloudflare_bindings()

        # Check for Iceberg credentials before running
        if os.environ.get("IMPALA_HOST"):
            example_iceberg_data_lake()
            example_iceberg_schema_analysis()
        else:
            print("\n⚠️  Skipping Iceberg examples (IMPALA_HOST not set)")

        # Multi-source integration
        example_multi_source_integration()
        example_cloudflare_performance_tuning()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
