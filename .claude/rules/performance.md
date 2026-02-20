# Performance Optimization

## Model Selection Strategy

**Haiku** (lightweight, cheap):
- Quick lookups, simple transformations
- Worker agents in multi-agent workflows

**Sonnet** (best coding model):
- Main development work
- LLM interpretation in production (default)
- Orchestrating multi-agent workflows

**Opus** (deepest reasoning):
- Complex architectural decisions
- Planning and code review agents
- Deep debugging

## Context Window Management

Avoid last 20% of context window for:
- Large-scale refactoring
- Feature implementation spanning multiple files

Lower context sensitivity tasks:
- Single-file edits
- Independent utility creation
- Simple bug fixes

## Saju-Specific Performance

- Engine calculation is synchronous and fast (~1ms)
- LLM interpretation is async and slow (3-10s)
- Always return calculation immediately, stream interpretation
- Cache calculation results for 24h (deterministic)
- Cache interpretation results for 1h
- Redis is optional - graceful degradation when unavailable

## Prompt Caching

Use `cache_control: {"type": "ephemeral"}` on system prompts:
- System prompt is ~1000 tokens, sent every request
- Caching reduces cost by ~90% for repeat calls
