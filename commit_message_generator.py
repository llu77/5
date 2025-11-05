#!/usr/bin/env python3
"""
Smart Commit Message Generator

Generates conventional commit messages from git diffs or descriptions.
Follows Angular/Conventional Commits specification.
"""

import os
import sys
import argparse
import subprocess
from anthropic import Anthropic


COMMIT_TYPES = {
    "feat": "A new feature",
    "fix": "A bug fix",
    "docs": "Documentation only changes",
    "style": "Changes that don't affect code meaning (formatting, etc)",
    "refactor": "Code change that neither fixes a bug nor adds a feature",
    "perf": "Code change that improves performance",
    "test": "Adding or correcting tests",
    "chore": "Changes to build process or auxiliary tools",
    "ci": "Changes to CI configuration files and scripts",
    "build": "Changes that affect the build system or dependencies",
    "revert": "Reverts a previous commit"
}


COMMIT_MESSAGE_PROMPT = """You are a commit message generator following the Conventional Commits specification.

Analyze the following information and generate a well-structured commit message:

<changes>
{changes}
</changes>

{context}

Generate a commit message in this format:

<type>(<scope>): <short description>

<body>
- Detailed explanation of changes
- Why the changes were made
- Any important notes
</body>

<footer>
{footer_notes}
</footer>

Guidelines:
1. Type must be one of: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert
2. Scope should be the module/component affected (optional but recommended)
3. Short description should be lowercase, imperative mood, no period
4. Body should explain what and why (not how)
5. Use bullet points for multiple changes
6. Keep lines under 72 characters for readability
7. Add breaking change notice in footer if applicable

Examples:

feat(auth): implement JWT-based authentication

Add login endpoint with token generation and validation.
Use RS256 algorithm for signing tokens.

fix(reports): correct date formatting in timezone conversion

Dates were displaying incorrectly due to timezone handling bug.
Now using UTC timestamps consistently across report generation.

BREAKING CHANGE: API now requires Authorization header for all endpoints

chore: update dependencies and refactor error handling

- Upgrade lodash to 4.17.21 for security patch
- Standardize error response format across endpoints
- Add error logging middleware

Provide your commit message following this format."""


