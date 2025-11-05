#!/usr/bin/env python3
"""
Extended Thinking Agent for Fly.io

Flask app with extended thinking, ready to deploy on Fly.io.
"""

import os
from flask import Flask, request, jsonify
from anthropic import Anthropic

app = Flask(__name__)

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "thinking-agent"}), 200


@app.route("/think", methods=["POST"])
def think():
    """
    Extended thinking endpoint.

    Request body:
    {
        "task": "Your problem or question",
        "thinking_budget": 3000,
        "domain": "general"
    }
    """
    try:
        data = request.get_json()

        if not data or "task" not in data:
            return jsonify({"error": "Missing 'task' in request body"}), 400

        task = data["task"]
        thinking_budget = data.get("thinking_budget", 3000)
        domain = data.get("domain", "general")
        context = data.get("context")

        # Domain-specific system prompts
        system_prompts = {
            "general": "You are an expert problem solver with deep analytical capabilities.",
            "math": "You are an expert mathematician. Show all work and explain your reasoning clearly.",
            "code": "You are an expert software engineer. Analyze code carefully and provide detailed explanations.",
            "strategy": "You are a strategic thinker. Consider multiple perspectives and long-term implications.",
            "data": "You are a data analyst. Examine data carefully and draw evidence-based conclusions."
        }

        system_prompt = system_prompts.get(domain, system_prompts["general"])

        if context:
            system_prompt += f"\n\nContext: {context}"

        # Create message with extended thinking
        response = anthropic_client.messages.create(
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

        return jsonify({
            "thinking": thinking,
            "answer": answer,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            "model": response.model
        }), 200

    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Quick analysis without extended thinking.

    Request body:
    {
        "query": "Your question",
        "context": "Context or code to analyze"
    }
    """
    try:
        data = request.get_json()

        if not data or "query" not in data:
            return jsonify({"error": "Missing 'query' in request body"}), 400

        query = data["query"]
        context = data.get("context", "")

        # Use faster model for quick analysis
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"{query}\n\n{context}"
            }]
        )

        result = ""
        for block in response.content:
            if block.type == "text":
                result = block.text

        return jsonify({
            "result": result,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }), 200

    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    """API documentation."""
    return jsonify({
        "service": "Thinking Agent API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "GET - Health check",
            "/think": "POST - Extended thinking analysis",
            "/analyze": "POST - Quick analysis",
            "/": "GET - This documentation"
        },
        "examples": {
            "think": {
                "url": "/think",
                "method": "POST",
                "body": {
                    "task": "Calculate the 20th Fibonacci number",
                    "thinking_budget": 3000,
                    "domain": "math"
                }
            },
            "analyze": {
                "url": "/analyze",
                "method": "POST",
                "body": {
                    "query": "What does this code do?",
                    "context": "def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)"
                }
            }
        }
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
