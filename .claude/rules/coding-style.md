# Coding Style

## Immutability (CRITICAL)

ALWAYS create new objects, NEVER mutate:

```python
# WRONG: Mutation
def update_counts(counts, key):
    counts[key] += 1  # MUTATION!
    return counts

# CORRECT: Immutability
def update_counts(counts, key):
    return {**counts, key: counts.get(key, 0) + 1}
```

Use frozen dataclasses for data models:

```python
@dataclass(frozen=True)
class PillarInfo:
    gan: str
    zhi: str
```

## File Organization

MANY SMALL FILES > FEW LARGE FILES:
- High cohesion, low coupling
- 200-400 lines typical, 800 max
- Extract utilities from large modules
- Organize by feature/domain, not by type

## Type Hints

ALWAYS use type hints on public functions:

```python
from __future__ import annotations

def calculate(year: int, month: int, day: int) -> SajuData:
    ...
```

## Error Handling

ALWAYS handle errors with specific exception types:

```python
try:
    result = some_operation()
    return result
except SpecificError as exc:
    logger.error("Operation failed: %s", exc)
    raise SajuError("User-friendly message") from exc
```

## Input Validation

ALWAYS validate via Pydantic models:

```python
class BirthInput(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
```

## Code Quality Checklist

Before marking work complete:
- [ ] Code is readable and well-named
- [ ] Functions are small (<50 lines)
- [ ] Files are focused (<800 lines)
- [ ] No deep nesting (>4 levels)
- [ ] Proper error handling
- [ ] No print() statements (use logging)
- [ ] No hardcoded values
- [ ] No mutation (immutable patterns used)
- [ ] Type hints on all public functions