class CommitMessageGenerator:
    """Generate conventional commit messages."""

    def __init__(self, api_key: str = None):
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-5"

    def get_git_diff(self, staged_only: bool = True) -> str:
        """Get git diff for commit message generation."""
        try:
            cmd = ["git", "diff", "--cached"] if staged_only else ["git", "diff"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git diff failed: {e}")

    def get_git_status(self) -> str:
        """Get git status summary."""
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git status failed: {e}")

    def generate_from_diff(
        self,
        diff: str = None,
        context: str = "",
        breaking_change: bool = False,
        issue_refs: list = None
    ) -> dict:
        """
        Generate commit message from git diff.

        Args:
            diff: Git diff text (if None, gets from staged changes)
            context: Additional context about the changes
            breaking_change: Whether this is a breaking change
            issue_refs: List of issue/ticket references

        Returns:
            Dictionary with commit message components
        """
        if diff is None:
            diff = self.get_git_diff()

        if not diff.strip():
            raise ValueError("No changes to commit (git diff is empty)")

        # Build context string
        context_str = ""
        if context:
            context_str += f"\nAdditional Context:\n{context}\n"

        # Build footer notes
        footer_notes = []
        if breaking_change:
            footer_notes.append("Include 'BREAKING CHANGE:' notice if applicable")
        if issue_refs:
            footer_notes.append(f"Reference issues: {', '.join(issue_refs)}")

        footer_str = "\n".join(footer_notes) if footer_notes else "No footer needed"

        # Generate commit message
        prompt = COMMIT_MESSAGE_PROMPT.format(
            changes=diff[:8000],  # Limit diff size
            context=context_str,
            footer_notes=footer_str
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        message_text = response.content[0].text.strip()

        # Parse components
        lines = message_text.split("\n")
        header = lines[0] if lines else ""

        body_start = 1
        # Skip empty lines after header
        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1

        body_lines = []
        footer_lines = []
        in_footer = False

        for line in lines[body_start:]:
            if line.strip().startswith("BREAKING CHANGE:") or \
               line.strip().startswith("Refs:") or \
               line.strip().startswith("Closes:"):
                in_footer = True

            if in_footer:
                footer_lines.append(line)
            else:
                body_lines.append(line)

        body = "\n".join(body_lines).strip()
        footer = "\n".join(footer_lines).strip()

        return {
            "header": header,
            "body": body,
            "footer": footer,
            "full_message": message_text,
            "formatted": self._format_for_git(header, body, footer)
        }

    def generate_from_description(
        self,
        description: str,
        commit_type: str = None,
        scope: str = None,
        breaking_change: bool = False,
        issue_refs: list = None
    ) -> dict:
        """
        Generate commit message from description.

        Args:
            description: Plain text description of changes
            commit_type: Type of commit (feat, fix, etc)
            scope: Scope of changes
            breaking_change: Whether this is a breaking change
            issue_refs: List of issue references

        Returns:
            Dictionary with commit message components
        """
        context = ""
        if commit_type:
            context += f"\nCommit Type: {commit_type}"
        if scope:
            context += f"\nScope: {scope}"

        footer_notes = []
        if breaking_change:
            footer_notes.append("This is a BREAKING CHANGE")
        if issue_refs:
            footer_notes.append(f"Reference issues: {', '.join(issue_refs)}")

        footer_str = "\n".join(footer_notes) if footer_notes else "No footer needed"

        prompt = COMMIT_MESSAGE_PROMPT.format(
            changes=f"Description: {description}",
            context=context,
            footer_notes=footer_str
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        message_text = response.content[0].text.strip()

        # Parse same as above
        lines = message_text.split("\n")
        header = lines[0] if lines else ""

        body_start = 1
        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1

        body_lines = []
        footer_lines = []
        in_footer = False

        for line in lines[body_start:]:
            if any(line.strip().startswith(prefix) for prefix in
                   ["BREAKING CHANGE:", "Refs:", "Closes:", "Fixes:"]):
                in_footer = True

            if in_footer:
                footer_lines.append(line)
            else:
                body_lines.append(line)

        body = "\n".join(body_lines).strip()
        footer = "\n".join(footer_lines).strip()

        return {
            "header": header,
            "body": body,
            "footer": footer,
            "full_message": message_text,
            "formatted": self._format_for_git(header, body, footer)
        }

    def _format_for_git(self, header: str, body: str, footer: str) -> str:
        """Format commit message for git commit."""
        parts = [header]

        if body:
            parts.append("")  # Blank line
            parts.append(body)

        if footer:
            parts.append("")  # Blank line
            parts.append(footer)

        return "\n".join(parts)

    def commit_with_message(self, message: str, amend: bool = False) -> bool:
        """
        Execute git commit with the generated message.

        Args:
            message: Commit message
            amend: Whether to amend previous commit

        Returns:
            True if successful
        """
        try:
            cmd = ["git", "commit"]
            if amend:
                cmd.append("--amend")
            cmd.extend(["-m", message])

            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git commit failed: {e}", file=sys.stderr)
            return False


def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(
        description="Generate conventional commit messages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from staged changes
  python commit_message_generator.py

  # From description
  python commit_message_generator.py --description "Added user login feature"

  # With context
  python commit_message_generator.py --context "Part of auth system refactor"

  # Specify type and scope
  python commit_message_generator.py \\
    --description "Fix memory leak in cache" \\
    --type fix --scope cache

  # Breaking change
  python commit_message_generator.py \\
    --description "Remove deprecated API endpoints" \\
    --breaking

  # With issue references
  python commit_message_generator.py \\
    --description "Add dark mode" \\
    --issues PROJ-123 PROJ-124

  # Auto-commit after generation
  python commit_message_generator.py --commit

  # Show available commit types
  python commit_message_generator.py --list-types
        """
    )

    parser.add_argument(
        "--description", "-d",
        help="Description of changes (instead of git diff)"
    )

    parser.add_argument(
        "--type", "-t",
        choices=list(COMMIT_TYPES.keys()),
        help="Commit type"
    )

    parser.add_argument(
        "--scope", "-s",
        help="Commit scope (e.g., auth, api, ui)"
    )

    parser.add_argument(
        "--context", "-c",
        help="Additional context for commit message"
    )

    parser.add_argument(
        "--breaking", "-b",
        action="store_true",
        help="Mark as breaking change"
    )

    parser.add_argument(
        "--issues", "-i",
        nargs="+",
        help="Issue/ticket references"
    )

    parser.add_argument(
        "--commit",
        action="store_true",
        help="Auto-commit after generating message"
    )

    parser.add_argument(
        "--amend",
        action="store_true",
        help="Amend previous commit"
    )

    parser.add_argument(
        "--list-types",
        action="store_true",
        help="List available commit types"
    )

    parser.add_argument(
        "--output", "-o",
        help="Save commit message to file"
    )

    args = parser.parse_args()

    # List types
    if args.list_types:
        print("\n📋 Available Commit Types:\n")
        for type_name, description in COMMIT_TYPES.items():
            print(f"  {type_name:12} {description}")
        print()
        return

    # Initialize generator
    try:
        generator = CommitMessageGenerator()
    except Exception as e:
        print(f"Error: Could not initialize. Make sure ANTHROPIC_API_KEY is set.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate commit message
    try:
        print("\n🔧 Generating commit message...\n")

        if args.description:
            result = generator.generate_from_description(
                description=args.description,
                commit_type=args.type,
                scope=args.scope,
                breaking_change=args.breaking,
                issue_refs=args.issues
            )
        else:
            result = generator.generate_from_diff(
                context=args.context,
                breaking_change=args.breaking,
                issue_refs=args.issues
            )

        # Display result
        print("=" * 70)
        print("📝 GENERATED COMMIT MESSAGE")
        print("=" * 70)
        print(result["formatted"])
        print("=" * 70)

        # Save if requested
        if args.output:
            with open(args.output, "w") as f:
                f.write(result["formatted"])
            print(f"\n💾 Saved to {args.output}")

        # Commit if requested
        if args.commit:
            confirm = input("\n🤔 Commit with this message? (y/n): ").strip().lower()
            if confirm == "y":
                if generator.commit_with_message(result["formatted"], amend=args.amend):
                    print("✅ Committed successfully!")
                else:
                    print("❌ Commit failed")
                    sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
