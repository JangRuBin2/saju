---
description: Enforce test-driven development. Write tests FIRST, then implement minimal code to pass. Verify 80%+ coverage.
---

Invoke the **tdd-guide** agent to enforce TDD methodology.

## TDD Cycle

1. **RED** - Write failing test
2. **GREEN** - Implement minimal code to pass
3. **REFACTOR** - Improve while keeping tests green
4. **VERIFY** - Check 80%+ coverage

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=term-missing
```

MANDATORY: Tests must be written BEFORE implementation. Never skip the RED phase.
