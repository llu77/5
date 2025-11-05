# Commit Message Formatting Rules

## Structure

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Header Rules

1. **Type** (required): One of feat, fix, docs, style, refactor, perf, test, chore
2. **Scope** (optional): Component/module affected
3. **Subject** (required):
   - Lowercase
   - Imperative mood ("add" not "added")
   - No period at end
   - Max 50 characters

## Body Rules

1. Wrap at 72 characters
2. Explain what and why (not how)
3. Use bullet points for multiple items
4. Separate from header with blank line

## Footer Rules

1. Reference issues: `Refs: #123, #456`
2. Close issues: `Closes: #123`
3. Breaking changes: `BREAKING CHANGE: description`

## Examples

Good:
```
feat(auth): add OAuth2 support

Implement OAuth2 authentication flow for third-party logins.
Support Google, GitHub, and Microsoft providers.

Refs: #245
```

Bad:
```
Added authentication.

I added OAuth2 because we needed it. Used some libraries.
```

## Tips

- Keep commits atomic (one logical change)
- Write in present tense
- Be specific but concise
- Reference docs/issues when relevant
