# Commit Message Best Practices

## General Guidelines

### 1. Atomic Commits
Each commit should represent one logical change.

**Good:**
```
fix(api): handle null values in user response
refactor(api): extract validation logic to middleware
```

**Bad:**
```
fix: various api fixes and refactoring
```

### 2. Clear Subject Lines
Make the purpose immediately clear.

**Good:**
```
feat(search): add fuzzy matching for product names
```

**Bad:**
```
update search
```

### 3. Detailed Body
Explain context, rationale, and impact.

**Good:**
```
perf(db): add indexes on frequently queried fields

Query performance was degrading with dataset growth.
Added compound indexes on (user_id, created_at) and (status, priority).
Reduces average query time from 450ms to 45ms.
```

**Bad:**
```
perf(db): faster queries
```

## Type Selection

### feat vs fix
- **feat**: New capability for users
- **fix**: Correcting incorrect behavior

### refactor vs chore
- **refactor**: Code structure changes (no behavior change)
- **chore**: Build, tools, dependencies

## Scope Guidelines

Use specific, consistent scopes:

**Good:** `auth`, `api`, `ui`, `db`, `tests`
**Avoid:** `stuff`, `misc`, `utils`

## Breaking Changes

Always document breaking changes:

```
feat!: remove legacy API v1

BREAKING CHANGE: API v1 endpoints removed
Migration guide: docs/migration-v1-to-v2.md
```

## Issue References

Link commits to issues:

```
fix(payments): handle timeout errors gracefully

Implement retry logic with exponential backoff.
Add timeout configuration to payment service.

Fixes: #789
Refs: #745, #623
```

## Multi-Language Projects

Include language/framework in scope:

```
feat(api/node): add rate limiting middleware
feat(web/react): add loading skeleton components
```

## Review Checklist

Before committing, verify:

- [ ] Type is correct
- [ ] Scope is specific
- [ ] Subject is clear and concise
- [ ] Body explains what and why
- [ ] Breaking changes documented
- [ ] Issues referenced
- [ ] One logical change per commit
