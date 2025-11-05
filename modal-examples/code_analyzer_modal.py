#!/usr/bin/env python3
"""
Code Analyzer with Modal

Analyze code files, repositories, and directories using Claude.
Based on the original Modal + Anthropic example.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import modal

# Create Modal app
app = modal.App(
    image=modal.Image.debian_slim().pip_install("anthropic", "gitpython")
)


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=300
)
def analyze_context(context: str, query: str, model: str = "claude-3-haiku-20240307") -> List[str]:
    """
    Analyze code or text context with a query.

    Args:
        context: Code or text to analyze
        query: Question or analysis request
        model: Claude model to use

    Returns:
        List of text responses
    """
    import anthropic

    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": query + "\n\n" + context
        }]
    )

    return [block.text for block in message.content]


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=600
)
def analyze_file(
    file_path: str,
    query: str = "Can you summarize what this code does?",
    model: str = "claude-3-haiku-20240307"
) -> Dict[str, Any]:
    """
    Analyze a single file.

    Args:
        file_path: Path to file
        query: Analysis query
        model: Claude model

    Returns:
        Analysis results
    """
    try:
        content = Path(file_path).read_text()
    except Exception as e:
        return {
            "file": file_path,
            "error": str(e),
            "analysis": None
        }

    analysis = analyze_context.remote(content, query, model)

    return {
        "file": file_path,
        "query": query,
        "analysis": analysis,
        "error": None
    }


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=1800
)
def analyze_directory(
    directory: str,
    pattern: str = "*.py",
    query: str = "Summarize what this code does",
    model: str = "claude-3-haiku-20240307",
    max_files: int = 50
) -> List[Dict[str, Any]]:
    """
    Analyze all files in a directory matching pattern.

    Args:
        directory: Directory path
        pattern: Glob pattern for files
        query: Analysis query
        model: Claude model
        max_files: Maximum files to analyze

    Returns:
        List of analysis results
    """
    files = list(Path(directory).glob(pattern))[:max_files]

    results = []
    for file_path in files:
        result = analyze_file.remote(
            file_path=str(file_path),
            query=query,
            model=model
        )
        results.append(result)

    return results


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=1800,
    network_file_systems={
        "/cache": modal.NetworkFileSystem.from_name("repo-cache", create_if_missing=True)
    }
)
def analyze_repository(
    repo_url: str,
    file_pattern: str = "**/*.py",
    query: str = "Explain what this file does",
    model: str = "claude-3-haiku-20240307",
    max_files: int = 20
) -> Dict[str, Any]:
    """
    Clone and analyze a git repository.

    Args:
        repo_url: Git repository URL
        file_pattern: Glob pattern for files
        query: Analysis query
        model: Claude model
        max_files: Maximum files to analyze

    Returns:
        Repository analysis results
    """
    import git
    import tempfile
    import shutil

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Clone repository
            print(f"Cloning {repo_url}...")
            repo = git.Repo.clone_from(repo_url, tmpdir)
            print(f"Cloned to {tmpdir}")

            # Find matching files
            files = list(Path(tmpdir).glob(file_pattern))[:max_files]
            print(f"Found {len(files)} files matching {file_pattern}")

            # Analyze files
            results = []
            for file_path in files:
                try:
                    content = file_path.read_text()
                    relative_path = file_path.relative_to(tmpdir)

                    analysis = analyze_context.remote(content, query, model)

                    results.append({
                        "file": str(relative_path),
                        "analysis": analysis,
                        "error": None
                    })
                except Exception as e:
                    results.append({
                        "file": str(file_path),
                        "analysis": None,
                        "error": str(e)
                    })

            return {
                "repository": repo_url,
                "files_analyzed": len(results),
                "results": results,
                "error": None
            }

        except Exception as e:
            return {
                "repository": repo_url,
                "files_analyzed": 0,
                "results": [],
                "error": str(e)
            }


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=600
)
def compare_implementations(
    code1: str,
    code2: str,
    language: str = "python"
) -> Dict[str, Any]:
    """
    Compare two code implementations.

    Args:
        code1: First implementation
        code2: Second implementation
        language: Programming language

    Returns:
        Comparison analysis
    """
    import anthropic

    client = anthropic.Anthropic()

    prompt = f"""Compare these two {language} implementations:

Implementation 1:
```{language}
{code1}
```

Implementation 2:
```{language}
{code2}
```

Analyze:
1. Functionality differences
2. Performance implications
3. Code quality and maintainability
4. Which is better and why
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    analysis = ""
    for block in response.content:
        if block.type == "text":
            analysis = block.text

    return {
        "language": language,
        "analysis": analysis
    }


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=900
)
def security_audit(
    code: str,
    language: str = "python",
    framework: Optional[str] = None
) -> Dict[str, Any]:
    """
    Security audit of code.

    Args:
        code: Code to audit
        language: Programming language
        framework: Framework if applicable

    Returns:
        Security audit results
    """
    import anthropic

    client = anthropic.Anthropic()

    prompt = f"""Perform a security audit on this {language} code"""
    if framework:
        prompt += f" (using {framework} framework)"
    prompt += f"""

```{language}
{code}
```

Check for:
1. SQL injection vulnerabilities
2. XSS vulnerabilities
3. Authentication/authorization issues
4. Input validation problems
5. Sensitive data exposure
6. Insecure dependencies
7. Other OWASP Top 10 vulnerabilities

Provide:
- List of issues with severity (Critical/High/Medium/Low)
- Explanation of each issue
- Recommended fixes
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    audit = ""
    for block in response.content:
        if block.type == "text":
            audit = block.text

    return {
        "language": language,
        "framework": framework,
        "audit": audit
    }


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")],
    timeout=600
)
def refactor_suggestion(
    code: str,
    language: str = "python",
    goal: str = "improve code quality and maintainability"
) -> Dict[str, Any]:
    """
    Get refactoring suggestions.

    Args:
        code: Code to refactor
        language: Programming language
        goal: Refactoring goal

    Returns:
        Refactoring suggestions
    """
    import anthropic

    client = anthropic.Anthropic()

    prompt = f"""Suggest refactorings for this {language} code to {goal}:

