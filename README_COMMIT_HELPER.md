# Commit Message Generator & Nested Documentation Pattern

Tools and examples for generating conventional commit messages and organizing nested documentation.

## 📚 What's Included

### 1. **Commit Message Generator** (`commit_message_generator.py`)
Smart CLI tool that generates conventional commit messages from git diffs or descriptions.

### 2. **Nested Documentation Example** (`.claude/custom-skills/commit-helper/`)
Complete example of nested documentation structure for Claude Code skills.

---

## 🚀 Commit Message Generator

### Features

- ✅ Generates from git diff or description
- ✅ Follows Conventional Commits specification
- ✅ Supports all commit types (feat, fix, docs, etc.)
- ✅ Handles breaking changes and issue references
- ✅ Can auto-commit after generation
- ✅ Preserves commit message formatting standards

### Installation

```bash
chmod +x commit_message_generator.py
```

### Usage

**From Staged Changes:**
```bash
# Generate from git diff
python commit_message_generator.py

# With context
python commit_message_generator.py --context "Part of auth refactor"

# Auto-commit
python commit_message_generator.py --commit
```

**From Description:**
```bash
# Basic
python commit_message_generator.py --description "Added user login feature"

# With type and scope
python commit_message_generator.py \
  --description "Fix memory leak in cache" \
  --type fix --scope cache

# Breaking change
python commit_message_generator.py \
  --description "Remove deprecated API endpoints" \
  --breaking

# With issue references
python commit_message_generator.py \
  --description "Add dark mode" \
  --issues PROJ-123 PROJ-124
```

**Other Options:**
```bash
# List available commit types
python commit_message_generator.py --list-types

# Save to file
python commit_message_generator.py --output commit-msg.txt

# Amend previous commit
python commit_message_generator.py --amend --commit
```

### Examples

#### Example 1: Feature Addition

**Input:**
```bash
python commit_message_generator.py \
  --description "Added user authentication with JWT tokens"
```

**Output:**
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware.
Use RS256 algorithm for signing tokens.
```

#### Example 2: Bug Fix

**Input:**
```bash
python commit_message_generator.py \
  --description "Fixed bug where dates displayed incorrectly in reports"
```

**Output:**
```
fix(reports): correct date formatting in timezone conversion

Dates were displaying incorrectly due to timezone handling bug.
Use UTC timestamps consistently across report generation.
```

#### Example 3: Multiple Changes

**Input:**
```bash
python commit_message_generator.py \
  --description "Updated dependencies and refactored error handling"
```

**Output:**
```
chore: update dependencies and refactor error handling

- Upgrade lodash to 4.17.21 for security patch
- Standardize error response format across endpoints
- Add error logging middleware
```

#### Example 4: Breaking Change

**Input:**
```bash
python commit_message_generator.py \
  --description "Remove deprecated API endpoints" \
  --breaking \
  --issues API-456
```

**Output:**
```
feat!: remove deprecated API v1 endpoints

API v1 has been removed in favor of v2.
All clients must upgrade to v2 endpoints.

BREAKING CHANGE: v1 endpoints no longer available
Refs: API-456
```

### Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | feat(auth): add OAuth2 support |
| `fix` | Bug fix | fix(api): handle null values |
| `docs` | Documentation | docs: update API guide |
| `style` | Formatting | style: apply prettier formatting |
| `refactor` | Code restructuring | refactor(db): extract query builder |
| `perf` | Performance improvement | perf(api): cache user queries |
| `test` | Test additions/fixes | test(auth): add login tests |
| `chore` | Build/tool changes | chore: upgrade webpack to 5.x |
| `ci` | CI changes | ci: add GitHub Actions workflow |
| `build` | Build system changes | build: configure rollup |
| `revert` | Revert previous commit | revert: feat(api): add rate limiting |

### Conventional Commits Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Rules:**
- **Type**: Required, one of the types above
- **Scope**: Optional, component/module affected
- **Subject**:
  - Lowercase, imperative mood
  - No period at end
  - Max 50 characters
- **Body**:
  - Wrap at 72 characters
  - Explain what and why (not how)
  - Separate from header with blank line
- **Footer**:
  - Issue references: `Refs: #123`
  - Breaking changes: `BREAKING CHANGE: description`

---

## 📖 Nested Documentation Pattern

### Structure

The `.claude/custom-skills/commit-helper/` directory demonstrates how to organize nested documentation:

```
commit-helper/
├── SKILL.md                  # Main entry point
├── usage-guide.md            # Basic usage
├── advanced-config.md        # Advanced features
├── examples.md               # Real examples
├── formatting-rules.md       # Formatting details
└── best-practices.md         # Best practices
```

### Pattern Benefits

**1. Progressive Disclosure**
- Main file is simple and scannable
- Details are in linked files
- Users can dive deeper as needed

**2. Modularity**
- Each file has single purpose
- Easy to update specific sections
- Better maintainability

**3. Discoverability**
- Clear navigation between files
- Related content grouped together
- Breadcrumb-style references

### How to Use This Pattern

**Step 1: Create Main Entry Point (SKILL.md)**
```markdown
---
name: your-skill
description: Brief description
---

# Skill Name

Quick overview and basic usage.

For detailed usage, see [usage-guide.md](usage-guide.md).
For advanced configuration, see [advanced-config.md](advanced-config.md).
```

**Step 2: Create Supporting Documents**
```markdown
# Usage Guide

Basic usage instructions...

For advanced features, see [advanced-config.md](advanced-config.md).
```

**Step 3: Cross-Reference**
```markdown
# Advanced Configuration

Advanced features...

For basic usage, return to [usage-guide.md](usage-guide.md).
For examples, see [examples.md](examples.md).
```

### Example: commit-helper Skill

