# Testing Requirements

## Minimum Test Coverage: 80%

Test Types (ALL required):
1. **Unit Tests** - Engine calculations, utility functions
2. **Integration Tests** - API endpoints via httpx AsyncClient
3. **Cross-Verification** - Known birth dates against reference saju sites

## Test-Driven Development

MANDATORY workflow:
1. Write test first (RED)
2. Run test - it should FAIL
3. Write minimal implementation (GREEN)
4. Run test - it should PASS
5. Refactor (IMPROVE)
6. Verify coverage (80%+)

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=term-missing

# Single module
pytest tests/test_engine/test_calculator.py -v

# Watch mode (with pytest-watch)
ptw tests/
```

## Engine Test Priority

The saju calculator is the foundation. These MUST be verified:
- Four pillars match known reference values
- Lunar-to-solar conversion is accurate
- Summer time correction works for 1948-1961
- Night zi (23:00) produces different results with different sect settings
- Element counts sum correctly (6 for 3-pillar, 8 for 4-pillar)
- Da Yun direction differs by gender + stem yin/yang

## Agent Support

- **tdd-guide** - Use PROACTIVELY for new features
- Run `pytest` after EVERY code change
