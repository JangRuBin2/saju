# Common Patterns

## API Response Format

All responses use Pydantic models:

```python
class SajuCalculateResponse(BaseModel):
    solar_date: str
    lunar_date: str
    year_pillar: PillarResponse
    month_pillar: PillarResponse
    day_pillar: PillarResponse
    time_pillar: PillarResponse | None
    day_master: str
    element_counts: dict[str, int]
    da_yun_list: list[DaYunResponse]
```

## Error Response Format

```python
class ErrorResponse(BaseModel):
    error: str      # Error class name
    message: str    # User-friendly message
```

## Service Layer Pattern

Services orchestrate between engine (calculation) and LLM (interpretation):

```python
class SajuService:
    def __init__(self, calculator, llm_client, cache):
        self._calculator = calculator
        self._llm = llm_client
        self._cache = cache

    def calculate(self, birth: BirthInput) -> SajuData:
        return self._calculator.calculate(...)

    async def reading(self, birth: BirthInput) -> tuple[SajuData, str]:
        saju = self.calculate(birth)
        interpretation = await self._llm.generate(prompt)
        return saju, interpretation
```

## Cache Key Pattern

Cache keys are hashed for privacy:

```python
CacheService.make_key("reading", year=1990, month=5, day=15, ...)
# -> "saju:reading:a1b2c3d4e5f6g7h8"
```

## Dependency Injection Pattern

Singletons initialized at app startup, injected via FastAPI Depends:

```python
def get_saju_service() -> SajuService:
    assert _saju_service is not None
    return _saju_service
```
