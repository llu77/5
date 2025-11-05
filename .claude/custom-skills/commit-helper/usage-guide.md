# Commit Helper Usage Guide

## Basic Usage

### From Staged Changes
```
Generate commit message from my staged git changes
```

The skill will:
1. Analyze your git diff
2. Identify the type of changes
3. Suggest appropriate commit message

### From Description
```
Create commit message: Added dark mode toggle to settings
```

## Commit Types

The skill uses conventional commit types:

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Formatting changes
- **refactor**: Code restructuring
- **perf**: Performance improvements
- **test**: Test additions/fixes
- **chore**: Build/tool changes

## Advanced Usage

For breaking changes, issue tracking, and complex scenarios, see [advanced-config.md](advanced-config.md).

## Examples

For detailed examples of generated commit messages, see [examples.md](examples.md).
