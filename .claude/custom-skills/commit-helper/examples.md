# Commit Message Examples

## Example 1: Feature Addition

**Input:** Added user authentication with JWT tokens

**Output:**
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware.
Use RS256 algorithm for signing tokens.
```

## Example 2: Bug Fix

**Input:** Fixed bug where dates displayed incorrectly in reports

**Output:**
```
fix(reports): correct date formatting in timezone conversion

Dates were displaying incorrectly due to timezone handling.
Use UTC timestamps consistently across report generation.
```

## Example 3: Multiple Changes

**Input:** Updated dependencies and refactored error handling

**Output:**
```
chore: update dependencies and refactor error handling

- Upgrade lodash to 4.17.21 for security patch
- Standardize error response format across endpoints
- Add error logging middleware
```

## Example 4: Breaking Change

**Input:** Removed deprecated API v1 endpoints

**Output:**
```
feat: remove deprecated API v1 endpoints

API v1 has been removed in favor of v2.
All clients must upgrade to v2 endpoints.

BREAKING CHANGE: v1 endpoints no longer available
Refs: MIGRATION-GUIDE.md
```

## Example 5: Performance Improvement

**Input:** Optimized database queries in user service

**Output:**
```
perf(users): optimize database queries with indexing

Add compound indexes on frequently queried fields.
Reduce query time from ~500ms to ~50ms for user lookups.
```

## More Examples

For domain-specific examples, see:
- [backend-examples.md](backend-examples.md)
- [frontend-examples.md](frontend-examples.md)
- [devops-examples.md](devops-examples.md)
