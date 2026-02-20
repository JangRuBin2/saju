---
description: Comprehensive security and quality review of uncommitted changes.
---

Invoke the **code-reviewer** agent for comprehensive review.

1. Get changed files: `git diff --name-only HEAD`

2. For each changed file, check:

**Security Issues (CRITICAL):**
- Hardcoded credentials, API keys
- Missing input validation
- PII leakage in logs/errors
- .env files in commits

**Code Quality (HIGH):**
- Functions >50 lines
- Files >800 lines
- Missing error handling
- print() statements
- Missing type hints
- Mutation patterns

**Python/FastAPI (HIGH):**
- Blocking sync calls in async endpoints
- Missing Pydantic validation
- Incorrect dependency injection

**Best Practices (MEDIUM):**
- Frozen dataclasses for value objects
- Consistent error hierarchy
- Tests for new code

3. Generate report with severity, location, fix suggestion
4. Block commit if CRITICAL or HIGH issues found