```{language}
{code}
```

Provide:
1. Specific refactoring suggestions
2. Refactored code examples
3. Explanation of improvements
4. Potential risks or trade-offs
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    suggestions = ""
    for block in response.content:
        if block.type == "text":
            suggestions = block.text

    return {
        "language": language,
        "goal": goal,
        "suggestions": suggestions
    }


@app.local_entrypoint()
def main(
    context: Optional[str] = None,
    query: str = "Can you summarize what this code does?",
    file: Optional[str] = None,
    directory: Optional[str] = None,
    repo: Optional[str] = None,
    pattern: str = "**/*.py",
    model: str = "claude-3-haiku-20240307"
):
    """
    CLI entrypoint for code analyzer.

    Examples:
        # Analyze this file
        modal run code_analyzer_modal.py

        # Analyze specific file
        modal run code_analyzer_modal.py --file "path/to/file.py"

        # Analyze directory
        modal run code_analyzer_modal.py \
            --directory "src/" \
            --pattern "**/*.py" \
            --query "Find potential bugs"

        # Analyze repository
        modal run code_analyzer_modal.py \
            --repo "https://github.com/user/repo" \
            --pattern "**/*.py" \
            --query "Summarize each file"
    """

    if repo:
        # Analyze repository
        print(f"Analyzing repository: {repo}")
        result = analyze_repository.remote(
            repo_url=repo,
            file_pattern=pattern,
            query=query,
            model=model
        )

        print(f"\n{'='*70}")
        print(f"REPOSITORY ANALYSIS: {repo}")
        print(f"{'='*70}")
        print(f"Files analyzed: {result['files_analyzed']}")

        if result['error']:
            print(f"Error: {result['error']}")
        else:
            for file_result in result['results']:
                print(f"\n--- {file_result['file']} ---")
                if file_result['error']:
                    print(f"Error: {file_result['error']}")
                else:
                    for response in file_result['analysis']:
                        print(response)

    elif directory:
        # Analyze directory
        print(f"Analyzing directory: {directory}")
        results = analyze_directory.remote(
            directory=directory,
            pattern=pattern,
            query=query,
            model=model
        )

        print(f"\n{'='*70}")
        print(f"DIRECTORY ANALYSIS: {directory}")
        print(f"{'='*70}")
        print(f"Files analyzed: {len(results)}")

        for result in results:
            print(f"\n--- {result['file']} ---")
            if result['error']:
                print(f"Error: {result['error']}")
            else:
                for response in result['analysis']:
                    print(response)

    elif file:
        # Analyze file
        print(f"Analyzing file: {file}")
        result = analyze_file.remote(
            file_path=file,
            query=query,
            model=model
        )

        print(f"\n{'='*70}")
        print(f"FILE ANALYSIS: {file}")
        print(f"{'='*70}")
        print(f"Query: {query}")

        if result['error']:
            print(f"Error: {result['error']}")
        else:
            for response in result['analysis']:
                print(response)

    else:
        # Analyze this file by default
        if context is None:
            context = Path(__file__).read_text()

        print(f"Analyzing code context ({len(context)} characters)")
        completion = analyze_context.remote(context, query, model)

        print(f"\n{'='*70}")
        print(f"QUERY: {query}")
        print(f"{'='*70}\n")

        for response in completion:
            print(response)


# Web API endpoints
@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")]
)
@modal.web_endpoint(method="POST")
def api_analyze(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze code via API.

    POST /api_analyze
    {
        "code": "your code here",
        "query": "What does this do?",
        "model": "claude-3-haiku-20240307"
    }
    """
    code = request_data.get("code")
    query = request_data.get("query", "Analyze this code")
    model = request_data.get("model", "claude-3-haiku-20240307")

    if not code:
        return {"error": "Missing 'code' field"}

    analysis = analyze_context.remote(code, query, model)

    return {
        "query": query,
        "analysis": analysis
    }


@app.function(
    secrets=[modal.Secret.from_name("anthropic-secret")]
)
@modal.web_endpoint(method="POST")
def api_security_audit(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Security audit via API.

    POST /api_security_audit
    {
        "code": "your code here",
        "language": "python",
        "framework": "django"
    }
    """
    code = request_data.get("code")
    if not code:
        return {"error": "Missing 'code' field"}

    result = security_audit.remote(
        code=code,
        language=request_data.get("language", "python"),
        framework=request_data.get("framework")
    )

    return result


if __name__ == "__main__":
    # Example usage
    sample_code = '''
def process_user_input(user_id, data):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()
'''

    print("Running security audit on sample code...")
    result = security_audit.remote(sample_code, "python")
    print(result["audit"])
