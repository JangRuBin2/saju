---
description: Fix build, import, or test errors with minimal changes. No refactoring.
---

Invoke the **build-error-resolver** agent.

1. Collect all errors:
```bash
python -c "from app.main import app"
pytest tests/ -v
```

2. Fix one error at a time with minimal diff
3. Run tests after each fix
4. DO NOT refactor or change architecture
5. Goal: get all tests passing again
