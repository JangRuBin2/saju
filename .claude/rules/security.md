# Security Guidelines

## Mandatory Security Checks

Before ANY commit:
- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] All user inputs validated via Pydantic
- [ ] Error messages don't leak sensitive data (stack traces, paths)
- [ ] .env file is gitignored
- [ ] No PII (birth dates) logged in plain text
- [ ] Rate limiting on public endpoints (when deployed)

## Secret Management

```python
# NEVER: Hardcoded secrets
api_key = "sk-ant-xxxxx"

# ALWAYS: Environment variables via config
from app.config import settings
api_key = settings.anthropic_api_key

if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not configured")
```

## Personal Data Protection

This service handles birth dates (personal information):
- Never log full birth date + gender combinations
- Do not persist user data unless explicitly required
- Cache keys must be hashed (SHA256), not raw birth data
- Consider privacy implications in error responses

## Security Response Protocol

If security issue found:
1. STOP immediately
2. Use **security-reviewer** agent
3. Fix CRITICAL issues before continuing
4. Rotate any exposed secrets
5. Review entire codebase for similar issues
