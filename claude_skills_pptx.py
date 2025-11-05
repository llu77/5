#!/usr/bin/env python3
"""
Claude Skills - PowerPoint Generator

Use Claude's pptx skill to create PowerPoint presentations programmatically.
Handles file downloads and provides easy-to-use interface.
"""

import os
import sys
import argparse
import re
from pathlib import Path
from anthropic import Anthropic


def extract_file_ids(response) -> list:
    """Extract file IDs from Claude response."""
    file_ids = []

    for block in response.content:
        if block.type == "bash_code_execution_tool_result":
            try:
                if hasattr(block, "content") and hasattr(block.content, "content"):
                    for item in block.content.content:
                        if hasattr(item, "file_id"):
                            file_ids.append(item.file_id)
            except Exception:
                continue

    return list(set(file_ids))


class PowerPointGenerator:
    """Generate PowerPoint presentations using Claude's pptx skill."""

    def __init__(self, api_key: str = None):
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-5"

    def create_presentation(
        self,
        topic: str,
        slides: int = None,
        style: str = "professional",
        additional_context: str = ""
    ) -> dict:
        """
        Create a PowerPoint presentation.

        Args:
            topic: Presentation topic/title
            slides: Number of slides (optional, Claude decides if None)
            style: Presentation style (professional, creative, minimal, corporate)
            additional_context: Additional requirements or context

        Returns:
            Dictionary with response and file information
        """
        # Build prompt
        prompt_parts = [f"Create a PowerPoint presentation about: {topic}"]

        if slides:
            prompt_parts.append(f"\nNumber of slides: {slides}")

        if style:
            style_descriptions = {
                "professional": "Use a professional, business-appropriate style with clean design",
                "creative": "Use creative, engaging visuals with bold colors",
                "minimal": "Use minimal, clean design with lots of white space",
                "corporate": "Use corporate, formal style suitable for executive presentations",
                "educational": "Use educational style with clear explanations and examples"
            }
            if style in style_descriptions:
                prompt_parts.append(f"\nStyle: {style_descriptions[style]}")

        if additional_context:
            prompt_parts.append(f"\nAdditional requirements:\n{additional_context}")

        prompt = "\n".join(prompt_parts)

        print(f"\n🎯 Creating presentation: {topic}")
        if style:
            print(f"📐 Style: {style}")
        if slides:
            print(f"📊 Target slides: {slides}")
        print()

        # Make API call
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=4096,
            betas=["code-execution-2025-08-25", "skills-2025-10-02"],
            container={
                "skills": [
                    {
                        "type": "anthropic",
                        "skill_id": "pptx",
                        "version": "latest"
                    }
                ]
            },
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "type": "code_execution_20250825",
                "name": "code_execution"
            }]
        )

        # Extract text responses
        text_responses = []
        for block in response.content:
            if block.type == "text":
                text_responses.append(block.text)

        # Extract file IDs
        file_ids = extract_file_ids(response)

        return {
            "response": response,
            "file_ids": file_ids,
            "text": "\n".join(text_responses),
            "success": len(file_ids) > 0
        }

    def download_file(self, file_id: str, output_path: str) -> bool:
        """
        Download file from Claude.

        Args:
            file_id: File ID from response
            output_path: Local path to save file

        Returns:
            True if successful
        """
        try:
            # Create output directory
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Download file
            print(f"⬇️  Downloading file...")
            file_content = self.client.beta.files.download(file_id=file_id)

            # Save to disk
            with open(output_path, "wb") as f:
                f.write(file_content.read())

            file_size = os.path.getsize(output_path)
            print(f"✅ Saved to: {output_path} ({file_size / 1024:.1f} KB)")
            return True

        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False

    def get_file_info(self, file_id: str) -> dict:
        """Get metadata about a file."""
        try:
            info = self.client.beta.files.retrieve_metadata(file_id=file_id)
            return {
                "filename": info.filename,
                "size": info.size_bytes,
                "mime_type": info.mime_type,
                "created_at": info.created_at
            }
        except Exception as e:
            print(f"⚠️  Could not retrieve file info: {e}")
            return {}


def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(
        description="Generate PowerPoint presentations using Claude's pptx skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic presentation
  python claude_skills_pptx.py "Introduction to Machine Learning"

  # With specific number of slides
  python claude_skills_pptx.py "Quarterly Business Review" --slides 10

  # With style
  python claude_skills_pptx.py "Team Building Workshop" --style creative

  # With additional context
  python claude_skills_pptx.py "Product Launch Plan" \\
    --context "Include market analysis, go-to-market strategy, and timeline"

  # Custom output path
  python claude_skills_pptx.py "Sales Training" \\
    --output presentations/sales_training.pptx

  # Corporate style for executives
  python claude_skills_pptx.py "Annual Report 2024" \\
    --style corporate --slides 15
        """
    )

    parser.add_argument(
        "topic",
        help="Presentation topic or title"
    )

    parser.add_argument(
        "--slides", "-s",
        type=int,
        help="Number of slides (optional, Claude decides if not specified)"
    )

    parser.add_argument(
        "--style",
        choices=["professional", "creative", "minimal", "corporate", "educational"],
        default="professional",
        help="Presentation style (default: professional)"
    )

    parser.add_argument(
        "--context", "-c",
        help="Additional context or requirements"
    )

    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: topic_name.pptx)"
    )

    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Don't download the file, just show file ID"
    )

    args = parser.parse_args()

    # Initialize generator
    try:
        generator = PowerPointGenerator()
    except Exception as e:
        print(f"Error: Could not initialize. Make sure ANTHROPIC_API_KEY is set.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)

    # Create presentation
    try:
        result = generator.create_presentation(
            topic=args.topic,
            slides=args.slides,
            style=args.style,
            additional_context=args.context or ""
        )

        # Show Claude's response
        if result["text"]:
            print("\n" + "="*70)
            print("📝 CLAUDE'S RESPONSE")
            print("="*70)
            print(result["text"])
            print("="*70 + "\n")

        # Handle file download
        if result["success"]:
            file_id = result["file_ids"][0]
            print(f"📁 File ID: {file_id}")

            # Get file info
            file_info = generator.get_file_info(file_id)
            if file_info:
                print(f"📄 Filename: {file_info.get('filename', 'N/A')}")
                print(f"📦 Size: {file_info.get('size', 0) / 1024:.1f} KB")

            if not args.no_download:
                # Determine output path
                if args.output:
                    output_path = args.output
                else:
                    # Generate filename from topic
                    safe_filename = re.sub(r'[^\w\s-]', '', args.topic.lower())
                    safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
                    output_path = f"{safe_filename}.pptx"

                # Download
                print()
                if generator.download_file(file_id, output_path):
                    print(f"\n🎉 Presentation created successfully!")
                    print(f"📂 Open: {output_path}")
                else:
                    print("\n⚠️  File was created but download failed")
                    print(f"💡 Try downloading manually with file ID: {file_id}")
        else:
            print("\n❌ No presentation file was generated")
            print("💡 Try rephrasing your request or check the response above")

    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