**Main File (SKILL.md):**
```markdown
# Commit Message Helper

Generate conventional commit messages.

See [usage-guide.md](usage-guide.md) for examples.
```

**Supporting Files:**
- `usage-guide.md` - How to use the skill
- `advanced-config.md` - Advanced features (links to other docs)
- `examples.md` - Real-world examples
- `formatting-rules.md` - Detailed formatting rules
- `best-practices.md` - Guidelines and tips

**Benefits:**
- Main file stays concise
- Users find what they need quickly
- Easy to update individual sections
- Clear documentation hierarchy

---

## 🔧 Integration with Git Workflow

### Daily Workflow

```bash
# 1. Make changes
git add .

# 2. Generate commit message
python commit_message_generator.py

# 3. Review and commit (or use --commit flag)
python commit_message_generator.py --commit
```

### Pre-commit Hook

Create `.git/hooks/prepare-commit-msg`:

```bash
#!/bin/bash
# Auto-generate commit message if empty

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2

# Only run for new commits (not amend, merge, etc.)
if [ -z "$COMMIT_SOURCE" ]; then
  # Check if message is empty
  if [ ! -s "$COMMIT_MSG_FILE" ]; then
    python commit_message_generator.py --output "$COMMIT_MSG_FILE"
  fi
fi
```

### Git Alias

Add to `.gitconfig`:

```ini
[alias]
  cm = !python /path/to/commit_message_generator.py --commit
  cmsg = !python /path/to/commit_message_generator.py
```

Usage:
```bash
git cm              # Generate and commit
git cmsg            # Generate message only
```

---

## 💡 Use Cases

### Use Case 1: Consistent Team Commits

**Problem:** Team members write inconsistent commit messages

**Solution:**
```bash
# Everyone uses the generator
python commit_message_generator.py --commit

# Ensures:
# - Consistent format
# - Proper type classification
# - Meaningful descriptions
```

### Use Case 2: Quick Fixes

**Problem:** Need to commit quickly but maintain quality

**Solution:**
```bash
# Quick one-liner
python commit_message_generator.py \
  --description "Fix null pointer in payment processor" \
  --type fix --scope payments --commit
```

### Use Case 3: Complex Multi-Component Changes

**Problem:** Large refactor affecting multiple areas

**Solution:**
```bash
# Detailed description with context
python commit_message_generator.py \
  --description "Refactor auth system and update dependencies" \
  --context "Part of security audit recommendations" \
  --issues SEC-789 --commit
```

### Use Case 4: Breaking Changes

**Problem:** Need to clearly communicate breaking changes

**Solution:**
```bash
python commit_message_generator.py \
  --description "Remove v1 API support" \
  --breaking \
  --issues MIGRATION-123 \
  --commit
```

---

## 🎨 Customization

### Custom Commit Types

Modify `COMMIT_TYPES` in the script:

```python
COMMIT_TYPES = {
    "feat": "A new feature",
    "fix": "A bug fix",
    # Add custom types
    "security": "Security patch",
    "hotfix": "Critical production fix",
}
```

### Custom Prompt Template

Modify `COMMIT_MESSAGE_PROMPT` to adjust generation style:

```python
COMMIT_MESSAGE_PROMPT = """
Your custom prompt here...
Include specific guidelines for your team/project.
"""
```

### Language-Specific Scopes

For multi-language projects:

```bash
python commit_message_generator.py \
  --description "Add user service tests" \
  --scope "api/node" \
  --type test
```

---

## 📊 Best Practices

### DO:
- ✅ Use descriptive scopes
- ✅ Keep subject lines concise (<50 chars)
- ✅ Explain what and why in body
- ✅ Reference issues
- ✅ Mark breaking changes clearly
- ✅ Use imperative mood ("add" not "added")

### DON'T:
- ❌ Use vague descriptions ("fix stuff", "update code")
- ❌ Combine unrelated changes
- ❌ Skip the body for complex changes
- ❌ Forget to reference issues
- ❌ Use past tense

### Commit Frequency

- **Too frequent**: Every small change (hard to review)
- **Too rare**: Giant commits (hard to understand)
- **Just right**: One logical change per commit

---

## 🐛 Troubleshooting

### "No changes to commit"

```bash
# Make sure you have staged changes
git add .

# Or specify unstaged changes
python commit_message_generator.py  # Uses --cached by default
```

### "API key not found"

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### "Git diff too large"

The tool limits diff size to 8000 characters. For large changes:

```bash
# Use description instead
python commit_message_generator.py \
  --description "Your summary of changes"
```

### "Generated message needs tweaking"

```bash
# Save and edit manually
python commit_message_generator.py --output msg.txt
nano msg.txt
git commit -F msg.txt
```

---

## 📚 Additional Resources

**Conventional Commits:**
- [Specification](https://www.conventionalcommits.org/)
- [Angular Convention](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit)

**Git Best Practices:**
- [Commit Message Guide](https://chris.beams.io/posts/git-commit/)
- [Semantic Versioning](https://semver.org/)

**This Repository:**
- `README_ADVANCED_PATTERNS.md` - Metaprompt & orchestrator patterns
- `README_THINKING_TOOLS.md` - Extended thinking tools
- `README_COMMIT_HELPER.md` - This file

---

## 🎯 Next Steps

1. **Try it out:**
   ```bash
   python commit_message_generator.py --interactive
   ```

2. **Set up git alias:**
   ```bash
   git config --global alias.cm '!python /path/to/commit_message_generator.py --commit'
   ```

3. **Create team standards:**
   - Document custom scopes
   - Define breaking change criteria
   - Set up pre-commit hooks

4. **Build nested docs:**
   - Use `.claude/custom-skills/` pattern
   - Create progressive documentation
   - Cross-reference related content

---

**Happy committing! 📝✨**
